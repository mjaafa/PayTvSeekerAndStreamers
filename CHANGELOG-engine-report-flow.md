# Engine cleanup and result/report flow changes

## Engine interface

- Added normalized result dictionaries for all active engines.
- Kept compatibility with the legacy URL-only flow.
- Added per-engine `last_status` records with `ok`, `skipped`, `partial_error`, or `error` states.
- Moved the optional SOCKS/VPN proxy import out of startup and into `configureProxy()` so normal offline execution does not import Linux-only proxy helpers.
- Added basic confidence scoring from passive fingerprints such as `dreambox`, `TwistedWeb`, `OpenWebIF`, `CCcam`, and `Enigma2`.

## Result storage

- Added `Database/result_store.py`.
- Added a new `SEARCH_RESULTS` table inside the existing `*_STB_streamer.db` database.
- Results are upserted by URL and retain first/last seen timestamps.

## Reports

- Added `Reporting/report_writer.py`.
- Every run now creates:
  - `reports/paytv_report_<timestamp>.json`
  - `reports/paytv_report_<timestamp>.csv`
  - `reports/paytv_report_<timestamp>.html`
  - `reports/latest.json`
  - `reports/latest.csv`
  - `reports/latest.html`
- Reports include a summary, engine status table, and normalized results.

## Runtime behavior

- The app still starts without API keys.
- Empty credentials produce a report with zero results and clear skipped-engine statuses.
- Browser verification remains disabled by default.
- Local proxy/VPN helper remains disabled by default.
