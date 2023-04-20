import signal
import threading
import os
import zipfile
from multiprocessing import Process
import sys
from Engine.shodan_api import shodan_api
from Engine.censys_api import censys
from Engine.zoomeye_api import zoomeye
from oss.customProxySock.customProxySock import customProxySock
import logging
from Colorer import colorer
### selenium and chromeDriver ###
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from NetworkHoppingManager.vpnHopper import vpnHopper
from notifiers import get_notifier
PROXY_HOST = 'socks5://127.0.0.1'  # rotating proxy
PROXY_PORT = 1080
PROXY_USER = '0H6Q9Qmx'
PROXY_PASS = 'fUX1QHnc'

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
          singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
          },
          bypassList: ["localhost"]
        }
      };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

class engine():
    proxyUsername   = PROXY_USER
    proxyPassword   = PROXY_PASS
    _init           = False;
    __device__      = ""

    def __init__(self, device="wlp59s0"):
        logging.debug("starting Search Engine");
        if (not self._init):
            self._init = False
            __device__ = device
        else:
            logging.info("Engine Proxy already configured getChromeDriver Instance can be done ")

        logging.debug(" setting up VPN Hopper ")
        __vpn_instance___ = vpnHopper()
       # vpnHopper.vpnBounceConfManagement(__vpn_instance___, device)
        mac_address = vpnHopper.get_mac_address(__vpn_instance___, device)
        logging.debug(" device %s mac address get mac address %s ", device, mac_address)
        vpnHopper.setup_if_conf_urllib3(__vpn_instance___, device)
        logging.debug(" urllib3 setup for device ...")
#        vpnHopper.vpnBounceConfManagement(__vpn_instance___)

    def checkProxyStatus(self):
        logging.debug(" state check thread");

    def configureProxy(self):
        if(self._init == True):
            logging.debug("Proxy already initialized")
            return

        logging.debug("configure proxy for selenium");
        self.proxyProcessor = customProxySock(1080, self.proxyUsername,
                                              self.proxyPassword,
                                              self.__device__)

        self.threadProxyStatus = threading.Thread(target=self.checkProxyStatus,
                                            name="self.checkProxyStatus",args=())
        self.threadProxyStatus.setDaemon(True)
        self.threadProxyStatus.start()


    def startProxy(self):
        if(self._init == True):
            return
        ## threading maybe used to avoid blocking
        self.threadProxy = threading.Thread(target=customProxySock.launchProxySock,
                                            name="customProxySock.launchProxySock",args=(self.proxyProcessor,))
        self.threadProxy.setDaemon(True)
        self.threadProxy.start()

    def stopProxy(self):
        logging.debug("Stopping Engine ")
        self._init = False
        #PID=self.threadProxy.ident
        #self.threadProxy.join()
        ###customProxySock.shutdownProxySock(self.proxyProcessor)
        #self.threadProxy.stop()
        #self.threadProxyStatus.stop()
        ####self._init = False
        ###os.kill(os.getpid(), signal.SIGKILL)

    def getChromedriverProxy(self, use_proxy=True, user_agent=None):
        logging.debug(" gettting chrome driver instance with proxy and custom user agent")
        if (None == user_agent):
            useragent = "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"
        if(self._init is False):
            return None
        logging.debug(" getChome driver ")
        path = os.path.dirname(os.path.abspath(__file__))
        chrome_options = webdriver.ChromeOptions()
        if use_proxy:
            pluginfile = 'proxy_auth_plugin.zip'

            with zipfile.ZipFile(pluginfile, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            chrome_options.add_extension(pluginfile)
        if useragent:
            chrome_options.add_argument('--user-agent=%s' % useragent)
        driver = webdriver.Chrome(
            os.path.join(path, 'chromedriver'),
            chrome_options=chrome_options)
        desired_capabilities = DesiredCapabilities.CHROME.copy()
        desired_capabilities['acceptInsecureCerts'] = True
        profile = webdriver.ChromeOptions()
        profile.add_argument('--ignore-certificate-errors')
        profile.add_argument('headless')
        driver = webdriver.Chrome(chrome_options=profile)
        return driver
