#!/usr/bin/env python3
"""
文献检索 + 筛选评分 + 选定集合（ProjGrantGen 自带，零外部依赖）。

自带多库检索 + 筛选 + 选定，合并为单一脚本，
使用标准库 urllib 直连以下**免密钥**学术数据库：
  - PubMed / Europe PMC  （生物医学首选）
  - OpenAlex             （全学科，254M+ 文献）
  - Crossref             （全学科 DOI 元数据）
  - Semantic Scholar     （引文计数，限流）

产出：
  <output-dir>/candidates/literature_search.json   原始候选
  <output-dir>/selected_papers.json                选定集合（含 ref_no）

用法：
  # A. 自动检索（推荐优先用 agent 的 WebSearch；本脚本用于批量/自动链路）
  python literature_search.py --queries "<领域A 核心概念英文>" \
        "<领域A/领域B 关键实体英文>" --domain biomedical --years 2021-2026 \
        --output-dir "./<project_slug>" --top-n 50

  # B. 降级：agent 用 WebSearch 手工整理后，喂入 JSON 直接规范化并赋 ref_no
  python literature_search.py --from-json "./<project_slug>/candidates/manual.json" \
        --output-dir "./<project_slug>" --top-n 50

  # C. 先自动/手工得到候选，再由 agent 圈定索引后导出最终集合
  python literature_search.py --from-json "./<project_slug>/candidates/literature_search.json" \
        --output-dir "./<project_slug>" --keep-indices 3 5 12 14 ...

说明：自动评分仅为起点（关键词相关度 + 时效 + 引文）；最终筛选请以
standards/scoring-system.md 的六维人工评分表为准。
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

USER_AGENT = "ProjGrantGen/1.0 (grant proposal literature helper)"

# ---------------------------------------------------------------------------
# 领域 → 数据库映射（任何领域一律不检索预印本服务器；
# arXiv/bioRxiv/medRxiv/Research Square/SSRN 等一律不进候选，见 scoring-system.md）
# ---------------------------------------------------------------------------
DOMAIN_DATABASES = {
    "biomedical": ["pubmed", "europe_pmc", "semantic_scholar", "crossref", "openalex"],
    "cs_ai": ["openalex", "semantic_scholar", "crossref", "dblp"],
    "cross": ["pubmed", "europe_pmc", "semantic_scholar", "crossref", "openalex", "dblp"],
    "general": ["openalex", "semantic_scholar", "crossref"],
    "engineering": ["openalex", "crossref", "semantic_scholar", "pubmed"],
}

BIOMEDICAL_KEYWORDS = [
    "cancer", "tumor", "tumour", "disease", "clinical", "patient", "patients",
    "cell", "protein", "gene", "genome", "genomic", "transcriptom", "proteom",
    "metabolom", "pathway", "signaling", "therap", "drug", "diagnos", "prognos",
    "biomarker", "infection", "immun", "mutation", "kinase", "receptor", "enzyme",
    "antibod", "virus", "bacter", "inflammat", "apoptos", "differentiation",
    "stem cell", "ribosome", "ubiquitin",
]


# ---------------------------------------------------------------------------
# HTTP 工具
# ---------------------------------------------------------------------------
def _http_get(url: str, params: dict | None = None, headers: dict | None = None,
              timeout: int = 30) -> bytes:
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=headers or {"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _http_get_json(url: str, params: dict | None = None, headers: dict | None = None,
                   timeout: int = 30) -> dict:
    return json.loads(_http_get(url, params, headers, timeout).decode("utf-8"))


# ---------------------------------------------------------------------------
# PubMed
# ---------------------------------------------------------------------------
def search_pubmed(query: str, max_results: int = 60, years: str = "") -> list[str]:
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    full_query = query
    if years and "-" in years:
        full_query = f"({query}) AND {years.replace('-', ':')}[dp]"
    elif years:
        full_query = f"({query}) AND {years}[dp]"
    params = {"db": "pubmed", "term": full_query, "retmax": max_results,
              "retmode": "json", "sort": "relevance"}
    try:
        time.sleep(0.34)
        data = _http_get_json(f"{base}esearch.fcgi", params)
        return data.get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        print(f"  PubMed search error: {e}")
        return []


def fetch_pubmed_details(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml", "rettype": "abstract"}
    try:
        time.sleep(0.34)
        xml = _http_get(f"{base}efetch.fcgi", params).decode("utf-8")
        return _parse_pubmed_xml(xml)
    except Exception as e:
        print(f"  PubMed fetch error: {e}")
        return []


def _parse_pubmed_xml(xml: str) -> list[dict]:
    root = ET.fromstring(xml)
    out = []
    for art in root.findall(".//PubmedArticle"):
        d = {"source": "PubMed"}
        d["pmid"] = _txt(art, ".//PMID")
        d["title"] = _txt_iter(art, ".//ArticleTitle")
        ab = art.findall(".//AbstractText")
        d["abstract"] = " ".join("".join(ae.itertext()) for ae in ab) if ab else ""
        alist = []
        for a in art.findall(".//Author")[:10]:
            last = a.findtext("LastName", "")
            fore = a.findtext("ForeName", "")
            if last:
                alist.append(f"{last} {fore[0]}." if fore else last)
        d["authors"] = ", ".join(alist) if alist else "Unknown"
        d["journal"] = art.findtext(".//Journal/ISOAbbreviation", "")
        d["year"] = art.findtext(".//PubDate/Year", "") or (art.findtext(".//PubDate/MedlineDate", "") or "")[:4]
        d["volume"] = art.findtext(".//Volume", "")
        d["issue"] = art.findtext(".//Issue", "")
        d["pages"] = art.findtext(".//Pagination/MedlinePgn", "")
        doi_e = art.find(".//ELocationID[@EIdType='doi']")
        d["doi"] = doi_e.text if doi_e is not None else ""
        d["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{d['pmid']}/" if d["pmid"] else ""
        d["key"] = d["doi"] or d["pmid"]
        d["cited_by"] = 0
        d["has_fulltext"] = bool(art.find(".//ArticleId[@IdType='pmc']") is not None)
        out.append(d)
    return out


def _txt(elem, xpath: str) -> str:
    e = elem.find(xpath)
    return e.text if e is not None else ""


def _txt_iter(elem, xpath: str) -> str:
    e = elem.find(xpath)
    return "".join(e.itertext()) if e is not None else ""


# ---------------------------------------------------------------------------
# Europe PMC
# ---------------------------------------------------------------------------
def search_europe_pmc(query: str, max_results: int = 60, years: str = "") -> list[dict]:
    base = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {"query": query, "resultType": "core",
              "pageSize": min(max_results, 100), "format": "json", "sort": "CITED desc"}
    if years and "-" in years:
        params["query"] = f"({query}) AND (FIRST_PDATE:[{years[:4]}-01-01 TO {years[5:]}-12-31])"
    try:
        data = _http_get_json(base, params)
        return _parse_europe_pmc(data.get("resultList", {}).get("result", []))
    except Exception as e:
        print(f"  Europe PMC search error: {e}")
        return []


def _parse_europe_pmc(results: list) -> list[dict]:
    out = []
    for p in results:
        d = {"source": "Europe PMC"}
        d["title"] = p.get("title", "") or ""
        d["abstract"] = p.get("abstractText", "") or ""
        d["doi"] = p.get("doi", "") or ""
        d["pmid"] = p.get("pmid", "") or ""
        d["year"] = p.get("pubYear", "") or ""
        author_str = p.get("authorString", "") or ""
        d["authors"] = ", ".join(author_str.split(", ")[:10]) if author_str else "Unknown"
        d["journal"] = p.get("journalTitle", "") or ""
        d["url"] = f"https://doi.org/{d['doi']}" if d["doi"] else ""
        d["key"] = d["doi"] or d["pmid"] or d["title"]
        d["cited_by"] = p.get("citedByCount", 0) or 0
        d["has_fulltext"] = bool(p.get("pmcid") or p.get("isOpenAccess", "") == "Y")
        out.append(d)
    return out


# ---------------------------------------------------------------------------
# OpenAlex
# ---------------------------------------------------------------------------
def search_openalex(query: str, max_results: int = 60, years: str = "") -> list[dict]:
    base = "https://api.openalex.org/works"
    params = {"search": query, "per_page": min(max_results, 200),
              "sort": "cited_by_count:desc",
              "select": "id,doi,title,authorships,publication_date,primary_location,"
                        "abstract_inverted_index,cited_by_count,open_access"}
    if years and "-" in years:
        params["filter"] = (f"from_publication_date:{years[:4]}-01-01,"
                            f"to_publication_date:{years[5:]}-12-31")
    try:
        time.sleep(0.11)
        data = _http_get_json(base, params, {"User-Agent": USER_AGENT})
        return _parse_openalex(data.get("results", []))
    except Exception as e:
        print(f"  OpenAlex search error: {e}")
        return []


def _parse_openalex(results: list) -> list[dict]:
    out = []
    for p in results:
        d = {"source": "OpenAlex"}
        d["title"] = p.get("title", "") or ""
        inv = p.get("abstract_inverted_index") or {}
        if inv:
            wp = []
            for w, pos in inv.items():
                for po in pos:
                    wp.append((po, w))
            wp.sort()
            d["abstract"] = " ".join(w for _, w in wp)
        else:
            d["abstract"] = ""
        d["doi"] = (p.get("doi", "") or "").replace("https://doi.org/", "")
        d["pmid"] = ""
        d["year"] = (p.get("publication_date", "") or "")[:4]
        alist = []
        for a in (p.get("authorships") or [])[:10]:
            name = (a.get("author") or {}).get("display_name", "")
            if name:
                alist.append(name)
        d["authors"] = ", ".join(alist) if alist else "Unknown"
        src = (p.get("primary_location") or {}).get("source") or {}
        d["journal"] = src.get("display_name", "") or ""
        d["url"] = f"https://doi.org/{d['doi']}" if d["doi"] else ""
        d["key"] = d["doi"] or d["title"]
        d["cited_by"] = p.get("cited_by_count", 0) or 0
        d["has_fulltext"] = bool((p.get("open_access") or {}).get("is_oa", False))
        out.append(d)
    return out


# ---------------------------------------------------------------------------
# Crossref
# ---------------------------------------------------------------------------
def search_crossref(query: str, max_results: int = 60, years: str = "") -> list[dict]:
    base = "https://api.crossref.org/works"
    params = {"query": query, "rows": min(max_results, 100), "sort": "relevance"}
    if years:
        params["filter"] = f"from-pub-date:{years[:4]},until-pub-date:{years[5:]}"
    try:
        data = _http_get_json(base, params, {"User-Agent": USER_AGENT})
        return _parse_crossref(data.get("message", {}).get("items", []))
    except Exception as e:
        print(f"  Crossref search error: {e}")
        return []


def _parse_crossref(items: list) -> list[dict]:
    out = []
    for p in items:
        d = {"source": "Crossref"}
        d["title"] = (p.get("title", [""])[0] if p.get("title") else "")
        d["abstract"] = p.get("abstract", "") or ""
        d["doi"] = p.get("DOI", "")
        d["pmid"] = ""
        for id_ in p.get("alternative-id", []):
            if id_.isdigit():
                d["pmid"] = id_
        yr = ""
        for k in ("published-print", "published-online", "created"):
            v = p.get(k)
            if v:
                yr = str(v.get("date-parts", [[""]])[0][0])
                break
        d["year"] = yr
        d["authors"] = ", ".join(
            f"{a.get('family','')} {a.get('given','')[:1]}." for a in p.get("author", [])[:10]
        ) or "Unknown"
        d["journal"] = (p.get("container-title", [""])[0] if p.get("container-title") else p.get("publisher", ""))
        d["url"] = f"https://doi.org/{d['doi']}" if d["doi"] else ""
        d["key"] = d["doi"]
        d["cited_by"] = p.get("is-referenced-by-count", 0) or 0
        d["has_fulltext"] = False
        out.append(d)
    return out


# ---------------------------------------------------------------------------
# Semantic Scholar
# ---------------------------------------------------------------------------
def search_semantic_scholar(query: str, max_results: int = 50, years: str = "") -> list[dict]:
    base = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": query, "limit": min(max_results, 100),
              "fields": "title,externalIds,authors,year,journal,abstract,url,citationCount"}
    if years and "-" in years:
        y = years.split("-")
        if len(y) == 2:
            params["year"] = f"{y[0]}-{y[1]}"
    try:
        time.sleep(3.0)
        data = _http_get_json(base, params)
        return _parse_s2(data.get("data", []))
    except Exception as e:
        print(f"  Semantic Scholar search error: {e}")
        return []


def _parse_s2(data: list) -> list[dict]:
    out = []
    for p in data:
        d = {"source": "Semantic Scholar"}
        d["title"] = p.get("title", "") or ""
        d["abstract"] = p.get("abstract", "") or ""
        ext = p.get("externalIds", {}) or {}
        d["doi"] = ext.get("DOI", "")
        d["pmid"] = ext.get("PubMed", "")
        d["year"] = str(p.get("year") or "")
        d["authors"] = ", ".join(a.get("name", "") for a in p.get("authors", [])[:10]) or "Unknown"
        j = p.get("journal")
        d["journal"] = (j.get("name", "") if isinstance(j, dict) else str(j)) if j else ""
        d["url"] = p.get("url", "")
        d["key"] = d["doi"] or d["pmid"] or d["title"]
        d["cited_by"] = p.get("citationCount", 0) or 0
        d["has_fulltext"] = False
        out.append(d)
    return out


# ---------------------------------------------------------------------------
# DBLP（CS/AI）
# ---------------------------------------------------------------------------
def search_dblp(query: str, max_results: int = 50) -> list[dict]:
    base = "https://dblp.org/search/publ/api"
    params = {"q": query, "h": min(max_results, 100), "format": "json"}
    try:
        data = _http_get_json(base, params)
        hits = data.get("result", {}).get("hits", {}).get("hit", [])
        out = []
        for hit in hits:
            info = hit.get("info", {})
            d = {"source": "DBLP"}
            d["title"] = info.get("title", "") or ""
            d["abstract"] = ""
            d["doi"] = info.get("doi", "") or ""
            d["pmid"] = ""
            d["year"] = str(info.get("year", "") or "")
            authors = info.get("authors", {}).get("author", [])
            if isinstance(authors, (str, dict)):
                authors = [authors]
            d["authors"] = ", ".join(
                a.get("text", "") if isinstance(a, dict) else str(a) for a in authors[:10]
            ) or "Unknown"
            d["journal"] = info.get("venue", "") or ""
            d["url"] = info.get("url", "") or ""
            d["key"] = d["doi"] or d["title"]
            d["cited_by"] = 0
            d["has_fulltext"] = bool(d["doi"])
            out.append(d)
        return out
    except Exception as e:
        print(f"  DBLP search error: {e}")
        return []


# ---------------------------------------------------------------------------
# 去重
# ---------------------------------------------------------------------------
def _norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", title.lower().strip())[:60]


def deduplicate(articles: list[dict]) -> list[dict]:
    seen_keys, seen_titles, result = set(), set(), []
    for a in articles:
        key = (a.get("key") or "").strip().lower()
        if key and key in seen_keys:
            continue
        if key:
            seen_keys.add(key)
        title = _norm_title(a.get("title", ""))
        if title and len(title) > 10:
            if title in seen_titles:
                continue
            seen_titles.add(title)
        result.append(a)
    return result


# ---------------------------------------------------------------------------
# 启发式评分（六维简化版；人工终筛见 scoring-system.md）
# ---------------------------------------------------------------------------
def _cjk_ratio(text: str) -> float:
    if not text:
        return 0.0
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return cjk / max(1, len(text))


def heuristic_score(record: dict, topic_terms: list[str]) -> float:
    text = f"{record.get('title','')} {record.get('abstract','')}".lower()
    relevance = sum(1 for t in topic_terms if t and t in text)
    rel_score = min(relevance / max(1, len(topic_terms)), 1.0) * 100  # 0-100 相关度
    yr = record.get("year", "")
    try:
        y = int(yr) if yr else 0
    except ValueError:
        y = 0
    current = 2026
    recency = max(0, 15 - max(0, current - y) * 1.5) if y else 5
    cited = record.get("cited_by", 0) or 0
    quality = min(20, cited / 50.0 * 20) if cited else 5
    return round(rel_score * 0.6 + recency + quality, 2)


def normalise(record: dict) -> dict:
    """规范化为统一字段（兼容手工 JSON 与 API 输出）。"""
    source = record.get("source") or record.get("database") or "Manual"
    doi = str(record.get("doi") or "").replace("https://doi.org/", "")
    authors = record.get("authors") or ""
    if isinstance(authors, list):
        authors = ", ".join(a.get("name", "") if isinstance(a, dict) else str(a) for a in authors)
    year = str(record.get("year") or record.get("publication_date") or "")
    return {
        "title": str(record.get("title") or "").strip(),
        "authors": str(authors).strip(),
        "journal": str(record.get("journal") or record.get("venue") or ""),
        "year": year[:4],
        "volume": str(record.get("volume") or ""),
        "issue": str(record.get("issue") or ""),
        "pages": str(record.get("pages") or ""),
        "doi": doi,
        "pmid": str(record.get("pmid") or ""),
        "url": str(record.get("url") or (f"https://doi.org/{doi}" if doi else "")),
        "source": str(source),
        "cited_by": int(record.get("cited_by") or record.get("citationCount") or 0),
        "open_access": "Yes" if record.get("has_fulltext") else "Unknown",
        "abstract": str(record.get("abstract") or "").strip(),
    }


# 预印本判定：来源词 + DOI 前缀双重覆盖（任何领域一律不允许预印本进入候选/终选）
_PREPRINT_WORDS = ("arxiv", "biorxiv", "medrxiv", "rxiv", "research square", "researchsquare",
                   "ssrn", "preprint", "pre-print")
_PREPRINT_DOI_PREFIXES = ("10.1101/", "10.21203/", "10.48550/", "10.2139/")


def _is_preprint(record: dict) -> bool:
    """判断是否为预印本（arXiv/bioRxiv/medRxiv/Research Square/SSRN 等）。"""
    blob = " ".join(str(record.get(k, "")) for k in
                    ("title", "journal", "source", "url", "doi", "pages")).lower()
    if any(w in blob for w in _PREPRINT_WORDS):
        return True
    doi = str(record.get("doi", "")).lower()
    return any(doi.startswith(p) for p in _PREPRINT_DOI_PREFIXES)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def _collect_from_apis(queries, domain, years, max_per_db):
    db_list = list(DOMAIN_DATABASES.get(domain, DOMAIN_DATABASES["general"]))
    if domain == "general":
        topic_text = " ".join(queries).lower()
        if any(kw in topic_text for kw in BIOMEDICAL_KEYWORDS):
            for extra in ("pubmed", "europe_pmc"):
                if extra not in db_list:
                    db_list.append(extra)
                    print(f"  [auto] 检测到生物医学关键词，追加 {extra}")
    search_fn = {
        "pubmed": lambda q: fetch_pubmed_details(search_pubmed(q, max_per_db, years)),
        "europe_pmc": lambda q: search_europe_pmc(q, max_per_db, years),
        "openalex": lambda q: search_openalex(q, max_per_db, years),
        "crossref": lambda q: search_crossref(q, max_per_db, years),
        "semantic_scholar": lambda q: search_semantic_scholar(q, max_per_db, years),
        "dblp": lambda q: search_dblp(q, max_per_db),
    }
    all_articles = []
    print(f"Domain: {domain} | Databases: {', '.join(db_list)} | Year range: {years or 'all'}")
    for qi, q in enumerate(queries, 1):
        print(f"=== Query [{qi}/{len(queries)}]: {q} ===")
        for db in db_list:
            fn = search_fn.get(db)
            if not fn:
                continue
            try:
                arts = fn(q)
                print(f"  [{db}] {len(arts)} 篇")
                all_articles.extend(arts)
            except Exception as e:
                print(f"  [{db}] error: {e}")
    return all_articles


def _select_and_write(candidates, output_dir, topic_terms, top_n, keep_indices):
    out = Path(output_dir)
    (out / "candidates").mkdir(parents=True, exist_ok=True)
    norm = [normalise(r) for r in candidates if r.get("title")]
    _pre = [r for r in norm if _is_preprint(r)]
    if _pre:
        print(f"  过滤预印本 {len(_pre)} 篇（任何领域一律禁止引用预印本，只保留正式出版版本）")
    norm = [r for r in norm if not _is_preprint(r)]
    norm = deduplicate(norm)
    # 候选落盘
    (out / "candidates" / "literature_search.json").write_text(
        json.dumps(norm, ensure_ascii=False, indent=2), encoding="utf-8")

    if keep_indices:
        bad = [i for i in keep_indices if i < 1 or i > len(norm)]
        if bad:
            sys.exit(f"--keep-indices 超出范围 1..{len(norm)}: {bad}")
        selected = [norm[i - 1] for i in keep_indices]
    else:
        ranked = sorted(norm, key=lambda r: heuristic_score(r, topic_terms), reverse=True)
        selected = ranked[:top_n]
        print(f"自动排序选取 top {len(selected)}（人工终筛请用 --keep-indices + scoring-system.md）")

    for ref_no, rec in enumerate(selected, 1):
        rec["ref_no"] = ref_no
    (out / "selected_papers.json").write_text(
        json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"候选 {len(norm)} 篇 → 选定 {len(selected)} 篇")
    print(f"已写出: {out / 'selected_papers.json'}")
    return selected


def main() -> None:
    ap = argparse.ArgumentParser(description="ProjGrantGen 自带文献检索与选定")
    ap.add_argument("--queries", nargs="+", default=None, help="检索式（中英文均可，3-5 组）")
    ap.add_argument("--topic", default=None, help="用于评分的主题词（默认取 queries 合并）")
    ap.add_argument("--domain", default="general",
                    choices=list(DOMAIN_DATABASES.keys()))
    ap.add_argument("--years", default="", help="年份范围，如 2021-2026")
    ap.add_argument("--max-per-db", type=int, default=60)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--top-n", type=int, default=60, help="自动选取篇数（可被 --keep-indices 覆盖）")
    ap.add_argument("--from-json", default=None, help="手工/已有候选 JSON（跳过 API 检索）")
    ap.add_argument("--keep-indices", nargs="+", type=int, default=None,
                    help="1-based 候选索引，人工圈定最终集合")
    args = ap.parse_args()

    if args.from_json:
        candidates = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
        if isinstance(candidates, dict):
            for k in ("unique_papers", "relevant_papers", "papers"):
                if isinstance(candidates.get(k), list):
                    candidates = candidates[k]
                    break
        print(f"从 {args.from_json} 读入 {len(candidates)} 条候选")
    elif args.queries:
        candidates = _collect_from_apis(args.queries, args.domain, args.years, args.max_per_db)
    else:
        sys.exit("必须提供 --queries 或 --from-json")

    topic = args.topic or " ".join(args.queries or [])
    topic_terms = [t for t in re.findall(r"[\w\u4e00-\u9fff-]+", topic.lower()) if len(t) > 1]
    _select_and_write(candidates, args.output_dir, topic_terms, args.top_n, args.keep_indices)


if __name__ == "__main__":
    main()
