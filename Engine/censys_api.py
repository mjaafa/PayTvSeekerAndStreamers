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

desired_capabilities = DesiredCapabilities.FIREFOX.copy()
desired_capabilities['acceptInsecureCerts'] = True

class censys():

    predefined_syntax_basic_url      = "https://censys.io/ipv4?q="
    predefined_filter_443_code       = "+443.http.get.status_code%3A+200+"
    predefined_filter_80_code        = "80.http.get.status_code%3A200+"
    predefined_filter_443_line       = "443.http.get.status_line%3A+200+"
    predefined_filter_80_line        = "80.http.get.status_line%3A200"
    use_rest_api                     = False;
    visibility                       = True;

    def __init__( self, __api_key__, __models__):
        __api_key = str(__api_key__).split(",")[1]
        logging.info(" api key : %s ", __api_key.split("@")[1])
        self.api_key = __api_key.split("@")[1]
        self.secret  = __api_key.split("@")[2]
        logging.debug(" API KEY : %s ", self.api_key)
        logging.debug(" secret KEY : %s ", self.secret)
        if (None == self.api_key or None == self.secret):
            self.use_rest_api = False;

        logging.info(" censys api init")
        self.api_keywords = __models__
        logging.info(" >> decrypted models key :: %s ", __models__)

    def _build_urls(self):
        url_built = []
        for __keyword__ in self.api_keywords.split(','):
            logging.info(" models search = %s", __keyword__)
            url = self.predefined_syntax_basic_url  + __keyword__.replace(" ","+")  + \
                  self.predefined_filter_443_code  +  self.predefined_filter_80_code  + \
                  self.predefined_filter_443_line + self.predefined_filter_80_line
            logging.debug(" url :: %s ", url);
            url_built.append(url)

        logging.debug(" url :: %s ", url_built);
        return url_built

    def _getPotentialStreamers(self):
        line  = []
        logging.info("Check Potential Streamers :")
        #   / html / body / div[1] / div[2] / div / div / div / div[5] / div / div[2] / div / div[25]
        next_page = self.driver.find_elements_by_css_selector(".hover > a:nth-child(1)")
        try :
            while None != next_page:
                results = self.driver.find_elements_by_css_selector("#resultset");
                for line in results[0].text.split('\n'):
                    #stripped_line = line.strip()
                    logging.debug("Search info : %s ", line)

                next_page = self.driver.find_elements_by_css_selector(".hover > a:nth-child(1)")
                if None == next_page:
                    self.driver.close()
                    return line
                self.driver.find_element_by_css_selector('.hover > a:nth-child(1)').click()
        except :
            logging.error("error page ")
        return line

    def search(self):
        __urls__ = self._build_urls()
        logging.info(" urls : %s ", __urls__)
        page_results = []

        for url in __urls__:
            try:
                if (None != url):
                    #response = requests.get(url, timeout=30, verify=False)  # To execute get request
                    #logging.debug("http code ", response.status_code)  # To logging.error http response code
                    #logging.debug(" response : %s", BeautifulSoup(response.content))  # To logging.error http response code
                    logging.debug("url : %s ", url)
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
                        self.driver.implicitly_wait(60)
                        logging.debug(" page reached ");
                        time.sleep(20.4)
                        cookies = self.driver.manage().getCookies();
                        self.driver.manage().getCookieNamed(cookies);
                        self.driver.manage().addCookie(cookies);
                        self.driver.get(url)
                        page_results = self._getPotentialStreamers()
                        print("Printed immediately.")
                        time.sleep(31.4)

                    except:
                        print(" page unreachable ...");
                        continue;
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
