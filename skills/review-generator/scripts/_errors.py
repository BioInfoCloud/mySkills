"""Shared error taxonomy, exit codes, structured reporting, and retry helpers.

Every pipeline script speaks the same error language:

    ERROR [RG-201] openalex: 3 attempt(s) exhausted (HTTP 429)
    HINT: Re-run with --resume to continue from the checkpoint.

Error code scheme (RG = Review Generator). The numeric band encodes severity,
and the second digit encodes the subsystem.

    RG-000  success                                     exit 0
    RG-100  usage / argument error                      exit 2
    RG-101  missing or unreadable input file            exit 2
    RG-102  malformed input data                        exit 2
    RG-103  value outside permitted range               exit 2
    RG-200  every data source failed                    exit 3
    RG-201  partial data-source failure (warning)       exit 0
    RG-202  result count below threshold (warning)      exit 0
    RG-203  --strict escalation of RG-201/RG-202        exit 3
    RG-300  contract / validation failure               exit 1
    RG-301  missing or empty deliverable                exit 1
    RG-302  readability contract failure                exit 1
    RG-303  writing-style advisory (warning)            exit 0
    RG-304  list-format violation (hard-coded bullet)   exit 1
    RG-400  remote API failure after retries            exit 3
    RG-500  unexpected internal error                   exit 1

Structured output contract: machine-readable lines are always prefixed with a
stable token (``ERROR [RG-xxx]`` / ``WARNING [RG-xxx]`` / ``HINT:``), so a
caller can grep the failure class without parsing free-form prose. Call
``write_report`` to also persist the collected issues as JSON.
"""

from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path
from typing import Any, Callable, Iterable, NoReturn

EXIT_BY_CODE: dict[str, int] = {
    "RG-000": 0,
    "RG-100": 2,
    "RG-101": 2,
    "RG-102": 2,
    "RG-103": 2,
    "RG-200": 3,
    "RG-201": 0,
    "RG-202": 0,
    "RG-203": 3,
    "RG-300": 1,
    "RG-301": 1,
    "RG-302": 1,
    "RG-303": 0,
    "RG-304": 1,
    "RG-400": 3,
    "RG-500": 1,
}

_SEVERITY_BY_CODE: dict[str, str] = {
    "RG-201": "warning",
    "RG-202": "warning",
    "RG-303": "warning",
}

_ISSUES: list[dict[str, str]] = []


class RGError(Exception):
    """A classified, user-facing pipeline error."""

    def __init__(self, code: str, message: str, hint: str = "") -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint

    @property
    def exit_code(self) -> int:
        return EXIT_BY_CODE.get(self.code, 1)


def _emit(code: str, severity: str, message: str, hint: str = "") -> None:
    _ISSUES.append({"code": code, "severity": severity, "message": message, "hint": hint})
    token = severity.upper()
    line = f"{token} [{code}] {message}"
    stream = sys.stderr if severity == "error" else sys.stdout
    print(line, file=stream)
    if hint:
        print(f"HINT: {hint}", file=stream)


def error(code: str, message: str, hint: str = "") -> None:
    """Record and print an error-level issue (does not exit)."""
    _emit(code, "error", message, hint)


def warn(code: str, message: str, hint: str = "") -> None:
    """Record and print a warning-level issue (does not exit)."""
    _emit(code, "warning", message, hint)


def fail(code: str, message: str, hint: str = "") -> NoReturn:
    """Record an error-level issue and terminate with the mapped exit code."""
    _emit(code, "error", message, hint)
    raise SystemExit(EXIT_BY_CODE.get(code, 1))


def retry_call(
    fn: Callable[[], Any],
    *,
    label: str,
    attempts: int = 4,
    base_delay: float = 1.0,
    max_delay: float = 20.0,
    on_retry: Callable[[int, float, BaseException], None] | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> Any:
    """Call ``fn`` with exponential backoff and jitter.

    Retries any exception raised by ``fn``. Re-raises the final exception so the
    caller can classify it; ``on_retry`` receives (attempt_index, delay, exc).
    """
    last: BaseException | None = None
    for attempt in range(1, max(1, attempts) + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - retry wrapper is intentionally broad
            last = exc
            if attempt >= attempts:
                break
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            delay += random.uniform(0, delay * 0.25)
            if on_retry is not None:
                on_retry(attempt, delay, exc)
            else:
                print(f"  retry {attempt}/{attempts - 1} for {label} in {delay:.1f}s ({exc})")
            sleep(delay)
    assert last is not None
    raise last


def write_report(path: str | Path) -> Path | None:
    """Persist collected issues as JSON. Returns the path, or None if empty."""
    if not _ISSUES:
        return None
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps({"issues": _ISSUES}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return target


def summary_line() -> str:
    errors = sum(1 for i in _ISSUES if i["severity"] == "error")
    warnings = sum(1 for i in _ISSUES if i["severity"] == "warning")
    return f"issues: {errors} error(s), {warnings} warning(s)"


def run_guarded(fn: Callable[[], None]) -> None:
    """Run ``fn``, converting RGError and unexpected exceptions into exit codes."""
    try:
        fn()
    except RGError as exc:
        _emit(exc.code, "error", exc.message, exc.hint)
        raise SystemExit(exc.exit_code) from None
    except SystemExit:
        raise
    except KeyboardInterrupt:
        warn("RG-500", "interrupted by user")
        raise SystemExit(130) from None
    except Exception as exc:  # noqa: BLE001 - top-level guard
        _emit("RG-500", f"unexpected internal error: {exc.__class__.__name__}: {exc}",
              "This is a defect. Re-run with --resume; if it repeats, report it.")
        raise SystemExit(1) from None


def parse_int_in_range(
    raw: str | int,
    *,
    name: str,
    low: int,
    high: int,
) -> int:
    """Parse and range-check an integer argument, failing with RG-103."""
    try:
        value = int(raw)
    except (TypeError, ValueError):
        fail("RG-103", f"{name} must be an integer, got {raw!r}")
    if not low <= value <= high:
        fail("RG-103", f"{name} must be between {low} and {high}, got {value}")
    return value


def require_files(paths: Iterable[str | Path], *, code: str = "RG-101") -> list[Path]:
    """Fail unless every path exists and is a non-empty file."""
    resolved: list[Path] = []
    for raw in paths:
        candidate = Path(raw)
        if not candidate.is_file():
            fail(code, f"missing input file: {candidate}",
                 "Check --input/--input-dir and that the previous pipeline step completed.")
        if candidate.stat().st_size == 0:
            fail(code, f"empty input file: {candidate}")
        resolved.append(candidate)
    return resolved
