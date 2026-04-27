# ZoomEye SDK migration

- Replaced the hand-written ZoomEye `/host/search` requests client with the official `zoomeyeai` SDK from `zoomeye-ai/ZoomEye-python`.
- Added lazy import of `zoomeyeai.sdk.ZoomEye`, so the application still starts when ZoomEye is not configured.
- Added `zoomeyeai>=3.0.1` to `requirements.txt`.
- Updated ZoomEye search to use SDK APIKEY authentication and `ZoomEye.search(...)`.
- Added support for configurable `ZOOMEYE_PAGE_SIZE`, `ZOOMEYE_SUB_TYPE`, `ZOOMEYE_FIELDS`, and `ZOOMEYE_FACETS` environment variables.
- Kept defensive result parsing for multiple API/SDK response shapes.
- Added clearer diagnostics when the configured ZoomEye credential appears to be an old JWT/login token instead of a current APIKEY.
