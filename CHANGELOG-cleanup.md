# Cleanup changelog

## No-certificate-auth cleanup

- `CustomCrypto/crypto.py`
  - Removed `ssl.create_default_context(... cafile=server_cert)` tied to committed cert files.
  - Removed `context.load_cert_chain(client.crt, client.key)`.
  - Removed direct socket/mTLS credential retrieval.
  - Added local or HTTPS credential loading with normal TLS verification.

- `server-nginx-configuration/server-conf/ssl.conf`
  - Removed `ssl_client_certificate`.
  - Removed `ssl_verify_client on`.
  - Restricted protocol list to TLSv1.2/TLSv1.3.

- `Engine/`
  - Replaced Selenium web scraping in Censys/ZoomEye with API clients.
  - Removed deprecated Alexa scraping and kept a no-op compatibility class.
  - Fixed the Chrome driver creation path and initialization bug.
  - Removed hard-coded proxy credentials.

- `oss/customProxySock/`
  - Fixed Python 3 byte handling.
  - Added no-auth SOCKS5 mode.
  - Fixed undefined exception variables and shutdown handling.

- `Database/`
  - Replaced unsafe string-built SELECT queries with parameterized queries.

- Repository hygiene
  - Removed committed generated shared-object binaries; rebuild the C helper locally if interface binding is needed.
  - Replaced the old CI workflow with a syntax-check workflow.


## Local credential startup patch

- `CustomCrypto/crypto.py`
  - Local `credentials.json` is now the default credential source.
  - The application can boot without connecting to a credential server.
  - `credentials.example.json` is used as a safe fallback if no local `credentials.json` exists.
  - Remote credential loading is optional and only used when configured and no local credential file is usable.
  - The legacy `crypto_fetchServerToken()` name is preserved for compatibility, but it now derives the token locally when using `credentials.json`.

- `Seeker/seeker.py`
  - Simplified crypto initialization so startup does not depend on server host/port settings.

- Repository hygiene
  - Added a placeholder `credentials.json` with no real secrets, so `python main.py` can start immediately.


## Placeholder credential handling

- `Engine/common.py`
  - Added placeholder-secret detection so values like `YOUR_SHODAN_KEY` are treated as missing credentials.

- `credentials.json`
  - Added a local startup-only placeholder with empty `apiKey` and `models`, allowing `python main.py` to boot without server access or external API calls.


## Server certificate sample cleanup

- Removed bundled generated server certificate/DH parameter files.
- Updated the Nginx sample to keep TLSv1.2/TLSv1.3 only.
- Local `credentials.json` mode does not require the Nginx credential server at all.


## Local startup execution patch

- Made Selenium import lazy so offline startup works without browser dependencies.
- Made Shodan import lazy so offline startup works without the shodan package when no API key is configured.
