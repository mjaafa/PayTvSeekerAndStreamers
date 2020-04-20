#!/usr/bin/env python
#
# shodan_ips.py
# Search SHODAN and print a list of IPs matching the query
#
# Author: achillean

from time import sleep
import shodan
import sys
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
from Database.database import database
from CustomCrypto.crypto import crypto
import hashlib
import json
from pprint import pprint
import os

class seeker():
    # Rocket simulates a rocket ship for a game
    #  or a physics simulation.
    visibility = False

    def __init__(self):
        # init webdriver
        self.display = Display(visible=self.visibility, size=(800, 600))
        self.display.start()

        # Configuration browser
        self.profile = webdriver.FirefoxProfile()
        self.profile.accept_untrusted_certs = True
        self.driver = webdriver.Firefox(firefox_profile=self.profile)

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
        # remote encrypt / decrypt.
        self.cryptoCore = crypto('https://localhost/','127.0.0.1', 443)
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

    def init_config(self):
        if (None == self.__init_storing_search_keys()):
            logging.error(" Error configuration cannot be completed ")
            return None;
        else:
            logging.info(" Init Configuration OK ")
            return self;

    def search(self):
        #engine init :: from remote :::::
        logging.info(" >> api key :: %s ", crypto.crypto_getMiscDataApiKey(self.cryptoCore))
        #api_key = crypto.crypto_decrypt(self.cryptoCore,crypto.crypto_getMiscDataApiKey(self.cryptoCore))
        api_key = crypto.crypto_decrypt(self.cryptoCore,
                                        self.searchKeyDatabase.getApiKey(self.__database_name__,
                                        crypto.crypto_getremoteHashIndex(self.cryptoCore)))

        models = crypto.crypto_decrypt(self.cryptoCore,
                                       self.searchKeyDatabase.getSearchKeys(self.__database_name__,
                                       crypto.crypto_getremoteHashIndex(self.cryptoCore)))

        logging.info(" >> decrypted api key :: %s ", api_key.decode("utf-8"))
        self.api = shodan.Shodan(api_key.decode("utf-8"))
####        logging.info(" >> api key :: %s ", crypto.crypto_getMiscDataModels(self.cryptoCore))
#        models = crypto.crypto_decrypt(self.cryptoCore,crypto.crypto_getMiscDataModels(self.cryptoCore))
        logging.info(" >> decrypted models key :: %s ", models.decode("utf-8").split(','))
        for __keyword__ in models.decode("utf-8").split(','):
            logging.info(" models search = %s", __keyword__)
            try:
                results = self.api.search(__keyword__)
                for result in results['matches']:
                    print('IP: {}'.format(result['ip_str']))
                    print('IP: {}'.format(result))
            except:
                logging.error(" error cannot reach search engine ")
        #ciphering_keys = self.searchKeyDatabase.getKeys(self.__database_name__)
        #logging.info(" >> ciphering keys %s ", ciphering_keys)
#driver_emby = webdriver.Firefox()
#
## Loop through the matches and print each IP
#for service in result['matches']:
#                print "**********************************"
#                print service['ip_str'];
#                print service['location'];
#                print service['port']
#                driver.implicitly_wait(10)
#                #if "186.229.29.210" in str(service['ip_str']):
#                #    continue;
#                if "443" in str(service['port']):
#                    url = "https://"+str(service['ip_str'])+":"+str(service['port'])+"/emby/users/public?format=json";
#                    secured=True;
#                else:
#                    url = "http://"+str(service['ip_str'])+":"+str(service['port'])+"/emby/users/public?format=json";
#                    secured=False;
#                print url
#               # print ("URL built is :", url.split(" ")[1])
#                try:
#                    driver.get(url);
#                except:
#                    continue;
#                detectingWeakUser();
#                torrentCheck="https://iknowwhatyoudownload.com/en/peer/?ip="+str(service['ip_str']);
#                driver.get(torrentCheck);
#                checkIfTargetusesTorrent();
#                if(Weak_user==True):
#                    if (True == secured):
#                        urld = "https://"+str(service['ip_str'])+":"+str(service['port']);
#                    else:
#                        urld = "http://"+str(service['ip_str'])+":"+str(service['port']);
#                    #driver_emby.set_window_size(1024, 768)
#                    #driver_emby.get(urld)
#                    Weak_user=False;
#                    print("URL ", urld)
#                #sleep(60);
#                #
#
#driver.close();
