import requests
import json
import logging
import Colorer
from bs4 import BeautifulSoup
## main program emerald hack ###
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import socket
#from goto import goto, label
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pyvirtualdisplay import Display
import pickle
import os
desired_capabilities = DesiredCapabilities.FIREFOX.copy()
desired_capabilities['acceptInsecureCerts'] = True
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from dns import reversename
import ipaddress
import sys

class alexa_api():
    predefined_syntax_basic_url      = "https://www.alexa.com/siteinfo"
    use_rest_api                     = False;
    visibility                       = False;

    def __init__( self, __api_name__):
        self.api_name = __api_name__
        logging.info(" api key")

    def _build_urls(self):
         return self.predefined_syntax_basic_url

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
        page_results = []
        urls = self._build_urls()
        if(self.api_name != "censys"):
            return

        try:
            if (None != self.url):
                #response = requests.get(url, timeout=30, verify=False)  # To execute get request
                #logging.debug("http code ", response.status_code)  # To logging.error http response code
                #logging.debug(" response : %s", BeautifulSoup(response.content))  # To logging.error http response code
                logging.debug("url : %s ", self.url)
                self.display = Display(visible=self.visibility, size=(800, 600))
                self.display.start()

                # Configuration browser
                self.profile = webdriver.FirefoxProfile()
                self.profile.accept_untrusted_certs = True
                self.driver = webdriver.Firefox(firefox_profile=self.profile)
                self.desired_capabilities = DesiredCapabilities.FIREFOX.copy()
                self.desired_capabilities['acceptInsecureCerts'] = True
#                    driver = webdriver.Firefox(capabilities=desired_capabilities)
#                    driver.accept_untrusted_certs = True
#                    driver.acceptSslCerts = True
                self.driver.set_window_size(1024, 768)
                try :
                    self.driver.implicitly_wait(20)
                    logging.debug(" page reached ");
                    time.sleep(2.4)
                    #software_names = "Firefox"
                    #operating_systems = "LINUX"
                    #user_agent_rotator = UserAgent(software_names=software_names,
#                                                       operating_systems=operating_systems, limit=1000)
                    #user_agent = user_agent_rotator.get_random_user_agent()
                    #self.profile.set_preference("general.useragent.override", user_agent)
                    pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
                    #cookies = self.driver.manage().getCookies();
                    #self.driver.manage().getCookieNamed(cookies);
                    #self.driver.manage().addCookie(cookies);
                    self.driver.get(self.url)
                    search = self.driver.find_element_by_xpath("//input[starts-with(@class, '.InputAutocomplete-singlesite-0')]")
                    search.clear()
                    for result in results:
                        try :
                            ip = ipaddress.ip_address(sys.argv[1])
                            domain_address = reversename.from_address(ip)
                            search.send_keys(domain_address)
                            auto_complete = self.driver.find_elements_by_xpath("//li[starts-with(@class, '.InputAutocomplete-singlesite-0')]")
                            auto_complete[0].click()
                            #                element_index = self.driver.find_elements_by_css_selector("div.SearchResult:nth-child(") + index_element + ")"
                            #                logging.info(" >> element_index = %s ", element_index)
                           #                results = self.driver.find_elements_by_css_selector(element_index);
                            cookies = pickle.load(open("cookies.pkl", "rb"))
                            for cookie in cookies:
                                self.driver.add_cookie(cookie)
                                page_results = self._getPotentialStreamers()
                                logging.info("Printed immediately.")
                                time.sleep(2.4)
                        except:
                            logging.info('%s is a correct IP%s address.', (ip, ip.version))
                except:
                    print(" page unreachable ...");
                    self.driver.close()
                    pass;

        except Exception as e:
            logging.debug(" error : %s", e)

                # print(response.text['Name'], " has a password : ", response.text['HasPassword'])  # To print formatted JSON response
#                try:
#                    json_results = json.loads((response.text))
#                except ValueError:  # includes simplejson.decoder.JSONDecodeError
#                    logging.debug('Decoding JSON has failed')
#                    continue;
#                    pass;

#        for distro in json_results:
#            print("User =  ", distro['Name']);
#            print("Has Password =  ", distro['HasPassword']);
#
#            if (result['port'] == 80):
#                print("clear port ")
#
#            if (distro['HasPassword'] == False):
#                if (result['port'] == 80):
#                    driver = webdriver.Firefox(capabilities=desired_capabilities)
#                    driver.accept_untrusted_certs = True
#                    driver.acceptSslCerts = True
#                    urld = 'http://{}'.format(result['ip_str']) + ':' + str(result['port'])
#                    print("URL ", urld)
#                    driver.set_window_size(1024, 768)
#                    try:
#                        driver.implicitly_wait(60)
#                        driver.get(urld)
#                    except:
#                        print(" page unreachable ...");
#                        continue;
#                        pass;
#                elif (result['port'] == 443):
#                    driver = webdriver.Firefox()
#                    urld = 'https://{}'.format(result['ip_str']) + ':' + str(result['port'])
#                    print("URL ", urld)
#                    driver.set_window_size(1024, 768)
#                    try:
#                        driver.implicitly_wait(30)
#                        driver.get(urld)
#                    except:
#                        print(" page unreachable ...");
#                        continue;
#                        pass;
#                else:
#                    driver = webdriver.Firefox()
#                    urld = 'http://{}'.format(result['ip_str']) + ':' + str(result['port'])
#                    print("URL ", urld)
#                    driver.set_window_size(1024, 768)
#                    try:
#                        driver.implicitly_wait(30)
#                        driver.get(urld)
#                    except:
#                        print(" page unreachable ...");
#                        continue;
#                        pass;

#            except requests.exceptions.HTTPError as errh:
#                logging.error("Http Error:", errh)
#            except requests.exceptions.ConnectionError as errc:
#                logging.error("Error Connecting:", errc)
#            except requests.exceptions.Timeout as errt:
#                logging.error("Timeout Error:", errt)
#            except requests.exceptions.RequestException as err:
#                logging.error("OOps: Something Else", err)
