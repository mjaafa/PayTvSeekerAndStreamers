#
#
# Search SHODAN and print a list of IPs matching the query
#
# Author: achillean
from time import sleep
import sys
import logging
import Colorer

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium
import hashlib
import json
from pprint import pprint
import os
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display
from Database.database import database
from CustomCrypto.crypto import crypto
from Engine.shodan_api import shodan_api
from Engine.censys_api import censys
from Engine.zoomeye_api import zoomeye
from Engine.alexa_api import alexa_api

class seeker():
    visibility = False

    def __init__(self):
        logging.info(" init ")

    def set_browser_visibilty(self, __visible__):
        self.visibility = __visible__;

    def get_browser_visibilty(self):
        return self.visibility;

    def __checkIfTargetusesTorrent(self):
        logging.debug("Check if Target uses torrent :");
        results = self.driver.find_elements_by_class_name('torrent_files');
        for torrentFiles in results:
            logging.info("Torrent ::", torrentFiles.text);

    def __init_storing_search_keys(self):
        self.cryptoCore = crypto('https://antikythera-techs.xyz/','antikythera-techs.xyz', 8443)

        logging.debug("cryptoCore : %s ", self.cryptoCore);
        if ( None != crypto.crypto_fetchServerToken(self.cryptoCore)):
            logging.info("    |->  Booting  component crypto remote server  : Done ")
        else:
            logging.info("    |->  Booting  component crypto remote server  : KO ")
            logging.error("        Please connect to the network or check the client key certificate : cannot fetch credential ")
            return None;

        __remote_client   = crypto.crypto_getClient(self.cryptoCore)

        self.__database_name__ = __remote_client + "_search_keys.db"

        self.searchKeyDatabase = database(self.__database_name__,
                                          " SEARCH_API (TOKEN_HASH TEXT, KEY1 BLOB NULL, KEY2 BLOB NULL, API_KEY TEXT, SEARCH_KEY TEXT, VERSION TEXT, PRIMARY KEY (TOKEN_HASH))")
        if (None != self.searchKeyDatabase.checkEncryption(self.__database_name__,
                                                           self.cryptoCore.remoteKeyHash)):
            logging.info(" check the encryption :: ")
            crypto.crypto_set_generateKeys(self.cryptoCore,
                                           False,
                                           self.searchKeyDatabase.getEncryptKey(self.__database_name__,
                                                                                crypto.crypto_getremoteHashIndex(self.cryptoCore)),
                                           self.searchKeyDatabase.getDecryptKey(self.__database_name__,
                                                                                crypto.crypto_getremoteHashIndex(self.cryptoCore)))
        else:
            crypto.crypto_set_generateKeys(self.cryptoCore,
                                           True,
                                           None,
                                           None)
            logging.info("    |->  Booting  component crypto Encryption generate key   : Done ")

        crypto.crypto_genEncryptionKey(self.cryptoCore)
        logging.info("    |->  Booting  component crypto Decryption generate key   : Done ")
        crypto.crypto_genDecryptionKey(self.cryptoCore)
        self.sessionKeyFile='sessionKeyFile.key'
        # strore keys
        crypto.crypto_getStoringKeys(self.cryptoCore, self.sessionKeyFile);

        query = " INSERT INTO SEARCH_API (TOKEN_HASH, KEY1, KEY2, API_KEY, SEARCH_KEY, VERSION) VALUES (?, ?, ?, ?, ?,?) " ;
        try:
            self.searchKeyDatabase.database_insert_raw_data_fromFile(self.__database_name__,
                                                                     "sessionKeyFile.key",
                                                                     query,
                                                                     crypto.crypto_getMiscDataApiKey(self.cryptoCore),
                                                                     crypto.crypto_getMiscDataModels(self.cryptoCore),
                                                                     crypto.crypto_getVersion(self.cryptoCore))
            os.remove(self.sessionKeyFile)
        except :
            logging.info("entry already in there")

        return self

    def __init_storing_streamers(self):
        __remote_client   = crypto.crypto_getClient(self.cryptoCore)
        self.__database_name__ = __remote_client + "_STB_streamer.db"

        self.streamingDatabase = database(self.__database_name__,
                                          " STREAMING_REPORT (IP_ADDRESS TEXT, SNAPSHOT BLOB NULL, IPTV_LIST TEXT, TOKEN_HASH TEXT, STREAMER_INFO TEXT, CCCAM_SERVER BLOB NULL, PRIMARY KEY (IP_ADDRESS))")


    def init_config(self):
        if (None == self.__init_storing_search_keys()):
            logging.error(" Error configuration cannot be completed ")
            return None;
        else:
            logging.info(" Init Configuration OK ")
            return self;

    def _show_reults(self, results):
        for result in results:
            logging.debug("url %s ", result)
            # logging.debug("results : %s ", result['data'])
            desired_capabilities = DesiredCapabilities.FIREFOX.copy()
            desired_capabilities['acceptInsecureCerts'] = True
            driver = webdriver.Firefox(capabilities=desired_capabilities)
            driver.accept_untrusted_certs = True
            driver.acceptSslCerts = True
            driver.set_window_size(1024, 768)
            try:
                driver.implicitly_wait(10)
                driver.get(result)
            except:
                logging.debug(" page unreachable ...");
                driver.quit()
                #display.close()
                continue;
                pass;

    def search(self):
        logging.info(" >> api key :: %s ", crypto.crypto_getMiscDataApiKey(self.cryptoCore))
        api_key = crypto.crypto_decrypt(self.cryptoCore,
                                        self.searchKeyDatabase.getApiKey(self.__database_name__,
                                        crypto.crypto_getremoteHashIndex(self.cryptoCore)))

        models = crypto.crypto_decrypt(self.cryptoCore,
                                       self.searchKeyDatabase.getSearchKeys(self.__database_name__,
                                       crypto.crypto_getremoteHashIndex(self.cryptoCore)))

        logging.info("get api key  encrypted : %s ", self.searchKeyDatabase.getSearchKeys(self.__database_name__,
                                                     crypto.crypto_getremoteHashIndex(self.cryptoCore)))

        logging.info(" >> decrypted api key :: %s ", api_key.decode("utf-8"))
        logging.info(" >> decrypted models key :: %s ", models.decode("utf-8"))

        self.__init_storing_streamers()

        self.censys_api = censys(api_key,
                                 models.decode("utf-8"))

        try:
            results = self.censys_api.search()
            self._show_reults(results);
            try:
                results_alexa = self.alexa_api_search.search(results)
                self._show_reults(results_alexa);
                logging.info("[SEEKER] %s", self.show_results)
            except :
                logging.info(" error alexa api ");
        except :
            logging.info(" error censys api ")

        self.zoomeye_api = zoomeye(api_key,
                                 models.decode("utf-8"))

        try:
            results = self.zoomeye_api.search()
            self._show_reults(results);
            try:
                results_alexa = self.alexa_api_search.search(results)
                self._show_reults(results_alexa);
                logging.info("[SEEKER] %s", self.show_results)
            except :
                logging.info(" error alexa api ");
        except :
            logging.info(" error zoomeye api ")

        self.shodan_api = shodan_api(api_key.decode("utf-8"),
                                     models.decode("utf-8"))

        try:
            results = self.shodan_api.search()
            #self._show_reults(results);
            try:
                self.alexa_api_search = alexa_api("censys")
                results_alexa = self.alexa_api_search.search(results)
                self._show_reults(results_alexa);
                logging.info("[SEEKER] %s", self.show_results)
            except :
                logging.info(" error alexa api ");
        except :
            logging.info(" error shodan api ");
