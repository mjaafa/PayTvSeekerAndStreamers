import logging
import os
from pathlib import Path

from CustomCrypto.crypto import crypto
from Database.database import database
from Database.result_store import ResultStore
from Engine.alexa_api import alexa_api
from Engine.censys_api import censys
from Engine.engine import engine
from Engine.results import dedupe_results, normalize_legacy_result
from Engine.shodan_api import shodan_api
from Engine.zoomeye_api import zoomeye
from Reporting.report_writer import ReportWriter
from Reporting.web_access_checker import WebAccessChecker

class seeker:
    visibility = False

    def __init__(self):
        logging.info("Initializing seeker")
        self.searchEngine = engine(device=os.environ.get("PAYTV_BIND_DEVICE", ""))
        self.proxy_enabled = os.environ.get("PAYTV_ENABLE_LOCAL_PROXY", "0") == "1"
        if self.proxy_enabled:
            self.searchEngine.configureProxy()
            self.searchEngine.startProxy()
        self.show_results = []  # Legacy URL-only list, kept for optional browser/Alexa flow.
        self.normalized_results = []
        self.engine_status = []
        self.report_paths = {}
        self.reporter = ReportWriter(os.environ.get("PAYTV_REPORT_DIR", "reports"))

    def set_browser_visibilty(self, __visible__):
        self.visibility = bool(__visible__)

    def get_browser_visibilty(self):
        return self.visibility

    def __init_storing_search_keys(self):
        # Local credentials.json is the default/offline mode.  A remote
        # PAYTV_CREDENTIALS_URL remains optional, but startup no longer depends
        # on reaching a credential server.
        self.cryptoCore = crypto(os.environ.get("PAYTV_CREDENTIALS_URL"))

        if crypto.crypto_fetchServerToken(self.cryptoCore) is None:
            logging.error("Cannot load credentials. Configure credentials.json or PAYTV_CREDENTIALS_FILE.")
            return None

        remote_client = crypto.crypto_getClient(self.cryptoCore)
        safe_client = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in remote_client)
        self.__database_name__ = safe_client + "_search_keys.db"

        self.searchKeyDatabase = database(
            self.__database_name__,
            "SEARCH_API (TOKEN_HASH TEXT, KEY1 BLOB NULL, KEY2 BLOB NULL, "
            "API_KEY TEXT, SEARCH_KEY TEXT, VERSION TEXT, PRIMARY KEY (TOKEN_HASH))",
        )

        if self.searchKeyDatabase.checkEncryption(
            self.__database_name__,
            crypto.crypto_getremoteHashIndex(self.cryptoCore),
        ):
            crypto.crypto_set_generateKeys(
                self.cryptoCore,
                False,
                self.searchKeyDatabase.getEncryptKey(
                    self.__database_name__,
                    crypto.crypto_getremoteHashIndex(self.cryptoCore),
                ),
                self.searchKeyDatabase.getDecryptKey(
                    self.__database_name__,
                    crypto.crypto_getremoteHashIndex(self.cryptoCore),
                ),
            )
        else:
            crypto.crypto_set_generateKeys(self.cryptoCore, True, None, None)

        crypto.crypto_genEncryptionKey(self.cryptoCore)
        crypto.crypto_genDecryptionKey(self.cryptoCore)

        session_key_file = Path("sessionKeyFile.key")
        query = (
            "INSERT INTO SEARCH_API "
            "(TOKEN_HASH, KEY1, KEY2, API_KEY, SEARCH_KEY, VERSION) "
            "VALUES (?, ?, ?, ?, ?, ?)"
        )
        try:
            crypto.crypto_getStoringKeys(self.cryptoCore, str(session_key_file))
            self.searchKeyDatabase.database_insert_raw_data_fromFile(
                self.__database_name__,
                str(session_key_file),
                query,
                crypto.crypto_getMiscDataApiKey(self.cryptoCore),
                crypto.crypto_getMiscDataModels(self.cryptoCore),
                crypto.crypto_getVersion(self.cryptoCore),
            )
        finally:
            if session_key_file.exists():
                session_key_file.unlink()
        return self

    def __init_storing_streamers(self):
        remote_client = crypto.crypto_getClient(self.cryptoCore)
        safe_client = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in remote_client)
        self.__streaming_database_name__ = safe_client + "_STB_streamer.db"
        self.streamingDatabase = database(
            self.__streaming_database_name__,
            "STREAMING_REPORT (IP_ADDRESS TEXT, SNAPSHOT BLOB NULL, IPTV_LIST TEXT, "
            "TOKEN_HASH TEXT, STREAMER_INFO TEXT, CCCAM_SERVER BLOB NULL, PRIMARY KEY (IP_ADDRESS))",
        )
        self.resultStore = ResultStore(self.__streaming_database_name__)

    def init_config(self):
        if self.__init_storing_search_keys() is None:
            logging.error("Configuration cannot be completed")
            return None
        logging.info("Configuration initialized")
        return self

    def _show_reults(self, results, engine_name="legacy"):
        # Legacy name kept for compatibility.  Browser verification is optional
        # and disabled unless PAYTV_VERIFY_RESULTS_IN_BROWSER=1.
        results = results or []
        normalized = [normalize_legacy_result(item, engine=engine_name) for item in results]
        normalized = dedupe_results(normalized)
        self.normalized_results.extend(normalized)
        self.show_results.extend([item.get("url") for item in normalized if item.get("url")])

        if os.environ.get("PAYTV_VERIFY_RESULTS_IN_BROWSER", "0") != "1":
            for result in normalized:
                logging.info(
                    "Result: engine=%s query=%r url=%s confidence=%s",
                    result.get("engine"),
                    result.get("query"),
                    result.get("url"),
                    result.get("confidence"),
                )
            return normalized

        driver = self.searchEngine.getChromedriverProxy(
            use_proxy=self.proxy_enabled,
            user_agent=None,
            headless=not self.visibility,
        )
        try:
            for result in normalized:
                url = result.get("url")
                logging.debug("Opening result URL: %s", url)
                try:
                    driver.set_window_size(1024, 768)
                    driver.implicitly_wait(10)
                    driver.get(url)
                except Exception as err:
                    logging.debug("Page unreachable %s: %s", url, err)
        finally:
            driver.quit()
        return normalized

    def _load_decrypted_search_material(self):
        api_key = crypto.crypto_decrypt(
            self.cryptoCore,
            self.searchKeyDatabase.getApiKey(
                self.__database_name__,
                crypto.crypto_getremoteHashIndex(self.cryptoCore),
            ),
        )
        models = crypto.crypto_decrypt(
            self.cryptoCore,
            self.searchKeyDatabase.getSearchKeys(
                self.__database_name__,
                crypto.crypto_getremoteHashIndex(self.cryptoCore),
            ),
        )
        api_key = api_key.decode("utf-8") if isinstance(api_key, bytes) else str(api_key)
        models = models.decode("utf-8") if isinstance(models, bytes) else str(models)
        logging.info("Loaded search configuration: %d model query item(s)", len([m for m in models.split(',') if m.strip()]))
        return api_key, models

    def _record_engine_status(self, name, search_engine, results=None, error=None):
        status = getattr(search_engine, "last_status", None) or {}
        if not status:
            status = {
                "engine": name,
                "status": "error" if error else "ok",
                "result_count": len(results or []),
                "error": str(error or ""),
            }
        if error:
            status = dict(status)
            status["status"] = "error"
            status["error"] = str(error)
        self.engine_status.append(status)

    def _finalize_results(self):
        web_report_paths = {}
        if os.environ.get("PAYTV_CHECK_WEB_LOAD", "0") == "0":
            try:
                checker = WebAccessChecker(os.environ.get("PAYTV_REPORT_DIR", "reports"))
                web_report_paths = checker.check_results(self.normalized_results)
            except Exception as err:
                logging.error("Web-load check failed: %s", err)
                web_report_paths = {"web_error": str(err)}

        self.report_paths = self.reporter.write(
            self.normalized_results,
            engine_status=self.engine_status,
            related_reports=web_report_paths,
        )
        self.report_paths.update(web_report_paths)

        """self.normalized_results = dedupe_results(self.normalized_results)
        if hasattr(self, "resultStore"):
            self.resultStore.upsert_many(self.normalized_results)
        self.report_paths = self.reporter.write(self.normalized_results, self.engine_status)
        logging.info("Result flow complete: %d normalized result(s)", len(self.normalized_results))
        return self.report_paths"""

    def search(self):
        api_key, models = self._load_decrypted_search_material()
        self.__init_storing_streamers()

        engines = [
            ("censys", censys(api_key, models, self.searchEngine)),
            ("zoomeye", zoomeye(api_key, models, self.searchEngine)),
            ("shodan", shodan_api(api_key, models)),
        ]

        try:
            for name, search_engine in engines:
                try:
                    logging.info("Running %s engine", name)
                    results = search_engine.search()
                    self._show_reults(results, engine_name=name)
                    self._record_engine_status(name, search_engine, results=results)
                except Exception as err:
                    logging.error("%s engine failed: %s", name, err)
                    self._record_engine_status(name, search_engine, error=err)

            if os.environ.get("PAYTV_ENABLE_ALEXA_ENRICHMENT", "0") == "1":
                try:
                    alexa_api_search = alexa_api("legacy", self.searchEngine)
                    self._show_reults(alexa_api_search.search(self.show_results), engine_name="alexa")
                    self.engine_status.append({"engine": "alexa", "status": "ok", "result_count": 0, "error": ""})
                except Exception as err:
                    logging.error("Alexa enrichment failed: %s", err)
                    self.engine_status.append({"engine": "alexa", "status": "error", "result_count": 0, "error": str(err)})

            self._finalize_results()
        finally:
            self.searchEngine.stopProxy()
        return self.normalized_results
