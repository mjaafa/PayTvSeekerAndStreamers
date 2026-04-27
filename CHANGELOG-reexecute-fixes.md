# Re-execution fixes

- Do not require the `shodan` Python package at startup when no model queries are configured.
- Skip Shodan cleanly when a Shodan key exists but the query model list is empty.
- Write current session key material even when reusing an existing key store.
- Update encrypted API/search material in SQLite if the key row already exists.
- Generated SQLite DBs, logs, and temporary key files are excluded from the distributable zip.
