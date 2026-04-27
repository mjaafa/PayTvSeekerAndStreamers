import logging
import os
from typing import Any, Dict, Iterable, List, Optional

from Engine.common import confidence_score, parse_api_bundle, split_keywords
from Engine.results import normalized_result


class zoomeye:
    """ZoomEye search engine backed by the official zoomeye-ai SDK.

    The project previously called ZoomEye with hand-written requests against the
    legacy /host/search endpoint.  ZoomEye's current official Python package is
    ``zoomeyeai`` and exposes ``zoomeyeai.sdk.ZoomEye`` with an APIKEY based
    ``search()`` method.  The SDK is imported lazily so the application can still
    start when ZoomEye is not configured or the optional dependency is missing.
    """

    name = "zoomeye"
    DEFAULT_FIELDS = "ip,port,domain,update_time,title,service,product,device,os,country,subdivisions,city,org,asn"

    def __init__(self, __api_key__, __models__, __engine__=None, limit=50):
        logging.info("ZoomEye SDK engine initialized")
        keys = parse_api_bundle(__api_key__)
        values = keys.get("zoomeye", [])
        self.api_key = values[0] if values else ""
        self.api_keywords = split_keywords(__models__)
        self.searchEngineProxy = __engine__
        self.limit = int(os.environ.get("ZOOMEYE_PAGE_SIZE", limit or 50))
        self.sub_type = os.environ.get("ZOOMEYE_SUB_TYPE", "all").strip() or "all"
        self.fields = os.environ.get("ZOOMEYE_FIELDS", self.DEFAULT_FIELDS).strip()
        self.facets = os.environ.get("ZOOMEYE_FACETS", "").strip()
        self._sdk_client = None
        self.last_status = {"engine": self.name, "status": "created", "result_count": 0, "error": ""}

    def _get_sdk_client(self):
        if self._sdk_client is not None:
            return self._sdk_client
        try:
            from zoomeyeai.sdk import ZoomEye  # type: ignore
        except ImportError as err:
            raise RuntimeError(
                "ZoomEye SDK is not installed. Install it with: "
                "pip install zoomeyeai  # or: pip install git+https://github.com/zoomeye-ai/ZoomEye-python"
            ) from err
        self._sdk_client = ZoomEye(api_key=self.api_key)
        return self._sdk_client

    def _query(self, keyword: str) -> Dict[str, Any]:
        client = self._get_sdk_client()
        page_size = max(1, min(int(self.limit or 50), 10000))
        try:
            payload = client.search(
                keyword,
                page=1,
                pagesize=page_size,
                sub_type=self.sub_type,
                fields=self.fields,
                facets=self.facets,
            )
        except ValueError as err:
            raise RuntimeError(self._format_sdk_error(err)) from err
        except Exception as err:
            raise RuntimeError(f"ZoomEye SDK search failed: {err}") from err
        if payload is None:
            return {}
        if not isinstance(payload, dict):
            raise RuntimeError(f"ZoomEye SDK returned unexpected payload type: {type(payload).__name__}")
        return payload

    def _extract_results(self, keyword: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        matches = self._extract_matches(payload)
        for item in matches[: self.limit]:
            if not isinstance(item, dict):
                logging.debug("Skipping non-dict ZoomEye result: %r", item)
                continue
            ip = self._first_nonempty(item, "ip", "ip_str", "host", "address")
            if not ip:
                continue
            port = self._port(item)
            service = self._service(item)
            protocol = self._protocol(service, port)
            title = self._first_nonempty(item, "title", "web_title", "name")
            banner = self._first_nonempty(item, "banner", "description", "http_body", "headers")
            geoinfo = self._dict_from_any(
                item.get("geoinfo")
                or item.get("geo_info")
                or item.get("aiweninfo")
                or item.get("ipipinfo")
                or item.get("location")
            )
            domain = self._first_nonempty(item, "domain", "site")
            hostnames = self._hostnames(item)
            if domain and domain not in hostnames:
                hostnames.append(domain)

            results.append(
                normalized_result(
                    engine=self.name,
                    query=keyword,
                    ip=ip,
                    port=port,
                    protocol=protocol,
                    hostnames=hostnames,
                    country=geoinfo.get("country") or geoinfo.get("country_code") or item.get("country") or "",
                    organization=self._first_nonempty(item, "organization", "org", "isp"),
                    title=title,
                    banner=banner,
                    evidence={
                        "source": "zoomeye-sdk",
                        "service": service,
                        "product": self._first_nonempty(item, "product", "app"),
                        "device": self._first_nonempty(item, "device"),
                        "os": self._first_nonempty(item, "os"),
                        "asn": self._first_nonempty(item, "asn"),
                        "update_time": self._first_nonempty(item, "update_time", "timestamp", "time"),
                    },
                    confidence=confidence_score(title, banner, service),
                )
            )
        return results

    def _extract_matches(self, payload: Dict[str, Any]) -> List[Any]:
        """Normalize likely ZoomEye SDK/API response shapes to a list.

        API v2 generally returns a top-level dict containing a ``data`` member;
        older/alternate client versions may return ``matches`` or ``results`` at
        the top level.  This method intentionally accepts all of those shapes.
        """
        if not isinstance(payload, dict):
            logging.warning("ZoomEye returned unexpected top-level JSON type: %s", type(payload).__name__)
            return []

        candidates = [payload.get("data"), payload.get("matches"), payload.get("results")]
        for candidate in candidates:
            matches = self._matches_from_candidate(candidate)
            if matches is not None:
                return matches
        logging.warning("ZoomEye SDK response had no parseable result list; keys=%s", sorted(payload.keys()))
        return []

    def _matches_from_candidate(self, candidate: Any) -> Optional[List[Any]]:
        if isinstance(candidate, list):
            return candidate
        if isinstance(candidate, dict):
            for key in ("matches", "results", "items", "data", "list"):
                value = candidate.get(key)
                if isinstance(value, list):
                    return value
            # Some field-filtered responses may expose a single asset-like dict.
            if any(k in candidate for k in ("ip", "domain", "port", "service")):
                return [candidate]
        return None

    def search(self):
        if not self.api_key:
            return self._skip("ZoomEye API key is missing")
        if self.api_key.startswith("eyJ"):
            logging.warning(
                "ZoomEye credential looks like an old JWT/login token. The official zoomeyeai SDK expects a current APIKEY."
            )
        if not self.api_keywords:
            return self._skip("ZoomEye API key configured, but no model queries are configured")

        all_results = []
        seen = set()
        errors = []
        for keyword in self.api_keywords:
            logging.info("Searching ZoomEye via SDK for keyword: %s", keyword)
            try:
                payload = self._query(keyword)
                extracted = self._extract_results(keyword, payload)
                for item in extracted:
                    key = (item["engine"], item["query"], item["url"])
                    if key not in seen:
                        seen.add(key)
                        all_results.append(item)
                logging.info("ZoomEye SDK query %r produced %d normalized result(s)", keyword, len(extracted))
            except Exception as err:
                message = f"{keyword}: {err}"
                errors.append(message)
                logging.error("ZoomEye SDK query failed for %r: %s", keyword, err)
        self.last_status = {
            "engine": self.name,
            "status": "ok" if not errors else "partial_error",
            "result_count": len(all_results),
            "error": "; ".join(errors[:3]),
        }
        logging.info("ZoomEye returned %d unique result(s)", len(all_results))
        return all_results

    def _port(self, item: Dict[str, Any]) -> int:
        portinfo = self._dict_from_any(item.get("portinfo") or item.get("port_info"))
        value = portinfo.get("port") or item.get("port") or item.get("service_port") or 80
        try:
            return int(value)
        except Exception:
            return 80

    def _service(self, item: Dict[str, Any]) -> str:
        portinfo = self._dict_from_any(item.get("portinfo") or item.get("port_info"))
        return str(
            portinfo.get("service")
            or portinfo.get("app")
            or item.get("service")
            or item.get("protocol")
            or item.get("app")
            or ""
        ).lower()

    def _protocol(self, service: str, port: int) -> str:
        if service in {"https", "ssl", "tls"} or port in {443, 8443}:
            return "https"
        return "http"

    def _hostnames(self, item: Dict[str, Any]) -> List[str]:
        hostnames = item.get("domains") or item.get("hostnames") or item.get("hostname") or []
        if isinstance(hostnames, str):
            hostnames = [hostnames]
        if not isinstance(hostnames, Iterable):
            return []
        return [str(value) for value in hostnames if str(value).strip()]

    def _skip(self, reason):
        logging.warning("%s; skipping ZoomEye search", reason)
        self.last_status = {"engine": self.name, "status": "skipped", "result_count": 0, "error": reason}
        return []

    def _format_sdk_error(self, err: Exception) -> str:
        detail = str(err)
        lower = detail.lower()
        if "apikey" in lower or "api-key" in lower or "api key" in lower or "authentication" in lower or "unauthorized" in lower:
            return f"ZoomEye SDK authentication failed: {detail}. Use a current ZoomEye APIKEY, not an expired JWT/login token."
        if "forbidden" in lower or "403" in lower:
            return f"ZoomEye SDK authorization failed: {detail}. Check account permissions/quota and APIKEY validity."
        return f"ZoomEye SDK error: {detail}"

    def _first_nonempty(self, item: Dict[str, Any], *keys: str) -> str:
        for key in keys:
            value = item.get(key)
            if value is None:
                continue
            if isinstance(value, (list, tuple)):
                value = value[0] if value else ""
            if isinstance(value, dict):
                continue
            text = str(value).strip()
            if text:
                return text
        return ""

    def _dict_from_any(self, value: Any) -> Dict[str, Any]:
        return value if isinstance(value, dict) else {}
