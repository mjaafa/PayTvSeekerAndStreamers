# PayTvSeekerAndStreamers — local credentials + cleaned engine/report flow

This cleaned legacy branch keeps the original project shape but removes the
mutual-TLS client-certificate dependency, starts with local `credentials.json`,
and adds a normalized result/report flow.

## Main changes

- Removed certificate-based client authentication from `CustomCrypto/crypto.py`.
- Removed `ssl_client_certificate` and `ssl_verify_client on` from the Nginx sample.
- Removed committed client certificates, private keys, and generated binaries.
- Added local `credentials.json` startup support.
- Cleaned the Censys, Shodan, ZoomEye, Alexa, Selenium engine, and SOCKS proxy modules.
- Fixed the Selenium engine initialization bug.
- Removed hard-coded proxy credentials.
- Disabled browser verification and local proxy usage by default.
- Added normalized result dictionaries for all active engines.
- Added per-engine status records.
- Added SQLite result persistence in `SEARCH_RESULTS`.
- Added JSON, CSV, and HTML reports in `reports/`.

## Configure credentials

The application starts in offline/local-credential mode by default.
A safe placeholder `credentials.json` is included so `python main.py` can boot
without connecting to a credential server or calling external search APIs. Edit
it locally and fill in your real `models` and `apiKey` values before expecting
Shodan/Censys/ZoomEye searches to return results.

You can regenerate it from the example at any time:

```bash
cp credentials.example.json credentials.json
```

Expected `apiKey` format:

```text
shodan@SHODAN_KEY, censys@CENSYS_PLATFORM_PAT, zoomeye@ZOOMEYE_APIKEY
```

Expected model format:

```text
cccam dreambox, TwistedWeb dreambox, vu tv, dreambox tv, vu TwistedWeb
```

Or point the app to another local/remote credential source:

```bash
export PAYTV_CREDENTIALS_FILE=/secure/path/credentials.json
# or
export PAYTV_CREDENTIALS_URL=https://example.org/credentials.json
```

No client certificate is required, and no server connection is attempted while
a usable local `credentials.json` exists. If you explicitly configure
`PAYTV_CREDENTIALS_URL`, HTTPS server certificates are verified by default.
For a lab-only self-signed endpoint, you can explicitly set:

```bash
export PAYTV_ALLOW_INSECURE_TLS=1
```

## Run

```bash
python main.py
```

With empty placeholder credentials, the app will still generate an empty report
and mark all engines as skipped.

## Result flow

Every engine now returns normalized result dictionaries with fields such as:

```json
{
  "engine": "shodan",
  "query": "dreambox tv",
  "ip": "192.0.2.10",
  "port": 443,
  "protocol": "https",
  "url": "https://192.0.2.10:443",
  "hostnames": [],
  "country": "",
  "organization": "",
  "title": "",
  "confidence": 0.5,
  "evidence": {},
  "timestamp_utc": "2026-04-27T12:00:00Z"
}
```

Legacy URL-only results are still accepted and converted automatically.

## Reports

Each run writes:

```text
reports/paytv_report_<timestamp>.json
reports/paytv_report_<timestamp>.csv
reports/paytv_report_<timestamp>.html
reports/latest.json
reports/latest.csv
reports/latest.html
```

The HTML report contains:

- execution summary
- per-engine status
- normalized result table

The JSON report contains the same information in machine-readable form.

## SQLite output

The legacy `*_STB_streamer.db` database is still created. A new table is added:

```sql
SEARCH_RESULTS (
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
```

## Optional proxy/browser behavior

The local SOCKS proxy is disabled by default:

```bash
export PAYTV_ENABLE_LOCAL_PROXY=1
```

Browser verification of returned URLs is also disabled by default:

```bash
export PAYTV_VERIFY_RESULTS_IN_BROWSER=1
```

The optional proxy helper is now imported lazily, so normal startup does not
load Linux-only VPN/proxy modules.

## Tests

The repository includes lightweight tests for result normalization and report
writing. In CI, install `pytest` and run:

```bash
pytest -q
```

Use this tool only for authorized, passive OSINT and defensive research.

## ZoomEye SDK

ZoomEye integration now uses the official `zoomeyeai` SDK from `zoomeye-ai/ZoomEye-python` instead of direct legacy `/host/search` requests. Install dependencies with:

```bash
pip install -r requirements.txt
```

The ZoomEye credential in `credentials.json` should be a current APIKEY value:

```text
zoomeye@YOUR_ZOOMEYE_APIKEY
```

Old JWT/login tokens that start with `eyJ...` may expire and are not the preferred credential for the SDK. Optional environment variables:

```bash
export ZOOMEYE_PAGE_SIZE=50
export ZOOMEYE_SUB_TYPE=all
export ZOOMEYE_FIELDS="ip,port,domain,update_time,title,service,product,device,os,country,org,asn"
export ZOOMEYE_FACETS=""
```

## Censys Platform SDK

Censys integration now uses the official `censys-platform` SDK instead of direct legacy Search API requests. Install dependencies with:

```bash
pip install -r requirements.txt
```

The Censys credential should be a Platform personal access token. Supported formats are:

```text
censys@YOUR_CENSYS_PLATFORM_PAT
censys@YOUR_CENSYS_ORG_ID@YOUR_CENSYS_PLATFORM_PAT
censys-platform@YOUR_CENSYS_PLATFORM_PAT
censys-platform@YOUR_CENSYS_ORG_ID@YOUR_CENSYS_PLATFORM_PAT
```

The old `censys@API_ID@API_SECRET` legacy Search API format is not the preferred format for the Platform SDK and may return 401/403.
