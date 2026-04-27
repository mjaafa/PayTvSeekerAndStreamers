"""Normalized search result helpers used by all engines.

The legacy project originally passed bare URLs between engines and the seeker.
These helpers keep that behavior compatible while adding structured metadata for
storage and reports.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple


Result = Dict[str, Any]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def infer_protocol(port: Any, explicit: Optional[str] = None) -> str:
    if explicit:
        explicit = str(explicit).lower().strip()
        if explicit in {"http", "https"}:
            return explicit
    try:
        port_int = int(port)
    except Exception:
        port_int = 80
    return "https" if port_int in {443, 8443} else "http"


def build_url(ip: str, port: Any = 80, protocol: Optional[str] = None) -> str:
    try:
        port_int = int(port)
    except Exception:
        port_int = 80
    scheme = infer_protocol(port_int, protocol)
    return f"{scheme}://{ip}:{port_int}"


def normalized_result(
    *,
    engine: str,
    query: str,
    ip: str,
    port: Any = 80,
    protocol: Optional[str] = None,
    url: Optional[str] = None,
    hostnames: Optional[Iterable[str]] = None,
    country: Optional[str] = None,
    organization: Optional[str] = None,
    title: Optional[str] = None,
    banner: Optional[str] = None,
    evidence: Optional[Dict[str, Any]] = None,
    confidence: float = 0.5,
) -> Result:
    """Build a stable, report-friendly result dictionary."""
    ip = str(ip or "").strip()
    try:
        port_int = int(port)
    except Exception:
        port_int = 80
    protocol_value = infer_protocol(port_int, protocol)
    url_value = url or build_url(ip, port_int, protocol_value)
    hostnames_list = [str(item) for item in (hostnames or []) if str(item).strip()]

    result = {
        "engine": str(engine or "unknown"),
        "query": str(query or ""),
        "ip": ip,
        "port": port_int,
        "protocol": protocol_value,
        "url": url_value,
        "hostnames": hostnames_list,
        "country": country or "",
        "organization": organization or "",
        "title": title or "",
        "banner": _truncate(banner or "", 500),
        "confidence": float(confidence),
        "evidence": evidence or {},
        "timestamp_utc": utc_now_iso(),
    }
    return result


def normalize_legacy_result(item: Any, engine: str = "legacy", query: str = "") -> Result:
    """Accept either a new result dict or an old string URL."""
    if isinstance(item, dict):
        normalized = dict(item)
        normalized.setdefault("engine", engine)
        normalized.setdefault("query", query)
        normalized.setdefault("url", "")
        normalized.setdefault("timestamp_utc", utc_now_iso())
        normalized.setdefault("evidence", {})
        normalized.setdefault("confidence", 0.5)
        return normalized

    url = str(item or "").strip()
    protocol, ip, port = parse_url(url)
    return normalized_result(
        engine=engine,
        query=query,
        ip=ip,
        port=port,
        protocol=protocol,
        url=url,
        confidence=0.3,
        evidence={"legacy_url_only": True},
    )


def dedupe_results(results: Iterable[Any]) -> List[Result]:
    """Deduplicate by engine/query/url while preserving order."""
    seen = set()
    output: List[Result] = []
    for raw in results or []:
        item = normalize_legacy_result(raw)
        key = (
            str(item.get("engine", "")),
            str(item.get("query", "")),
            str(item.get("url", "")),
        )
        if not item.get("url") or key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def result_key(item: Result) -> Tuple[str, str, int]:
    return (str(item.get("ip", "")), str(item.get("protocol", "")), int(item.get("port") or 0))


def parse_url(url: str) -> Tuple[str, str, int]:
    protocol = "http"
    rest = str(url or "").strip()
    if "://" in rest:
        protocol, rest = rest.split("://", 1)
    rest = rest.split("/", 1)[0]
    if ":" in rest:
        ip, port_text = rest.rsplit(":", 1)
        try:
            port = int(port_text)
        except Exception:
            port = 443 if protocol == "https" else 80
    else:
        ip = rest
        port = 443 if protocol == "https" else 80
    return protocol, ip, port


def _truncate(value: str, limit: int) -> str:
    value = str(value or "")
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."
