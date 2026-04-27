import logging
import os
import threading
import zipfile
from pathlib import Path


# Selenium is optional at startup. Import it lazily only when browser
# verification is explicitly requested. This lets local-credentials/offline
# mode boot without installing a browser stack.

def _load_selenium():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        try:
            from selenium.webdriver.chrome.service import Service
        except Exception:  # pragma: no cover - Selenium 3 fallback only
            Service = None
    except ImportError as err:
        raise RuntimeError(
            "Selenium is required only for browser verification. "
            "Install requirements.txt or disable PAYTV_VERIFY_RESULTS_IN_BROWSER."
        ) from err
    return webdriver, Options, Service



PROXY_HOST = os.environ.get("PAYTV_PROXY_HOST", "127.0.0.1")
PROXY_PORT = int(os.environ.get("PAYTV_PROXY_PORT", "1080"))
PROXY_USER = os.environ.get("PAYTV_PROXY_USER", "")
PROXY_PASS = os.environ.get("PAYTV_PROXY_PASS", "")


MANIFEST_JSON = """
{
  "version": "1.0.0",
  "manifest_version": 2,
  "name": "Chrome Proxy Auth",
  "permissions": ["proxy", "tabs", "unlimitedStorage", "storage", "<all_urls>", "webRequest", "webRequestBlocking"],
  "background": {"scripts": ["background.js"]},
  "minimum_chrome_version":"22.0.0"
}
"""


BACKGROUND_JS = """
var config = {
  mode: "fixed_servers",
  rules: {
    singleProxy: {scheme: "%s", host: "%s", port: parseInt(%s)},
    bypassList: ["localhost", "127.0.0.1"]
  }
};
chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
function callbackFn(details) {
  return {authCredentials: {username: "%s", password: "%s"}};
}
chrome.webRequest.onAuthRequired.addListener(callbackFn, {urls: ["<all_urls>"]}, ['blocking']);
"""


class engine:
    """Browser/proxy factory for the legacy seeker.

    The old implementation hard-coded proxy credentials and returned ``None``
    because ``_init`` was never set.  This version is usable without a proxy,
    and the local SOCKS proxy is optional.
    """

    def __init__(self, device=None, proxy_host=PROXY_HOST, proxy_port=PROXY_PORT,
                 proxy_username=PROXY_USER, proxy_password=PROXY_PASS):
        self.__device__ = device or os.environ.get("PAYTV_BIND_DEVICE", "")
        self.proxy_host = proxy_host
        self.proxy_port = int(proxy_port)
        self.proxyUsername = proxy_username or ""
        self.proxyPassword = proxy_password or ""
        self.proxyProcessor = None
        self.threadProxy = None
        self.threadProxyStatus = None
        self._init = True
        logging.debug("Search engine initialized; bind device=%s", self.__device__ or "not set")

    def checkProxyStatus(self):
        logging.debug("Proxy status thread started")

    def configureProxy(self, port=None, username=None, password=None, device=None):
        # Import the custom SOCKS proxy lazily. The proxy/vpn helper is optional
        # and should not affect normal offline startup or report generation.
        from oss.customProxySock.customProxySock import customProxySock

        self.proxy_port = int(port or self.proxy_port)
        self.proxyUsername = username if username is not None else self.proxyUsername
        self.proxyPassword = password if password is not None else self.proxyPassword
        self.__device__ = device if device is not None else self.__device__
        self.proxyProcessor = customProxySock(
            self.proxy_port,
            self.proxyUsername,
            self.proxyPassword,
            self.__device__,
        )
        self.threadProxyStatus = threading.Thread(
            target=self.checkProxyStatus,
            name="engine.checkProxyStatus",
            daemon=True,
        )
        self.threadProxyStatus.start()
        logging.debug("Local SOCKS proxy configured on 127.0.0.1:%s", self.proxy_port)
        return self.proxyProcessor

    def startProxy(self):
        if self.proxyProcessor is None:
            self.configureProxy()
        if self.threadProxy and self.threadProxy.is_alive():
            return
        self.threadProxy = threading.Thread(
            target=self.proxyProcessor.launchProxySock,
            name="customProxySock.launchProxySock",
            daemon=True,
        )
        self.threadProxy.start()
        logging.info("Local SOCKS proxy started on 127.0.0.1:%s", self.proxy_port)

    def stopProxy(self):
        logging.debug("Stopping search engine proxy")
        if self.proxyProcessor is not None:
            self.proxyProcessor.shutdownProxySock()

    def _write_proxy_auth_extension(self, proxy_scheme):
        pluginfile = Path("proxy_auth_plugin.zip")
        background_js = BACKGROUND_JS % (
            proxy_scheme,
            self.proxy_host,
            self.proxy_port,
            self.proxyUsername,
            self.proxyPassword,
        )
        with zipfile.ZipFile(pluginfile, "w") as zp:
            zp.writestr("manifest.json", MANIFEST_JSON)
            zp.writestr("background.js", background_js)
        return str(pluginfile)

    def getChromedriverProxy(self, use_proxy=True, user_agent=None, headless=True):
        webdriver, Options, Service = _load_selenium()
        logging.debug("Creating Chrome driver; proxy=%s", use_proxy)
        user_agent = user_agent or os.environ.get(
            "PAYTV_USER_AGENT",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120 Safari/537.36",
        )

        options = Options()
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        if headless:
            options.add_argument("--headless=new")

        if use_proxy:
            proxy_scheme = os.environ.get("PAYTV_PROXY_SCHEME", "socks5")
            if self.proxyUsername and self.proxyPassword and proxy_scheme in {"http", "https"}:
                options.add_extension(self._write_proxy_auth_extension(proxy_scheme))
            else:
                options.add_argument(f"--proxy-server={proxy_scheme}://{self.proxy_host}:{self.proxy_port}")

        driver_path = os.environ.get("CHROMEDRIVER_PATH")
        local_driver = Path(__file__).with_name("chromedriver")
        if not driver_path and local_driver.exists():
            driver_path = str(local_driver)

        if driver_path and Service is not None:
            return webdriver.Chrome(service=Service(driver_path), options=options)
        return webdriver.Chrome(options=options)
