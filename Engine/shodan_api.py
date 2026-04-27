import logging

from Engine.common import confidence_score, is_real_secret, parse_api_bundle, split_keywords
from Engine.results import normalized_result


def _load_shodan():
    try:
        import shodan
    except ImportError as err:
        raise RuntimeError(
            "The shodan Python package is required only when a Shodan API key is configured. "
            "Install requirements.txt or remove the Shodan key."
        ) from err
    return shodan


class shodan_api:
    name = "shodan"

    def __init__(self, __api_key__, __models__, limit=100):
        logging.info("Shodan API engine initialized")
        keys = parse_api_bundle(__api_key__)
        values = keys.get("shodan", [])
        raw_key = str(__api_key__ or "").strip()
        self.api_key = values[0] if values else (raw_key if is_real_secret(raw_key) and "@" not in raw_key else "")
        self.keywords = split_keywords(__models__)
        self.limit = limit
        self.api = None
        self.last_status = {"engine": self.name, "status": "created", "result_count": 0, "error": ""}

    def search(self):
        if not self.api_key:
            return self._skip("Shodan API key is missing")
        if not self.keywords:
            return self._skip("Shodan API key configured, but no model queries are configured")
        if self.api is None:
            self.api = _load_shodan().Shodan(self.api_key)

        results = []
        seen = set()
        errors = []
        for keyword in self.keywords:
            logging.info("Searching Shodan for keyword: %s", keyword)
            try:
                payload = self.api.search(keyword, limit=self.limit)
            except Exception as err:
                message = f"{keyword}: {err}"
                errors.append(message)
                logging.error("Shodan query failed for %r: %s", keyword, err)
                continue

            for match in payload.get("matches", []):
                item = self._result_from_match(keyword, match)
                if not item:
                    continue
                key = (item["engine"], item["query"], item["url"])
                if key not in seen:
                    seen.add(key)
                    results.append(item)

        self.last_status = {
            "engine": self.name,
            "status": "ok" if not errors else "partial_error",
            "result_count": len(results),
            "error": "; ".join(errors[:3]),
        }
        logging.info("Shodan returned %d unique result(s)", len(results))
        return results

    def _result_from_match(self, keyword, match):
        ip = match.get("ip_str") or match.get("ip")
        if not ip:
            return None
        port = match.get("port", 80)
        ssl_enabled = bool(match.get("ssl"))
        protocol = "https" if ssl_enabled or int(port or 0) in {443, 8443} else "http"
        http_data = match.get("http") or {}
        location = match.get("location") or {}
        hostnames = match.get("hostnames") or []
        title = http_data.get("title") or match.get("title") or ""
        data = match.get("data") or ""
        organization = match.get("org") or match.get("isp") or ""
        return normalized_result(
            engine=self.name,
            query=keyword,
            ip=ip,
            port=port,
            protocol=protocol,
            hostnames=hostnames,
            country=location.get("country_code") or location.get("country_name") or "",
            organization=organization,
            title=title,
            banner=data,
            evidence={
                "source": "shodan",
                "transport": match.get("transport", ""),
                "product": match.get("product", ""),
                "version": match.get("version", ""),
            },
            confidence=confidence_score(title, data),
        )

    def _skip(self, reason):
        logging.warning("%s; skipping Shodan search", reason)
        self.last_status = {"engine": self.name, "status": "skipped", "result_count": 0, "error": reason}
        return []
