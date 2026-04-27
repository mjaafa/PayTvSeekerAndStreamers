from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import hashlib
import json
import logging
import os
import ssl
import urllib.request
from pathlib import Path
from urllib.parse import urljoin


class crypto:
    """Credential and session-key helper.

    This version does **not** require a credential server to start the
    application.  The default/offline path is local ``credentials.json``.

    Credential loading order:
      1. PAYTV_CREDENTIALS_FILE, if set.
      2. credentials.json in the current working directory.
      3. credentials.json in the project root.
      4. credentials.example.json in the project root, as a startup-safe fallback.
      5. PAYTV_CREDENTIALS_URL, if set.
      6. <server_url>/credentials.json, only when a server URL was explicitly passed.

    No client certificate is loaded and no mutual-TLS authentication is used.
    HTTPS still validates the server certificate by default.  For lab-only
    self-signed endpoints, set PAYTV_ALLOW_INSECURE_TLS=1 explicitly.
    """

    generateKeys = True

    def __init__(self, __server_url__=None, __server_ip__=None, __server_port__=None):
        self.server_url = __server_url__
        self.server_ip = __server_ip__
        self.server_port = __server_port__
        self.credential = {}
        self.remoteKeyRAW = None
        self.remoteKey = None
        self.remoteKeyHash = None
        self.encryptionKeyRAW = None
        self.decryptionKeyRAW = None
        self.encryptionKey = None
        self.decryptionKey = None
        self.sessionEncryptionToken = None
        self.sessionDecryptionToken = None

        try:
            self.credential = self._load_credentials()
        except Exception as err:
            logging.error("Credential loading failed: %s", err)
            self.credential = {}

    @staticmethod
    def _project_root():
        return Path(__file__).resolve().parents[1]

    def _candidate_credentials_files(self):
        """Return local credential files in preferred order, without duplicates."""
        candidates = []
        env_file = os.environ.get("PAYTV_CREDENTIALS_FILE")
        if env_file:
            candidates.append(Path(env_file).expanduser())

        cwd = Path.cwd()
        root = self._project_root()
        candidates.extend([
            cwd / "credentials.json",
            root / "credentials.json",
            root / "credentials.example.json",
        ])

        unique = []
        seen = set()
        for path in candidates:
            try:
                key = str(path.resolve())
            except Exception:
                key = str(path)
            if key not in seen:
                unique.append(path)
                seen.add(key)
        return unique

    def _load_credentials(self):
        local_error = None
        for path in self._candidate_credentials_files():
            if not path.exists():
                continue
            try:
                credentials = self._load_credentials_file(path)
                if path.name == "credentials.example.json":
                    logging.warning(
                        "Using credentials.example.json fallback. Copy it to credentials.json "
                        "and fill real API keys for actual searches."
                    )
                else:
                    logging.info("Using local credential file: %s", path)
                return credentials
            except Exception as err:
                local_error = err
                logging.warning("Cannot load local credential file %s: %s", path, err)

        # Remote credentials are optional. They are only tried if explicitly configured
        # or if legacy code passes a server URL and no local credentials are available.
        url = os.environ.get("PAYTV_CREDENTIALS_URL")
        if not url and self.server_url:
            url = urljoin(str(self.server_url).rstrip("/") + "/", "credentials.json")

        if url:
            try:
                logging.info("No usable local credentials found; trying remote credentials: %s", url)
                return self._load_credentials_url(url)
            except Exception as err:
                logging.warning("Remote credential loading failed; continuing without server: %s", err)
                if local_error is not None:
                    raise RuntimeError(
                        "No usable credentials.json was found and remote credential loading failed"
                    ) from err
                raise

        raise FileNotFoundError(
            "No credentials source found. Create credentials.json from "
            "credentials.example.json, or set PAYTV_CREDENTIALS_FILE."
        )

    def _load_credentials_file(self, path: Path):
        with path.open("r", encoding="utf-8") as fd:
            data = json.load(fd)
        return self._normalise_credentials(data)

    def _load_credentials_url(self, url: str):
        timeout = int(os.environ.get("PAYTV_CREDENTIALS_TIMEOUT", "10"))
        context = ssl.create_default_context()
        if os.environ.get("PAYTV_ALLOW_INSECURE_TLS") == "1":
            logging.warning("PAYTV_ALLOW_INSECURE_TLS=1 is enabled; TLS certificates are not verified.")
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        request = urllib.request.Request(url, headers={"User-Agent": "PayTvSeeker/no-mtls"})
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            data = json.loads(response.read().decode("utf-8"))
        return self._normalise_credentials(data)

    def _normalise_credentials(self, data):
        try:
            entry = data["Credential"][0]
            encryption = entry["Encryption"][0]
        except (KeyError, IndexError, TypeError) as err:
            raise ValueError("Invalid credential JSON structure") from err

        credential = {
            "name": entry.get("Name", "Pay-TV-seeker"),
            "version": encryption.get("Version", "unknown"),
            "method": encryption.get("Method", "LocalCredentialsJson"),
            "password": encryption.get("Password", ""),
            "algorithm": encryption.get("Algorithm", "hashes.SHA3_512"),
            "token": encryption.get("token", ""),
            "backend": encryption.get("backend", "default_backend"),
            "models": encryption.get("models", ""),
            "apiKey": encryption.get("apiKey", ""),
        }

        if not credential["password"] or not credential["token"]:
            raise ValueError("Credential JSON must contain Password and token fields")
        return credential

    @staticmethod
    def _to_bytes(value):
        if isinstance(value, bytes):
            return value
        if isinstance(value, bytearray):
            return bytes(value)
        return str(value).encode("utf-8")

    def crypto_fetchServerToken(self):
        """Initialise the local crypto token from loaded credentials.

        The method name is kept for backward compatibility, but it no longer
        means that a server must be contacted.  With local ``credentials.json``
        this method only derives a Fernet key from Password + token.
        """
        if not self.credential:
            logging.error("No credential data available")
            return None

        hash_name = str(self.credential.get("algorithm", "hashes.SHA3_512")).split(".")[-1]
        try:
            hash_func = getattr(hashes, hash_name)
        except AttributeError:
            logging.error("Unsupported hash algorithm %s", hash_name)
            return None

        kdf = PBKDF2HMAC(
            algorithm=hash_func(),
            length=32,
            salt=self._to_bytes(self.credential["token"]),
            iterations=100000,
            backend=default_backend(),
        )
        password_bytes = self._to_bytes(self.credential["password"])
        self.remoteKeyRAW = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        self.remoteKey = Fernet(self.remoteKeyRAW)
        self.remoteKeyHash = hashlib.sha512(self.remoteKeyRAW).hexdigest()
        logging.debug("Credential token initialized for client %s", self.crypto_getClient())
        return self

    def crypto_getremoteHashIndex(self):
        return self.remoteKeyHash

    def crypto_set_generateKeys(self, __enable__, __encryption_key__, __decryption_key__):
        self.generateKeys = __enable__
        if not __enable__:
            self.encryptionKeyRAW = self._to_bytes(__encryption_key__)
            self.decryptionKeyRAW = self._to_bytes(__decryption_key__)

    def crypto_genEncryptionKey(self):
        if self.remoteKey is None:
            raise RuntimeError("Call crypto_fetchServerToken() before generating encryption keys")
        if self.generateKeys:
            self.encryptionKeyRAW = Fernet.generate_key()
        self.encryptionKey = Fernet(self.encryptionKeyRAW)
        self.sessionEncryptionToken = MultiFernet([self.remoteKey, self.encryptionKey])

    def crypto_genDecryptionKey(self):
        if self.remoteKeyRAW is None:
            raise RuntimeError("Call crypto_fetchServerToken() before generating decryption keys")
        if self.generateKeys:
            self.decryptionKeyRAW = Fernet.generate_key()
        self.decryptionKey = Fernet(self.decryptionKeyRAW)
        self.remoteKey = Fernet(self.remoteKeyRAW)
        self.sessionDecryptionToken = MultiFernet([
            self.remoteKey,
            self.encryptionKey,
            self.decryptionKey,
        ])

    def crypto_encrypt(self, __object__):
        if self.sessionEncryptionToken is None:
            raise RuntimeError("Encryption token is not initialized")
        return self.sessionEncryptionToken.encrypt(self._to_bytes(__object__))

    def crypto_decrypt(self, __object__):
        if self.sessionDecryptionToken is None:
            raise RuntimeError("Decryption token is not initialized")
        return self.sessionDecryptionToken.decrypt(self._to_bytes(__object__))

    def crypto_getClient(self):
        return self.credential.get("name", "Pay-TV-seeker")

    def crypto_getStoringKeys(self, __session_key_file__):
        """Persist the current session key material for the SQLite key store.

        Older code only wrote this file when keys were newly generated. That
        made startup fail when a database already existed and the keys were
        reused. Write the current keys whenever they are available.
        """
        if self.encryptionKeyRAW is None or self.decryptionKeyRAW is None:
            raise RuntimeError("Session keys are not initialized")
        with open(__session_key_file__, "w", encoding="utf-8") as fd:
            fd.write(str(self.remoteKeyHash) + "\n")
            fd.write(self.encryptionKeyRAW.decode("utf-8") + "\n")
            fd.write(self.decryptionKeyRAW.decode("utf-8"))

    def crypto_getMiscDataModels(self):
        return self.crypto_encrypt(self.credential.get("models", ""))

    def crypto_getMiscDataApiKey(self):
        return self.crypto_encrypt(self.credential.get("apiKey", ""))

    def crypto_getVersion(self):
        return self.credential.get("version", "unknown")
