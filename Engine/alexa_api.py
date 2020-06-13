import requests
import json
import logging
from Colorer import colorer
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import socket
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pyvirtualdisplay import Display
import pickle
import os
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from dns import reversename
import ipaddress
import sys

class alexa_api():
    predefined_syntax_basic_url      = "https://www.alexa.com/siteinfo/"
    use_rest_api                     = False;
    visibility                       = True;

    def __init__( self, __api_name__, __engine__):
        self.api_name = __api_name__
        self.searchEngineProxy = __engine__
        logging.info(" api key")

    def _build_urls(self, __url__):
         ip_address = __url__.split('//')[1].split(':')[0]
         reversed_dns = socket.gethostbyaddr(ip_address)
         return self.predefined_syntax_basic_url+'/'+reversed_dns[0]

    def _getPotentialStreamers(self, results):
        search_traffic  = []
        logging.info("Check Potential Streamers :")
        try :
            search_traffic = self.driver.find_element_by_css_selector("#card_topkeywords > section:nth-child(3) > div:nth-child(2) > div:nth-child(2) > div:nth-child(2)")
            logging.info(" >> search traffic  = %s %", search_traffic)
        except :
            logging.error("error page ")
        return search_traffic

    def search(self, results):
#        if(self.api_name != "censys"):
#            return
        logging.debug(" walkthrough the list %s", results)

        # Configuration browser
        logging.debug(" Engine search instance ....")
        self.driver = self.searchEngineProxy.getChromedriverProxy(use_proxy=True)
        logging.debug(" Engine search instance got")
        if (self.visibility):
            self.display = Display(visible=self.visibility, size=(800, 600))
            self.display.start()
        else:
            logging.debug(" no display")
            #self.driver.set_window_size(0,0)

        for self._url_ in results:
            try:
                if (None != self._url_):
                    logging.debug(" url = %s", self._url_)

                    # Configuration browser
                    try :
                        self.driver.implicitly_wait(2)
                        logging.debug(" page reached ");
                        self.driver.implicitly_wait(2)
                        time.sleep(2.4)
                        url = self._build_urls(self._url_)
                        logging.debug("potential server -- streamer : %s ", url)
                        self.driver.get(url)

                        try:
                            countryRank = self.driver.find_element_by_id("CountryRank")
                            logging.info("Country : %s ", str(countryRank.text).replace('\n', ':'))
                        except Exception as err:
                            logging.error(" option not caught error %s  ", str(err));

                        try:
                            WebElement;  totalVisitor = self.driver.find_element_by_id("donutChart");
                            logging.info("Total Element : %s  ", totalVisitor.text)
                        except Exception as err:
                            logging.error(" option not caught error %s  ", str(err));

                    except:
                        print(" page unreachable ...");
                        results    = list(filter(lambda x: x != self._url_, results))
                        #                       self.driver.quit()
                        pass;
#                filtered_results.append(self._url_)
            except Exception as e:
                logging.debug(" error : %s", e)
                self.driver.quit()
                if (self.visibility):
                    self.display.close();
        return results


