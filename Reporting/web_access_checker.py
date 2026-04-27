"""Controlled web-page load checks for normalized seeker results.

This module intentionally performs only simple web-page reachability checks for
URLs that were already returned by the OSINT engines.  It does not try default
credentials, does not submit forms, does not crawl, does not enumerate paths,
and does not interact with pages beyond fetching the reported URL.
"""

from __future__ import annotations

import csv
import html
import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse

from Engine.results import dedupe_results


TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


class WebAccessChecker:
    def __init__(
        self,
        output_dir: str = "reports",
        timeout: Optional[float] = None,
        max_results: Optional[int] = None,
        verify_tls: Optional[bool] = None,
        user_agent: Optional[str] = None,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout if timeout is not None else float(os.environ.get("PAYTV_WEB_CHECK_TIMEOUT", "6"))
        self.max_results = max_results if max_results is not None else int(os.environ.get("PAYTV_WEB_CHECK_MAX", "50"))
        if verify_tls is None:
            verify_tls = os.environ.get("PAYTV_WEB_CHECK_VERIFY_TLS", "1") != "0"
        self.verify_tls = verify_tls
        self.user_agent = user_agent or os.environ.get(
            "PAYTV_WEB_CHECK_USER_AGENT",
            "PayTvSeeker-WebLoadCheck/1.0 (+authorized-passive-check)",
        )

    def check_results(self, results: Iterable[Dict[str, Any]]) -> Dict[str, str]:
        normalized = dedupe_results(results)
        if self.max_results > 0:
            normalized = normalized[: self.max_results]
        checks = [self._check_one(item) for item in normalized if item.get("url")]
        return self.write(checks)

    def write(self, checks: List[Dict[str, Any]]) -> Dict[str, str]:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = self.output_dir / f"web_load_check_{stamp}"
        payload = {
            "summary": self._summary(checks),
            "checks": checks,
            "policy": {
                "mode": "single-url-web-page-load-only",
                "no_login": True,
                "no_form_submission": True,
                "no_crawling": True,
                "no_path_enumeration": True,
                "timeout_seconds": self.timeout,
                "max_results": self.max_results,
                "verify_tls": self.verify_tls,
            },
        }
        json_path = base.with_suffix(".json")
        csv_path = base.with_suffix(".csv")
        html_path = base.with_suffix(".html")
        latest_json = self.output_dir / "latest_web_load.json"
        latest_csv = self.output_dir / "latest_web_load.csv"
        latest_html = self.output_dir / "latest_web_load.html"
        self._write_json(json_path, payload)
        self._write_json(latest_json, payload)
        self._write_csv(csv_path, checks)
        self._write_csv(latest_csv, checks)
        self._write_html(html_path, payload)
        self._write_html(latest_html, payload)
        paths = {
            "web_json": str(json_path),
            "web_csv": str(csv_path),
            "web_html": str(html_path),
            "latest_web_html": str(latest_html),
        }
        logging.info("Web-load report written: %s", paths)
        return paths

    def _check_one(self, item: Dict[str, Any]) -> Dict[str, Any]:
        url = str(item.get("url") or "").strip()
        check = {
            "checked_at_utc": self._now(),
            "engine": item.get("engine", ""),
            "query": item.get("query", ""),
            "url": url,
            "ip": item.get("ip", ""),
            "port": item.get("port", ""),
            "protocol": item.get("protocol", ""),
            "loaded": False,
            "http_status": "",
            "final_url": "",
            "content_type": "",
            "title": "",
            "content_length": "",
            "error": "",
        }
        if not self._safe_url(url):
            check["error"] = "unsupported or malformed URL"
            return check
        try:
            import requests
        except ImportError:
            check["error"] = "requests is required for web load checks; install requirements.txt"
            return check

        headers = {"User-Agent": self.user_agent, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.5"}
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True,
                verify=self.verify_tls,
                stream=True,
            )
            body = self._read_small_text(response)
            check.update(
                {
                    "loaded": self._is_loaded(response.status_code, response.headers.get("content-type", ""), body),
                    "http_status": response.status_code,
                    "final_url": response.url,
                    "content_type": response.headers.get("content-type", ""),
                    "content_length": response.headers.get("content-length", ""),
                    "title": self._extract_title(body),
                }
            )
            response.close()
        except requests.exceptions.SSLError as err:
            check["error"] = f"TLS verification failed: {err}. For lab/self-signed checks only, set PAYTV_WEB_CHECK_VERIFY_TLS=0."
        except requests.exceptions.Timeout:
            check["error"] = f"timeout after {self.timeout}s"
        except requests.exceptions.ConnectionError as err:
            check["error"] = f"connection error: {err}"
        except requests.exceptions.RequestException as err:
            check["error"] = f"request error: {err}"
        except Exception as err:
            check["error"] = f"unexpected error: {err}"
        return check

    def _safe_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    def _read_small_text(self, response: Any, limit: int = 65536) -> str:
        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=4096, decode_unicode=True):
            if not chunk:
                continue
            chunks.append(chunk)
            total += len(chunk)
            if total >= limit:
                break
        return "".join(chunks)

    def _extract_title(self, body: str) -> str:
        match = TITLE_RE.search(body or "")
        if not match:
            return ""
        title = re.sub(r"\s+", " ", html.unescape(match.group(1))).strip()
        return title[:200]

    def _is_loaded(self, status_code: int, content_type: str, body: str) -> bool:
        return 200 <= int(status_code or 0) < 400

    def _summary(self, checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        loaded = [item for item in checks if item.get("loaded")]
        reachable_http = [item for item in checks if str(item.get("http_status") or "").strip()]
        return {
            "generated_at_utc": self._now(),
            "checked_count": len(checks),
            "loaded_count": len(loaded),
            "http_response_count": len(reachable_http),
            "error_count": len([item for item in checks if item.get("error")]),
        }

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def _write_csv(self, path: Path, checks: List[Dict[str, Any]]) -> None:
        fields = [
            "checked_at_utc",
            "engine",
            "query",
            "url",
            "loaded",
            "http_status",
            "final_url",
            "content_type",
            "title",
            "ip",
            "port",
            "protocol",
            "error",
        ]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for item in checks:
                writer.writerow({field: item.get(field, "") for field in fields})

    def _write_html(self, path: Path, payload: Dict[str, Any]) -> None:
        summary = payload.get("summary", {})
        checks = payload.get("checks", [])
        rows = []
        for item in checks:
            url = html.escape(str(item.get("url", "")))
            rows.append(
                "<tr>"
                f"<td>{html.escape(str(item.get('loaded', '')))}</td>"
                f"<td>{html.escape(str(item.get('http_status', '')))}</td>"
                f"<td><a href=\"{url}\">{url}</a></td>"
                f"<td>{html.escape(str(item.get('title', '')))}</td>"
                f"<td>{html.escape(str(item.get('content_type', '')))}</td>"
                f"<td>{html.escape(str(item.get('engine', '')))}</td>"
                f"<td>{html.escape(str(item.get('query', '')))}</td>"
                f"<td>{html.escape(str(item.get('error', '')))}</td>"
                "</tr>"
            )
        body = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>PayTV Seeker Web Load Check</title>
  <style>
    body {{ font-family: sans-serif; margin: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    th, td {{ border: 1px solid #ccc; padding: 0.4rem; vertical-align: top; }}
    th {{ background: #f4f4f4; text-align: left; }}
    code {{ background: #f4f4f4; padding: 0.1rem 0.2rem; }}
  </style>
</head>
<body>
  <h1>Web Load Check</h1>
  <p>Generated: <code>{generated}</code></p>
  <p>Checked: <strong>{checked}</strong> | Loaded: <strong>{loaded}</strong> | HTTP responses: <strong>{responses}</strong> | Errors: <strong>{errors}</strong></p>
  <p>Mode: exact returned URL only. No login, no form submission, no crawling, no path enumeration.</p>
  <table>
    <thead><tr><th>Loaded</th><th>Status</th><th>URL</th><th>Title</th><th>Content type</th><th>Engine</th><th>Query</th><th>Error</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>
""".format(
            generated=html.escape(str(summary.get("generated_at_utc", ""))),
            checked=summary.get("checked_count", 0),
            loaded=summary.get("loaded_count", 0),
            responses=summary.get("http_response_count", 0),
            errors=summary.get("error_count", 0),
            rows="".join(rows) or '<tr><td colspan="8">No URLs checked.</td></tr>',
        )
        path.write_text(body, encoding="utf-8")

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")