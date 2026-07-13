#!/usr/bin/env python3
"""
Multi-database literature search, deduplication, and Excel export.
Supports: PubMed, Europe PMC, arXiv (CS/AI only), Semantic Scholar, Crossref,
          OpenAlex, DBLP, IEEE Xplore, Dimensions.

Preprint servers (bioRxiv, medRxiv) are NOT searched by default. The --domain
setting controls which databases are used; see DOMAIN_DATABASES below.

Usage:
    python multi_db_search.py --topic "mRNA cancer vaccine" --output-dir ./search_results
                               --max_per_db 80 --years 2021-2025
                               --domain biomedical

    python multi_db_search.py --topic "transformer architecture NLP" --output-dir ./search_results
                              --domain cs_ai

    # API keys via environment variables:
    #   NCBI_API_KEY     (PubMed, for higher rate limits)
    #   IEEE_API_KEY     (IEEE Xplore)
    #   DIMENSIONS_API_KEY (Dimensions.ai)
"""

import argparse, json, os, re, sys, time, xml.etree.ElementTree as ET

from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print("requests is required. Install with: pip install requests")
    sys.exit(1)

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
except ImportError:
    print("openpyxl required for Excel export. Install: pip install openpyxl")
    sys.exit(1)


NCBI_API_KEY = os.environ.get("NCBI_API_KEY", "")
SEMANTIC_SCHOLAR_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")

USER_AGENT = "ReviewGenerator/1.0 (https://github.com/anomalyco/review-generator)"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", title.lower().strip())[:60]

# ---------------------------------------------------------------------------
# PubMed
# ---------------------------------------------------------------------------
def search_pubmed(query: str, max_results: int = 80, years: str = "") -> list[str]:
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    full_query = query
    if years and "-" in years:
        yr = years.replace("-", ":")
        full_query = f"({query}) AND {yr}[dp]"
    elif years:
        full_query = f"({query}) AND {years}[dp]"
    params = {"db": "pubmed", "term": full_query, "retmax": max_results,
              "retmode": "json", "sort": "relevance"}
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
        time.sleep(0.1)
    else:
        time.sleep(0.34)
    try:
        r = requests.get(f"{base}esearch.fcgi", params=params, timeout=30)
        result = r.json().get("esearchresult", {})
        idlist = result.get("idlist", [])
        if not idlist and result.get("warning"):
            print(f"  PubMed warning: {result.get('warning')}")
        if not idlist and result.get("errorlist"):
            print(f"  PubMed error: {result.get('errorlist')}")
        return idlist
    except Exception as e:
        print(f"  PubMed search error: {e}")
        return []


