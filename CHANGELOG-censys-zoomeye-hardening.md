# Censys / ZoomEye hardening

- Fixed Censys parser crash when the API returns non-dict `result`, hit, or service values.
- Added defensive parsing for Censys `result.hits`, top-level `hits`, top-level `data`, `services`, and `matched_services` shapes.
- Added clearer Censys HTTP/auth error messages.
- Added explicit Censys fields request for host/service previews.
- Hardened ZoomEye result parsing for multiple response shapes.
- Added ZoomEye `.hk` fallback endpoint when the primary endpoint returns HTTP 403.
- Added a warning when the ZoomEye credential looks like an old JWT token; current APIKEY credentials are preferred.
- Added clearer ZoomEye 401/403 diagnostics without logging API tokens.
