# Censys Platform SDK migration

- Replaced direct `requests` calls to `https://search.censys.io/api/v2/hosts/search`.
- Added lazy import of the official `censys-platform` SDK.
- Added support for `censys@PERSONAL_ACCESS_TOKEN` and `censys@ORG_ID@PERSONAL_ACCESS_TOKEN`.
- Kept defensive parsing for SDK/Pydantic response objects and multiple hit shapes.
- Added `censys-platform>=0.13.5` to `requirements.txt` and `environment.yml`.
- Updated README and credentials example to prefer Censys Platform personal access tokens.
