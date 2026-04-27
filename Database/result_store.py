"""SQLite result persistence for normalized engine outputs."""

from __future__ import annotations

import json
import logging
import sqlite3
from typing import Any, Dict, Iterable

from Engine.results import dedupe_results


class ResultStore:
    def __init__(self, database_name):
        self.database_name = database_name
        self._init_schema()

    def _init_schema(self):
        with sqlite3.connect(self.database_name) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS SEARCH_RESULTS (
                    URL TEXT PRIMARY KEY,
                    ENGINE TEXT,
                    QUERY TEXT,
                    IP_ADDRESS TEXT,
                    PORT INTEGER,
                    PROTOCOL TEXT,
                    HOSTNAMES TEXT,
                    COUNTRY TEXT,
                    ORGANIZATION TEXT,
                    TITLE TEXT,
                    CONFIDENCE REAL,
                    EVIDENCE_JSON TEXT,
                    FIRST_SEEN_UTC TEXT,
                    LAST_SEEN_UTC TEXT
                )
                """
            )
            conn.commit()

    def upsert_many(self, results: Iterable[Dict[str, Any]]) -> int:
        normalized = dedupe_results(results)
        if not normalized:
            logging.info("No normalized results to store")
            return 0
        with sqlite3.connect(self.database_name) as conn:
            for item in normalized:
                url = item.get("url", "")
                if not url:
                    continue
                hostnames = item.get("hostnames") or []
                evidence = item.get("evidence") or {}
                timestamp = item.get("timestamp_utc") or ""
                conn.execute(
                    """
                    INSERT INTO SEARCH_RESULTS (
                        URL, ENGINE, QUERY, IP_ADDRESS, PORT, PROTOCOL, HOSTNAMES,
                        COUNTRY, ORGANIZATION, TITLE, CONFIDENCE, EVIDENCE_JSON,
                        FIRST_SEEN_UTC, LAST_SEEN_UTC
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(URL) DO UPDATE SET
                        ENGINE = excluded.ENGINE,
                        QUERY = excluded.QUERY,
                        IP_ADDRESS = excluded.IP_ADDRESS,
                        PORT = excluded.PORT,
                        PROTOCOL = excluded.PROTOCOL,
                        HOSTNAMES = excluded.HOSTNAMES,
                        COUNTRY = excluded.COUNTRY,
                        ORGANIZATION = excluded.ORGANIZATION,
                        TITLE = excluded.TITLE,
                        CONFIDENCE = excluded.CONFIDENCE,
                        EVIDENCE_JSON = excluded.EVIDENCE_JSON,
                        LAST_SEEN_UTC = excluded.LAST_SEEN_UTC
                    """,
                    (
                        url,
                        item.get("engine", ""),
                        item.get("query", ""),
                        item.get("ip", ""),
                        item.get("port", 0),
                        item.get("protocol", ""),
                        ";".join(hostnames) if isinstance(hostnames, list) else str(hostnames),
                        item.get("country", ""),
                        item.get("organization", ""),
                        item.get("title", ""),
                        item.get("confidence", 0.0),
                        json.dumps(evidence, sort_keys=True),
                        timestamp,
                        timestamp,
                    ),
                )
            conn.commit()
        logging.info("Stored %d normalized result(s) in %s", len(normalized), self.database_name)
        return len(normalized)
