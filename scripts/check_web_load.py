#!/usr/bin/env python3
"""Run web-page load checks against a generated PayTV Seeker JSON report.

Important: the positional argument is a report JSON file, usually
``reports/latest.json``.  It is not the project ZIP archive.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Reporting.web_access_checker import WebAccessChecker


def _load_report(path: Path) -> dict:
    if path.suffix.lower() == ".zip":
        raise ValueError(
            "You passed the project ZIP archive. Extract it, run `python3 main.py` "
            "with PAYTV_CHECK_WEB_LOAD=1, then pass `reports/latest.json` to this script."
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError(f"Report is not a UTF-8 JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Report is not valid JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"Report JSON must contain an object at the top level: {path}")
    if "results" not in payload:
        raise ValueError(
            f"Report JSON does not contain a `results` field: {path}. "
            "Use the main seeker report, usually `reports/latest.json`, not `latest_web_load.json`."
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether URLs in a PayTV Seeker report load as web pages.")
    parser.add_argument("report", nargs="?", default="reports/latest.json", help="Path to report JSON, default: reports/latest.json")
    parser.add_argument("--output-dir", default="reports", help="Directory for web-load reports")
    parser.add_argument("--timeout", type=float, default=None, help="Per-URL timeout in seconds")
    parser.add_argument("--max", type=int, default=None, help="Maximum number of URLs to check")
    parser.add_argument("--insecure", action="store_true", help="Disable TLS verification for lab/self-signed checks")
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"Report not found: {report_path}", file=sys.stderr)
        print("Run first: PAYTV_CHECK_WEB_LOAD=1 python3 main.py", file=sys.stderr)
        return 2
    try:
        payload = _load_report(report_path)
    except ValueError as exc:
        print(f"Cannot run web-load check: {exc}", file=sys.stderr)
        return 2

    results = payload.get("results", [])
    checker = WebAccessChecker(
        output_dir=args.output_dir,
        timeout=args.timeout,
        max_results=args.max,
        verify_tls=False if args.insecure else None,
    )
    paths = checker.check_results(results)
    print("Web-load check complete")
    for key, value in paths.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())