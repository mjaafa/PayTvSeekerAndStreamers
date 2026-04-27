# Server Nginx configuration

This sample now uses normal server-side TLS only.  Mutual TLS / client
certificate authentication was removed.

To use HTTPS with this sample:

1. Generate or install your own server certificate on the server.
2. Update `server-conf/ssl.conf` with your server certificate/key paths.
3. Do **not** commit generated certificates, private keys, or client certificates to this repository.

The Python application does not need this server config when local `credentials.json` is used.

The previous `ssl_client_certificate` and `ssl_verify_client on` directives were intentionally removed.
