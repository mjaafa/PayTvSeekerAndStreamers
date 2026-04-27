"""Result reporting for the cleaned legacy seeker."""

from __future__ import annotations

import csv
import html
import json
import logging
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

from Engine.results import dedupe_results


class ReportWriter:
    def __init__(self, output_dir="reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    #def write(self, results: Iterable[Dict[str, Any]], engine_status=None) -> Dict[str, str]:
    def write(self, results, engine_status=None, related_reports=None):
        normalized = dedupe_results(results)
        engine_status = engine_status or []
        related_reports = related_reports or {}

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = self.output_dir / f"paytv_report_{stamp}"

        summary = self._summary(normalized, engine_status)
        payload = {"summary": summary, "engine_status": engine_status, "results": normalized}

        json_path = base.with_suffix(".json")
        csv_path = base.with_suffix(".csv")
        html_path = base.with_suffix(".html")
        latest_json = self.output_dir / "latest.json"
        latest_csv = self.output_dir / "latest.csv"
        latest_html = self.output_dir / "latest.html"

        self._write_json(json_path, payload)
        self._write_json(latest_json, payload)
        self._write_csv(csv_path, normalized)
        self._write_csv(latest_csv, normalized)
        self._write_html(html_path, payload)
        self._write_html(latest_html, payload)

        paths = {"json": str(json_path), "csv": str(csv_path), "html": str(html_path), "latest_html": str(latest_html)}
        logging.info("Report written: %s", paths)
        return paths

    def _summary(self, results: List[Dict[str, Any]], engine_status: List[Dict[str, Any]]) -> Dict[str, Any]:
        by_engine = Counter(item.get("engine", "unknown") for item in results)
        by_query = Counter(item.get("query", "") for item in results if item.get("query"))
        unique_targets = {(item.get("ip"), item.get("port"), item.get("protocol")) for item in results}
        return {
            "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "result_count": len(results),
            "unique_target_count": len(unique_targets),
            "by_engine": dict(by_engine),
            "by_query": dict(by_query),
            "engines_run": engine_status,
        }

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def _write_csv(self, path: Path, results: List[Dict[str, Any]]) -> None:
        fields = [
            "timestamp_utc",
            "engine",
            "query",
            "url",
            "ip",
            "port",
            "protocol",
            "hostnames",
            "country",
            "organization",
            "title",
            "confidence",
        ]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for item in results:
                row = {field: item.get(field, "") for field in fields}
                if isinstance(row.get("hostnames"), list):
                    row["hostnames"] = ";".join(row["hostnames"])
                writer.writerow(row)

    def _write_html(self, path: Path, payload: Dict[str, Any]) -> None:
        summary = payload["summary"]
        results = payload["results"]
        statuses = payload.get("engine_status", [])
        rows = []
        for item in results:
            url = html.escape(str(item.get("url", "")))
            rows.append(
                "<tr>"
                f"<td>{html.escape(str(item.get('engine', '')))}</td>"
                f"<td>{html.escape(str(item.get('query', '')))}</td>"
                f"<td><a href=\"{url}\">{url}</a></td>"
                f"<td>{html.escape(str(item.get('ip', '')))}</td>"
                f"<td>{html.escape(str(item.get('port', '')))}</td>"
                f"<td>{html.escape(str(item.get('country', '')))}</td>"
                f"<td>{html.escape(str(item.get('organization', '')))}</td>"
                f"<td>{html.escape(str(item.get('confidence', '')))}</td>"
                "</tr>"
            )
        status_rows = []
        for item in statuses:
            status_rows.append(
                "<tr>"
                f"<td>{html.escape(str(item.get('engine', '')))}</td>"
                f"<td>{html.escape(str(item.get('status', '')))}</td>"
                f"<td>{html.escape(str(item.get('result_count', '')))}</td>"
                f"<td>{html.escape(str(item.get('error', '')))}</td>"
                "</tr>"
            )

        no_status = '<tr><td colspan="4">No engines recorded.</td></tr>'
        no_results = '<tr><td colspan="8">No results.</td></tr>'
        body = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>PayTV Seeker Report</title>
  <style>
    body {{ font-family: sans-serif; margin: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    th, td {{ border: 1px solid #ccc; padding: 0.4rem; vertical-align: top; }}
    th {{ background: #f4f4f4; text-align: left; }}
    code {{ background: #f4f4f4; padding: 0.1rem 0.2rem; }}
  </style>
</head>
<body>
  <h1>PayTV Seeker Report</h1>
  <p>Generated: <code>{generated}</code></p>
  <p>Results: <strong>{result_count}</strong> | Unique targets: <strong>{unique_target_count}</strong></p>

  <h2>Engine status</h2>
  <table>
    <thead><tr><th>Engine</th><th>Status</th><th>Results</th><th>Error</th></tr></thead>
    <tbody>{status_rows}</tbody>
  </table>

  <h2>Results</h2>
  <table>
    <thead><tr><th>Engine</th><th>Query</th><th>URL</th><th>IP</th><th>Port</th><th>Country</th><th>Organization</th><th>Confidence</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>
""".format(
            generated=html.escape(str(summary.get("generated_at_utc"))),
            result_count=summary.get("result_count"),
            unique_target_count=summary.get("unique_target_count"),
            status_rows="".join(status_rows) or no_status,
            rows="".join(rows) or no_results,
        )
        path.write_text(body, encoding="utf-8")