def fetch_pubmed_details(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml", "rettype": "abstract"}
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
        time.sleep(0.1)
    else:
        time.sleep(0.34)
    try:
        r = requests.get(f"{base}efetch.fcgi", params=params, timeout=30)
        return _parse_pubmed_xml(r.text)
    except Exception as e:
        print(f"  PubMed fetch error: {e}")
        return []


def _parse_pubmed_xml(xml: str) -> list[dict]:
    root = ET.fromstring(xml)
    articles = []
    for art in root.findall(".//PubmedArticle"):
        d: dict[str, Any] = {"source": "PubMed"}
        d["pmid"] = _txt(art, ".//PMID")
        d["title"] = _txt_iter(art, ".//ArticleTitle")
        ab_elems = art.findall(".//AbstractText")
        d["abstract"] = " ".join(["".join(ae.itertext()) for ae in ab_elems]) if ab_elems else ""
        authors = art.findall(".//Author")
        alist = []
        for a in authors[:10]:
            last = a.findtext("LastName", "")
            fore = a.findtext("ForeName", "")
            if last:
                alist.append(f"{last} {fore[0]}." if fore else last)
        d["authors"] = ", ".join(alist) if alist else "Unknown"
        d["journal"] = art.findtext(".//Journal/ISOAbbreviation", "")
        d["year"] = art.findtext(".//PubDate/Year", "") or art.findtext(".//PubDate/MedlineDate", "")[:4]
        d["volume"] = art.findtext(".//Volume", "")
        d["issue"] = art.findtext(".//Issue", "")
        d["pages"] = art.findtext(".//Pagination/MedlinePgn", "")
        doi_e = art.find(".//ELocationID[@EIdType='doi']")
        d["doi"] = doi_e.text if doi_e is not None else ""
        pmc_e = art.find(".//ArticleId[@IdType='pmc']")
        d["pmcid"] = pmc_e.text if pmc_e is not None else ""
        d["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{d['pmid']}/" if d["pmid"] else ""
        d["key"] = d["doi"] or d["pmid"]
        d["cited_by"] = 0
        d["has_fulltext"] = bool(d.get("pmcid", ""))
        articles.append(d)
    return articles


def _txt(elem, xpath: str, ns: dict | None = None) -> str:
    e = elem.find(xpath, ns) if ns else elem.find(xpath)
    return e.text if e is not None else ""


def _txt_iter(elem, xpath: str) -> str:
    e = elem.find(xpath)
    return "".join(e.itertext()) if e is not None else ""


# ---------------------------------------------------------------------------
# arXiv
# ---------------------------------------------------------------------------
def search_arxiv(query: str, max_results: int = 50) -> list[dict]:
    base = "https://export.arxiv.org/api/query"
    safe_q = requests.utils.quote(query.replace(" ", "+AND+"))
    params = f"search_query=all:{safe_q}&start=0&max_results={max_results}&sortBy=relevance"
    try:
        r = requests.get(f"{base}?{params}", timeout=30)
        return _parse_arxiv_xml(r.text)
    except Exception as e:
        print(f"  arXiv search error: {e}")
        return []


def _parse_arxiv_xml(xml: str) -> list[dict]:
    ns = {"a": "http://www.w3.org/2005/Atom",
          "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(xml)
    articles = []
    for entry in root.findall("a:entry", ns):
        d: dict[str, Any] = {"source": "arXiv"}
        d["title"] = _txt(entry, "a:title", ns).replace("\n", " ").strip()
        d["abstract"] = _txt(entry, "a:summary", ns).replace("\n", " ").strip()
        d["year"] = _txt(entry, "a:published", ns)[:4]
        authors = []
        for a in entry.findall("a:author", ns):
            name = _txt(a, "a:name", ns)
            if name:
                authors.append(name)
        d["authors"] = ", ".join(authors[:10]) if authors else "Unknown"
        d["journal"] = "arXiv preprint"
        d["doi"] = ""
        for link in entry.findall("a:link", ns):
            if link.get("title") == "doi":
                d["doi"] = link.get("href", "").replace("https://doi.org/", "")
        d["pmid"] = ""
        d["url"] = _txt(entry, "a:id", ns)
        d["key"] = d["doi"] or d["url"]
        d["cited_by"] = 0
        d["has_fulltext"] = True  # arXiv always has full text
        articles.append(d)
    return articles


# ---------------------------------------------------------------------------
# Semantic Scholar
# ---------------------------------------------------------------------------
def search_semantic_scholar(query: str, max_results: int = 50, years: str = "") -> list[dict]:
    base = "https://api.semanticscholar.org/graph/v1/paper/search"
    fields = "title,externalIds,authors,year,journal,abstract,url,citationCount,isOpenAccess"
    params = {"query": query, "limit": min(max_results, 100), "fields": fields}
    if years and "-" in years:
        y = years.split("-")
        if len(y) == 2:
            params["year"] = f"{y[0]}-{y[1]}"
    headers = {"x-api-key": SEMANTIC_SCHOLAR_API_KEY} if SEMANTIC_SCHOLAR_API_KEY else {}
    if not SEMANTIC_SCHOLAR_API_KEY:
        time.sleep(3.0)
    try:
        r = requests.get(base, params=params, headers=headers, timeout=30)
        data = r.json()
        results = data.get("data", [])
        if not results:
            print(f"  Semantic Scholar: 0 results for query '{query[:60]}...'")
            if "error" in data:
                print(f"  Semantic Scholar error: {data['error']}")
        return _parse_s2(results)
    except Exception as e:
        print(f"  Semantic Scholar search error: {e}")
        return []


def _parse_s2(data: list) -> list[dict]:
    articles = []
    for p in data:
        d: dict[str, Any] = {"source": "Semantic Scholar"}
        d["title"] = p.get("title", "")
        d["abstract"] = p.get("abstract", "") or ""
        ext = p.get("externalIds", {}) or {}
        d["doi"] = ext.get("DOI", "")
        d["pmid"] = ext.get("PubMed", "")
        year = p.get("year")
        d["year"] = str(year) if year else ""
        authors = p.get("authors", [])
        d["authors"] = ", ".join([a.get("name", "") for a in authors[:10]]) if authors else "Unknown"
        j = p.get("journal")
        d["journal"] = (j.get("name", "") if isinstance(j, dict) else str(j)) if j else ""
        d["url"] = p.get("url", "")
        d["key"] = d["doi"] or d["pmid"]
        d["cited_by"] = p.get("citationCount", 0) or 0
        d["has_fulltext"] = bool(p.get("isOpenAccess", False))
        articles.append(d)
    return articles


# ---------------------------------------------------------------------------
# Crossref
# ---------------------------------------------------------------------------
def search_crossref(query: str, max_results: int = 50, years: str = "") -> list[dict]:
    base = "https://api.crossref.org/works"
    params = {"query": query, "rows": min(max_results, 100), "sort": "relevance", "order": "desc"}
    if years:
        params["filter"] = f"from-pub-date:{years[:4]},until-pub-date:{years[5:]}"
    try:
        r = requests.get(base, params=params, timeout=30, headers={"User-Agent": USER_AGENT})
        data = r.json()
        items = data.get("message", {}).get("items", [])
        return _parse_crossref(items)
    except Exception as e:
        print(f"  Crossref search error: {e}")
        return []


def _parse_crossref(items: list) -> list[dict]:
    articles = []
    for p in items:
        d: dict[str, Any] = {"source": "Crossref"}
        d["title"] = p.get("title", [""])[0] if p.get("title") else ""
        d["abstract"] = p.get("abstract", "") or ""
        d["doi"] = p.get("DOI", "")
        d["pmid"] = ""
        for id_ in p.get("alternative-id", []):
            if id_.isdigit():
                d["pmid"] = id_
        year = ""
        if p.get("published-print"):
            year = str(p["published-print"].get("date-parts", [[""]])[0][0])
        elif p.get("published-online"):
            year = str(p["published-online"].get("date-parts", [[""]])[0][0])
        elif p.get("created"):
            year = str(p["created"].get("date-parts", [[""]])[0][0])
        d["year"] = year
        authors = p.get("author", [])
        d["authors"] = ", ".join([f"{a.get('family','')} {a.get('given','')[:1]}." for a in authors[:10]]) if authors else "Unknown"
        d["journal"] = (p.get("container-title", [""])[0] if p.get("container-title") else p.get("publisher", ""))
        d["url"] = f"https://doi.org/{d['doi']}" if d["doi"] else ""
        d["key"] = d["doi"]
        d["cited_by"] = p.get("is-referenced-by-count", 0) or 0
        d["has_fulltext"] = False
        articles.append(d)
    return articles


# ---------------------------------------------------------------------------
# OpenAlex (NEW) — Free, open, 254M+ works, all disciplines
# ---------------------------------------------------------------------------
def search_openalex(query: str, max_results: int = 50, years: str = "") -> list[dict]:
    base = "https://api.openalex.org/works"
    params: dict[str, Any] = {
        "search": query,
        "per_page": min(max_results, 200),
        "sort": "cited_by_count:desc",
        "select": "id,doi,title,authorships,publication_date,primary_location,abstract_inverted_index,cited_by_count,open_access,type,type_crossref"
    }
    if years and "-" in years:
        params["filter"] = f"from_publication_date:{years[:4]}-01-01,to_publication_date:{years[5:]}-12-31"
    # Polite pool: 1 request per 100ms
    time.sleep(0.11)
    try:
        r = requests.get(base, params=params, timeout=30,
                         headers={"User-Agent": USER_AGENT})
        data = r.json()
        return _parse_openalex(data.get("results", []))
    except Exception as e:
        print(f"  OpenAlex search error: {e}")
        return []


def _parse_openalex(results: list) -> list[dict]:
    articles = []
    for p in results:
        d: dict[str, Any] = {"source": "OpenAlex"}
        d["title"] = p.get("title", "") or ""
        # Reconstruct abstract from inverted index
        inv_idx = p.get("abstract_inverted_index")
        if inv_idx:
            word_positions = []
            for word, positions in inv_idx.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort()
            d["abstract"] = " ".join([w for _, w in word_positions])
        else:
            d["abstract"] = ""
        d["doi"] = (p.get("doi", "") or "").replace("https://doi.org/", "")
        d["pmid"] = ""
        # Get year
        pub_date = p.get("publication_date", "") or ""
        d["year"] = pub_date[:4] if pub_date else ""
        # Authors
        authors = p.get("authorships", []) or []
        alist = []
        for a in authors[:10]:
            name = (a.get("author") or {}).get("display_name", "")
            if name:
                alist.append(name)
        d["authors"] = ", ".join(alist) if alist else "Unknown"
        # Venue
        loc = p.get("primary_location") or {}
        source = loc.get("source") or {}
        d["journal"] = source.get("display_name", "") or ""
        d["url"] = f"https://doi.org/{d['doi']}" if d["doi"] else ""
        d["key"] = d["doi"] or d["title"]
        d["cited_by"] = p.get("cited_by_count", 0) or 0
        # Open access
        oa = p.get("open_access") or {}
        d["has_fulltext"] = bool(oa.get("is_oa", False))
        d["oa_url"] = oa.get("oa_url", "") or ""
        articles.append(d)
    return articles


# ---------------------------------------------------------------------------
# Europe PMC (NEW) — Life sciences, 41M+ abstracts, 8M+ full-text OA articles
# ---------------------------------------------------------------------------
def search_europe_pmc(query: str, max_results: int = 50, years: str = "") -> list[dict]:
    base = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params: dict[str, Any] = {
        "query": query,
        "resultType": "core",
        "pageSize": min(max_results, 100),
        "format": "json",
        "sort": "CITED desc",
    }
    if years and "-" in years:
        params["query"] = f"({query}) AND (FIRST_PDATE:[{years[:4]}-01-01 TO {years[5:]}-12-31])"
    try:
        r = requests.get(base, params=params, timeout=30)
        data = r.json()
        results = data.get("resultList", {}).get("result", [])
        return _parse_europe_pmc(results)
    except Exception as e:
        print(f"  Europe PMC search error: {e}")
        return []


def _parse_europe_pmc(results: list) -> list[dict]:
    articles = []
    for p in results:
        d: dict[str, Any] = {"source": "Europe PMC"}
        d["title"] = p.get("title", "") or ""
        d["abstract"] = p.get("abstractText", "") or ""
        d["doi"] = p.get("doi", "") or ""
        d["pmid"] = p.get("pmid", "") or p.get("source", "") or ""
        d["pmcid"] = p.get("pmcid", "") or ""
        d["year"] = p.get("pubYear", "") or ""
        author_str = p.get("authorString", "") or ""
        if author_str:
            authors = author_str.split(", ")
            d["authors"] = ", ".join(authors[:10])
        else:
            d["authors"] = "Unknown"
        d["journal"] = p.get("journalTitle", "") or p.get("bookOrReportDetails", {}).get("publisher", "") or ""
        d["url"] = f"https://doi.org/{d['doi']}" if d["doi"] else p.get("fullTextUrlList", {}).get("fullTextUrl", [{}])[0].get("url", "") if p.get("fullTextUrlList") else ""
        d["key"] = d["doi"] or d["pmid"] or d["title"]
        d["cited_by"] = p.get("citedByCount", 0) or 0
        d["has_fulltext"] = bool(p.get("hasPDF", "") == "Y" or d["pmcid"] or p.get("isOpenAccess", "") == "Y")
        d["oa_url"] = p.get("fullTextUrlList", {}).get("fullTextUrl", [{}])[0].get("url", "") if p.get("fullTextUrlList") else ""
        articles.append(d)
    return articles


# ---------------------------------------------------------------------------
# Dimensions.ai (NEW) — 140M+ publications, grants, patents, clinical trials
# Requires DIMENSIONS_API_KEY environment variable
# ---------------------------------------------------------------------------
def search_dimensions(query: str, max_results: int = 50, years: str = "",
                      api_key: str = "") -> list[dict]:
    if not api_key:
        api_key = os.environ.get("DIMENSIONS_API_KEY", "")
    if not api_key:
        print("  Dimensions: No API key found. Set DIMENSIONS_API_KEY env var. Skipping.")
        return []

    base = "https://app.dimensions.ai/api/dsl/v2"
    dsl_query = f'search publications for "{query}" return publications[id+doi+title+authors+year+journal+times_cited+abstract] sort by times_cited limit {min(max_results, 50)}'
    if years and "-" in years:
        dsl_query = f'search publications for "{query}" where year in [{years[:4]}:{years[5:]}] return publications[id+doi+title+authors+year+journal+times_cited+abstract] sort by times_cited limit {min(max_results, 50)}'

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        r = requests.post(base, json={"query": dsl_query}, headers=headers, timeout=30)
        data = r.json()
        publications = data.get("publications", [])
        return _parse_dimensions(publications)
    except Exception as e:
        print(f"  Dimensions search error: {e}")
        return []


def _parse_dimensions(publications: list) -> list[dict]:
    articles = []
    for p in publications:
        d: dict[str, Any] = {"source": "Dimensions"}
        d["title"] = p.get("title", "") or ""
        d["abstract"] = p.get("abstract", "") or ""
        d["doi"] = p.get("doi", "") or ""
        d["pmid"] = ""
        d["year"] = str(p.get("year", "")) or ""
        authors = p.get("authors", []) or []
        alist = []
        for a in authors[:10]:
            fn = a.get("first_name", "")
            ln = a.get("last_name", "")
            if ln:
                alist.append(f"{ln} {fn[0]}." if fn else ln)
        d["authors"] = ", ".join(alist) if alist else "Unknown"
        j = p.get("journal") or {}
        d["journal"] = j.get("title", "") if isinstance(j, dict) else str(j) if j else ""
        d["url"] = f"https://doi.org/{d['doi']}" if d["doi"] else ""
        d["key"] = d["doi"] or d["title"]
        d["cited_by"] = p.get("times_cited", 0) or 0
        d["has_fulltext"] = False
        articles.append(d)
    return articles


# ---------------------------------------------------------------------------
# DBLP — Computer science bibliography, covers all major CS conferences
# ---------------------------------------------------------------------------
def search_dblp(query: str, max_results: int = 50) -> list[dict]:
    base = "https://dblp.org/search/publ/api"
    params = {"q": query, "h": min(max_results, 100), "format": "json"}
    try:
        r = requests.get(base, params=params, timeout=30)
        data = r.json()
        hits = data.get("result", {}).get("hits", {}).get("hit", [])
        return _parse_dblp(hits)
    except Exception as e:
        print(f"  DBLP search error: {e}")
        return []


def _parse_dblp(hits: list) -> list[dict]:
    articles = []
    for hit in hits:
        info = hit.get("info", {})
        d: dict[str, Any] = {"source": "DBLP"}
        d["title"] = info.get("title", "") or ""
        d["abstract"] = ""  # DBLP doesn't provide abstracts
        d["doi"] = info.get("doi", "") or ""
        d["pmid"] = ""
        d["year"] = str(info.get("year", "")) or ""
        authors = info.get("authors", {}).get("author", [])
        if isinstance(authors, str):
            authors = [authors]
        elif isinstance(authors, dict):
            authors = [authors.get("text", "")]
        d["authors"] = ", ".join(authors[:10]) if authors else "Unknown"
        # Venue
        venue = info.get("venue", "") or ""
        d["journal"] = venue
        d["url"] = info.get("url", "") or ""
        d["key"] = d["doi"] or d["title"]
        d["cited_by"] = 0
        d["has_fulltext"] = bool(d["doi"])
        articles.append(d)
    return articles


# ---------------------------------------------------------------------------
# IEEE Xplore (NEW) — Requires API key (env: IEEE_API_KEY)
# ---------------------------------------------------------------------------
def search_ieee(query: str, max_results: int = 50, years: str = "",
                api_key: str = "") -> list[dict]:
    if not api_key:
        api_key = os.environ.get("IEEE_API_KEY", "")
    if not api_key:
        print("  IEEE Xplore: No API key found. Set IEEE_API_KEY env var or pass --ieee_api_key")
        return []

    base = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
    params: dict[str, Any] = {
        "apikey": api_key,
        "format": "json",
        "max_records": min(max_results, 100),
        "start_record": 1,
        "sort_order": "desc",
        "sort_field": "article_number",
        "query_text": f"({query})"
    }
    if years and "-" in years:
        params["start_year"] = years[:4]
        params["end_year"] = years[5:]
    try:
        r = requests.get(base, params=params, timeout=30)
        data = r.json()
        articles = data.get("articles", [])
        return _parse_ieee(articles)
    except Exception as e:
        print(f"  IEEE Xplore search error: {e}")
        return []


def _parse_ieee(articles: list) -> list[dict]:
    results = []
    for p in articles:
        d: dict[str, Any] = {"source": "IEEE Xplore"}
        d["title"] = p.get("title", "") or ""
        d["abstract"] = p.get("abstract", "") or ""
        d["doi"] = p.get("doi", "") or ""
        d["pmid"] = ""
        d["year"] = str(p.get("publication_year", "")) or ""
        authors = p.get("authors", {}).get("authors", []) if isinstance(p.get("authors"), dict) else []
        alist = [a.get("full_name", "") for a in authors[:10] if a.get("full_name")]
        d["authors"] = ", ".join(alist) if alist else "Unknown"
        d["journal"] = p.get("publication_title", "") or ""
        d["url"] = p.get("pdf_url", "") or (f"https://doi.org/{d['doi']}" if d["doi"] else "")
        d["key"] = d["doi"] or d["title"]
        d["cited_by"] = p.get("citing_paper_count", 0) or 0
        d["has_fulltext"] = bool(p.get("pdf_url", ""))
        results.append(d)
    return results


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------
def deduplicate(articles: list[dict]) -> list[dict]:
    """Remove duplicates by DOI, then PMID, then normalized title."""
    seen_keys: set[str] = set()
    seen_titles: set[str] = set()
    result = []
    for a in articles:
        key = a.get("key", "").strip().lower()
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
# Literature Excel generation
# ---------------------------------------------------------------------------
def write_literature_excel(articles: list[dict], output_path: str) -> str:
    """Write literature to Excel, return the path."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Literature"

    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
    header_align = Alignment(horizontal="center", vertical="center")
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin"))

    headers = ["Ref#", "Title", "Authors", "Journal", "Year", "Source DB",
               "DOI", "PMID", "URL", "Cited By", "Open Access", "Abstract"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border

    for i, a in enumerate(articles, 1):
        ws.cell(row=i+1, column=1, value=i).border = thin_border
        ws.cell(row=i+1, column=2, value=a.get("title", "")[:300]).border = thin_border
        ws.cell(row=i+1, column=3, value=a.get("authors", "")[:200]).border = thin_border
        ws.cell(row=i+1, column=4, value=a.get("journal", "")[:120]).border = thin_border
        ws.cell(row=i+1, column=5, value=a.get("year", "")).border = thin_border
        ws.cell(row=i+1, column=6, value=a.get("source", "")).border = thin_border
        ws.cell(row=i+1, column=7, value=a.get("doi", "")).border = thin_border
        ws.cell(row=i+1, column=8, value=a.get("pmid", "")).border = thin_border
        ws.cell(row=i+1, column=9, value=a.get("url", "")).border = thin_border
        ws.cell(row=i+1, column=10, value=a.get("cited_by", 0)).border = thin_border
        ws.cell(row=i+1, column=11, value="Yes" if a.get("has_fulltext") else "No").border = thin_border
        ws.cell(row=i+1, column=12, value=a.get("abstract", "")[:500]).border = thin_border

    # Column widths
    widths = {"A": 6, "B": 70, "C": 40, "D": 30, "E": 8, "F": 18,
              "G": 30, "H": 10, "I": 45, "J": 10, "K": 12, "L": 80}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    wb.save(output_path)
    return output_path


# ---------------------------------------------------------------------------
# Domain-aware database selection
# ---------------------------------------------------------------------------
# Biomedical keywords for general domain auto-detection
BIOMEDICAL_KEYWORDS = [
    "cancer", "tumor", "tumour", "disease", "clinical", "patient", "patients",
    "cell", "cells", "protein", "gene", "genome", "genomic", "transcriptom",
    "proteom", "metabolom", "pathway", "signaling", "therap", "drug",
    "diagnos", "prognos", "biomarker", "infection", "immun", "mutation",
    "kinase", "receptor", "ligand", "enzyme", "antibod", "virus", "bacter",
    "inflammat", "apoptos", "differentiation", "stem cell",
]

DOMAIN_DATABASES = {
    "biomedical": ["pubmed", "europe_pmc", "semantic_scholar", "crossref", "openalex", "dimensions"],
    "cs_ai": ["dblp", "semantic_scholar", "openalex", "crossref", "arxiv", "dimensions", "ieee"],
    "cross": ["pubmed", "europe_pmc", "semantic_scholar", "crossref", "openalex", "dblp", "arxiv", "dimensions"],
    "general": ["openalex", "semantic_scholar", "crossref", "dimensions"],
    "all": ["pubmed", "europe_pmc", "arxiv", "semantic_scholar", "crossref", "openalex", "dblp", "ieee", "dimensions"],
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Multi-database literature search")
    parser.add_argument("--topic", default=None, help="Search topic (single topic)")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--max_per_db", type=int, default=80, help="Max results per database")
    parser.add_argument("--years", default="", help="Year range, e.g. 2021-2025 (empty = no limit)")
    parser.add_argument("--domain", default="all",
                        choices=list(DOMAIN_DATABASES.keys()),
                        help="Domain for automatic database selection")
    parser.add_argument("--databases", nargs="+", default=None,
                        help="Explicit database list (overrides --domain)")
    parser.add_argument("--ieee_api_key", default="",
                        help="IEEE Xplore API key (or set IEEE_API_KEY env var)")
    parser.add_argument("--topics", nargs="+", default=None,
                        help="Multiple search topics (alternative to --topic). Runs each topic separately and merges results.")
    args = parser.parse_args()

    # Support multiple topics
    topics = args.topics if args.topics else ([args.topic] if args.topic else [])
    if not topics:
        print("Error: Either --topic or --topics must be provided.")
        sys.exit(1)

    # Determine databases
    if args.databases:
        db_list = args.databases
    else:
        db_list = list(DOMAIN_DATABASES.get(args.domain, DOMAIN_DATABASES["all"]))
        # Auto-detect: if domain is "general" and topic contains biomedical keywords,
        # conditionally add pubmed and europe_pmc to reach ≥4 databases
        if args.domain == "general":
            topic_text = " ".join(topics).lower()
            if any(kw in topic_text for kw in BIOMEDICAL_KEYWORDS):
                for extra_db in ["pubmed", "europe_pmc"]:
                    if extra_db not in db_list:
                        db_list.append(extra_db)
                        print(f"  [auto] Added {extra_db} — biomedical keywords detected in topic")

    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Domain: {args.domain}")
    print(f"Databases: {', '.join(db_list)}")
    if args.years:
        print(f"Year range: {args.years}")
    else:
        print("Year range: No limit (will search all years)")
    print(f"Topics: {len(topics)} topic(s)")
    for i, t in enumerate(topics):
        print(f"  [{i+1}] {t}")
    print()

    all_articles = []

    search_fn = {
        "pubmed": lambda q: fetch_pubmed_details(
            search_pubmed(q, args.max_per_db, args.years)),
        "europe_pmc": lambda q: search_europe_pmc(
            q, args.max_per_db, args.years),
        "arxiv": lambda q: search_arxiv(q, args.max_per_db),
        "semantic_scholar": lambda q: search_semantic_scholar(
            q, args.max_per_db, args.years),
        "crossref": lambda q: search_crossref(
            q, args.max_per_db, args.years),
        "openalex": lambda q: search_openalex(
            q, args.max_per_db, args.years),
        "dblp": lambda q: search_dblp(q, args.max_per_db),
        "ieee": lambda q: search_ieee(
            q, args.max_per_db, args.years, args.ieee_api_key),
        "dimensions": lambda q: search_dimensions(
            q, args.max_per_db, args.years),
    }

    for topic_idx, topic in enumerate(topics):
        print(f"=== Topic [{topic_idx+1}/{len(topics)}]: {topic} ===")
        for db_name in db_list:
            fn = search_fn.get(db_name)
            if not fn:
                print(f"[{db_name.capitalize()}] Unknown database, skipped")
                continue
            print(f"[{db_name.capitalize()}] Searching...")
            try:
                articles = fn(topic)
                print(f"  Found {len(articles)} articles")
                if len(articles) == 0:
                    print(f"  WARNING: {db_name} returned 0 results for '{topic[:60]}...'")
                    print(f"  TIP: Try shorter, more focused queries (2-3 keywords)")
                all_articles.extend(articles)
            except Exception as e:
                print(f"  Error: {e}")

    # Deduplicate
    total = len(all_articles)
    all_articles = deduplicate(all_articles)
    deduped = total - len(all_articles)
    print(f"\nTotal before dedup: {total}, after: {len(all_articles)} ({deduped} removed)")

    # Sort by year desc, then cited_by desc
    def sort_key(a):
        y = a.get("year", "0")
        try:
            return (-int(y) if y else 0, -(a.get("cited_by", 0) or 0))
        except ValueError:
            return (0, -(a.get("cited_by", 0) or 0))
    all_articles.sort(key=sort_key)

    # Save JSON
    json_path = Path(args.output_dir) / "literature_search.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON: {json_path}")

    # Save Excel
    excel_path = Path(args.output_dir) / "literature_search.xlsx"
    write_literature_excel(all_articles, excel_path)
    print(f"Saved Excel: {excel_path}")

    # Source breakdown
    sources: dict[str, int] = {}
    for a in all_articles:
        s = a.get("source", "Unknown")
        sources[s] = sources.get(s, 0) + 1
    print("\nSource breakdown:")
    for s, n in sorted(sources.items()):
        print(f"  {s}: {n}")

    # Full-text availability
    ft_count = sum(1 for a in all_articles if a.get("has_fulltext"))
    print(f"\nOpen Access / Full-text available: {ft_count}/{len(all_articles)}")

    # Zero-result warning
    if len(all_articles) < 20:
        print(f"\nWARNING: Only {len(all_articles)} articles found (< 20).")
        print("TIP: Try the following strategies:")
        print("  1. Use --topics with multiple shorter queries instead of one long --topic")
        print("     Example: --topics 'RNH1 gene function' 'ribonuclease inhibitor cancer' 'RNH1 angiogenin'")
        print("  2. Remove year restrictions (omit --years)")
        print("  3. Use more general keywords or synonyms")
        print("  4. Add more databases with --databases pubmed openalex crossref semantic_scholar")


if __name__ == "__main__":
    main()
