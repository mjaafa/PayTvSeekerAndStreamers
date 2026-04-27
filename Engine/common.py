import logging
from typing import Dict, List

from Engine.results import build_url


_PLACEHOLDER_PREFIXES = (
    "YOUR_",
    "CHANGE_ME",
    "CHANGE-ME",
    "REPLACE_ME",
    "REPLACE-ME",
    "EXAMPLE",
)


def is_real_secret(value) -> bool:
    """Return True only for non-empty, non-placeholder credential values."""
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="ignore")
    value = str(value or "").strip()
    if not value:
        return False
    upper_value = value.upper()
    if upper_value in {"NONE", "NULL", "TODO", "TBD", "N/A"}:
        return False
    return not any(upper_value.startswith(prefix) for prefix in _PLACEHOLDER_PREFIXES)


def parse_api_bundle(api_bundle) -> Dict[str, List[str]]:
    """Parse legacy apiKey strings like 'shodan@KEY, censys@ID@SECRET'."""
    if isinstance(api_bundle, bytes):
        api_bundle = api_bundle.decode("utf-8", errors="ignore")
    result = {}
    for part in str(api_bundle or "").split(","):
        part = part.strip()
        if not part or "@" not in part:
            continue
        pieces = [piece.strip() for piece in part.split("@")]
        name = pieces[0].lower()
        values = [piece for piece in pieces[1:] if is_real_secret(piece)]
        if values:
            result[name] = values
    return result


def split_keywords(keywords) -> List[str]:
    if isinstance(keywords, bytes):
        keywords = keywords.decode("utf-8", errors="ignore")
    return [item.strip() for item in str(keywords or "").split(",") if item.strip()]


def result_url(ip: str, port, protocol=None) -> str:
    return build_url(ip, port, protocol)


def log_engine_error(engine_name: str, err: Exception):
    logging.error("%s engine error: %s", engine_name, err)
