import logging
from typing import Any, Dict, Iterable, List, Optional, Tuple

from Engine.common import confidence_score, parse_api_bundle, split_keywords
from Engine.results import normalized_result


class censys:
    """Censys Platform engine using the official ``censys-platform`` SDK.

    Supported credential formats in ``credentials.json``:

    - ``censys@PERSONAL_ACCESS_TOKEN``
    - ``censys@ORGANIZATION_ID@PERSONAL_ACCESS_TOKEN``
    - ``censys-platform@PERSONAL_ACCESS_TOKEN``
    - ``censys-platform@ORGANIZATION_ID@PERSONAL_ACCESS_TOKEN``

    The old legacy format ``censys@API_ID@API_SECRET`` is no longer a good fit
    for the Platform SDK.  If such credentials are used, the SDK will likely
    return 401/403 until the value is replaced with a Platform personal access
    token.
    """

    name = "censys"

    def __init__(self, __api_key__, __models__, __engine__=None, limit=50):
        logging.info("Censys Platform SDK engine initialized")
        keys = parse_api_bundle(__api_key__)
        values = keys.get("censys-platform") or keys.get("censys") or []
        self.organization_id, self.personal_access_token = self._parse_platform_credentials(values)
        self.api_keywords = split_keywords(__models__)
        self.searchEngineProxy = __engine__
        self.limit = int(limit or 50)
        self.last_status = {"engine": self.name, "status": "created", "result_count": 0, "error": ""}

    def _parse_platform_credentials(self, values: List[str]) -> Tuple[str, str]:
        if not values:
            return "", ""
        if len(values) == 1:
            return "", values[0]
        # Platform SDK uses an optional organization_id plus a bearer-style
        # personal access token.  This also keeps compatibility with the old
        # comma-separated apiKey string format.
        return values[0], values[1]

    def _import_sdk(self):
        try:
            from censys_platform import SDK  # type: ignore
        except ImportError as err:
            raise RuntimeError(
                "The censys-platform Python package is required for the Censys engine. "
                "Install it with: pip install censys-platform"
            ) from err
        return SDK

    def _query(self, keyword: str) -> Dict[str, Any]:
        SDK = self._import_sdk()
        fields = [
            "host.ip",
            "host.names",
            "host.location.country",
            "host.location.country_code",
            "host.autonomous_system.name",
            "host.autonomous_system.organization",
            "host.services.port",
            "host.services.protocol",
            "host.services.service_name",
            "host.services.transport_protocol",
            "host.services.observed_at",
            "host.services.http.response.html_title",
        ]
        body = {
            "query": keyword,
            "page_size": self.limit,
            "fields": fields,
        }
        sdk_kwargs = {"personal_access_token": self.personal_access_token}
        if self.organization_id:
            sdk_kwargs["organization_id"] = self.organization_id

        try:
            with SDK(**sdk_kwargs) as sdk:
                response = sdk.global_data.search(search_query_input_body=body)
        except Exception as err:
            raise RuntimeError(self._format_sdk_error(err)) from err

        return self._to_plain(response)

    def _extract_results(self, keyword: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        hits = self._extract_hits(payload)
        for hit in hits:
            hit = self._coerce_hit(hit)
            if not hit:
                continue
            host = self._extract_host(hit)
            ip = self._hit_ip(hit, host)
            if not ip:
                continue
            services = self._hit_services(hit, host)
            if not services:
                services = [{"port": 443, "service_name": "HTTP", "protocol": "HTTPS"}, {"port": 80, "service_name": "HTTP"}]
            for service in services:
                service = self._coerce_service(service)
                if not service:
                    continue
                try:
                    port = int(service.get("port") or service.get("web.port") or 443)
                except Exception:
                    port = 443
                service_name = str(
                    service.get("service_name")
                    or service.get("name")
                    or service.get("protocol")
                    or service.get("web.service_name")
                    or ""
                ).lower()
                extended_name = str(
                    service.get("extended_service_name")
                    or service.get("extended_name")
                    or service.get("protocol")
                    or service.get("web.protocol")
                    or ""
                ).lower()
                protocol = "https" if "https" in extended_name or service_name == "https" or port in {443, 8443} else "http"
                title = self._service_title(service)
                location = self._as_dict(host.get("location")) or self._as_dict(hit.get("location"))
                autonomous_system = self._as_dict(host.get("autonomous_system")) or self._as_dict(hit.get("autonomous_system"))
                results.append(
                    normalized_result(
                        engine=self.name,
                        query=keyword,
                        ip=ip,
                        port=port,
                        protocol=protocol,
                        hostnames=self._hit_hostnames(hit, host),
                        country=location.get("country") or location.get("country_code") or "",
                        organization=autonomous_system.get("name") or autonomous_system.get("organization") or "",
                        title=title,
                        evidence={
                            "source": "censys-platform-sdk",
                            "service_name": service_name,
                            "extended_service_name": extended_name,
                            "transport_protocol": service.get("transport_protocol", ""),
                            "observed_at": service.get("observed_at", ""),
                        },
                        confidence=confidence_score(title, service_name, extended_name),
                    )
                )
        return results

    def _extract_hits(self, payload: Dict[str, Any]) -> List[Any]:
        if not isinstance(payload, dict):
            return []
        candidates: List[Any] = []
        candidates.append(payload.get("hits"))
        candidates.append(payload.get("data"))
        result_obj = payload.get("result")
        candidates.append(result_obj)
        if isinstance(result_obj, dict):
            candidates.append(result_obj.get("hits"))
            nested_result = result_obj.get("result")
            candidates.append(nested_result)
            if isinstance(nested_result, dict):
                candidates.append(nested_result.get("hits"))
                candidates.append(nested_result.get("data"))
        for candidate in candidates:
            if isinstance(candidate, list):
                return candidate
            if isinstance(candidate, dict):
                nested = candidate.get("hits") or candidate.get("results") or candidate.get("data")
                if isinstance(nested, list):
                    return nested
        logging.warning("Censys Platform response had no parseable hits list")
        return []

    def _coerce_hit(self, value: Any) -> Dict[str, Any]:
        value = self._to_plain(value)
        if isinstance(value, dict):
            return value
        if isinstance(value, str) and value.strip():
            return {"ip": value.strip()}
        logging.debug("Skipping non-dict Censys hit: %r", value)
        return {}

    def _coerce_service(self, value: Any) -> Dict[str, Any]:
        value = self._to_plain(value)
        if isinstance(value, dict):
            return value
        if isinstance(value, str) and value.strip():
            return {"service_name": value.strip()}
        logging.debug("Skipping non-dict Censys service: %r", value)
        return {}

    def _extract_host(self, hit: Dict[str, Any]) -> Dict[str, Any]:
        host = self._as_dict(hit.get("host"))
        if host:
            return host
        # Some SDK/pydantic serializations flatten selected fields as keys.
        rebuilt: Dict[str, Any] = {}
        for key, value in hit.items():
            if isinstance(key, str) and key.startswith("host."):
                self._set_dotted(rebuilt, key[5:], value)
        return rebuilt

    def _hit_ip(self, hit: Dict[str, Any], host: Optional[Dict[str, Any]] = None) -> str:
        host = host or self._as_dict(hit.get("host"))
        return str(
            hit.get("ip")
            or hit.get("host.ip")
            or host.get("ip")
            or hit.get("ip_str")
            or ""
        ).strip()

    def _hit_hostnames(self, hit: Dict[str, Any], host: Optional[Dict[str, Any]] = None) -> List[str]:
        host = host or self._as_dict(hit.get("host"))
        names = host.get("names") or hit.get("names") or hit.get("host.names") or hit.get("hostnames") or []
        if isinstance(names, str):
            names = [names]
        elif not isinstance(names, Iterable):
            names = []
        name = hit.get("name") or host.get("name")
        output = [str(item) for item in names if str(item).strip()]
        if name and str(name) not in output:
            output.append(str(name))
        return output

    def _hit_services(self, hit: Dict[str, Any], host: Optional[Dict[str, Any]] = None) -> List[Any]:
        host = host or self._as_dict(hit.get("host"))
        services = (
            host.get("services")
            or hit.get("services")
            or hit.get("host.services")
            or hit.get("matched_services")
            or []
        )
        if isinstance(services, dict):
            return [services]
        if isinstance(services, list):
            return services
        if isinstance(services, str) and services.strip():
            return [services]
        return []

    def _service_title(self, service: Dict[str, Any]) -> str:
        http_data = self._as_dict(service.get("http"))
        response_data = self._as_dict(http_data.get("response"))
        return str(
            response_data.get("html_title")
            or response_data.get("title")
            or service.get("http.response.html_title")
            or service.get("title")
            or ""
        )

    def search(self):
        if not self.personal_access_token:
            return self._skip("Censys Platform personal access token is missing")
        if not self.api_keywords:
            return self._skip("Censys credentials configured, but no model queries are configured")

        all_results = []
        seen = set()
        errors = []
        for keyword in self.api_keywords:
            logging.info("Searching Censys Platform for keyword: %s", keyword)
            try:
                payload = self._query(keyword)
                extracted = self._extract_results(keyword, payload)
                for item in extracted:
                    key = (item["engine"], item["query"], item["url"])
                    if key not in seen:
                        seen.add(key)
                        all_results.append(item)
                logging.info("Censys Platform query %r produced %d normalized result(s)", keyword, len(extracted))
            except Exception as err:
                message = f"{keyword}: {err}"
                errors.append(message)
                logging.error("Censys Platform query failed for %r: %s", keyword, err)
        self.last_status = {
            "engine": self.name,
            "status": "ok" if not errors else "partial_error",
            "result_count": len(all_results),
            "error": "; ".join(errors[:3]),
        }
        logging.info("Censys Platform returned %d unique result(s)", len(all_results))
        return all_results

    def _skip(self, reason):
        logging.warning("%s; skipping Censys search", reason)
        self.last_status = {"engine": self.name, "status": "skipped", "result_count": 0, "error": reason}
        return []

    def _format_sdk_error(self, err: Exception) -> str:
        status_code = getattr(err, "status_code", None)
        body = getattr(err, "body", "") or getattr(err, "message", "") or str(err)
        body_text = str(body)[:400]
        if status_code in {401, 403}:
            hint = "Censys Platform authentication/authorization failed"
            if self.organization_id and len(self.organization_id) == 36:
                hint += ". Check that the second censys@... value is a Platform personal access token, not a legacy API secret"
            return f"{hint} with HTTP {status_code}: {body_text}"
        if status_code:
            return f"Censys Platform SDK HTTP {status_code}: {body_text}"
        return f"Censys Platform SDK error: {body_text}"

    @staticmethod
    def _as_dict(value):
        value = censys._to_plain(value)
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _set_dotted(target: Dict[str, Any], dotted_key: str, value: Any) -> None:
        parts = [part for part in str(dotted_key).split(".") if part]
        cursor = target
        for part in parts[:-1]:
            next_value = cursor.get(part)
            if not isinstance(next_value, dict):
                next_value = {}
                cursor[part] = next_value
            cursor = next_value
        if parts:
            cursor[parts[-1]] = value

    @staticmethod
    def _to_plain(value: Any) -> Any:
        """Convert SDK/Pydantic response objects into ordinary Python data."""
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, list):
            return [censys._to_plain(item) for item in value]
        if isinstance(value, tuple):
            return [censys._to_plain(item) for item in value]
        if isinstance(value, dict):
            return {key: censys._to_plain(item) for key, item in value.items()}
        for method_name in ("model_dump", "dict", "to_dict"):
            method = getattr(value, method_name, None)
            if callable(method):
                try:
                    return censys._to_plain(method())
                except TypeError:
                    try:
                        return censys._to_plain(method(exclude_none=True))
                    except Exception:
                        pass
                except Exception:
                    pass
        if hasattr(value, "__dict__"):
            return {key: censys._to_plain(item) for key, item in vars(value).items() if not key.startswith("_")}
        return value
