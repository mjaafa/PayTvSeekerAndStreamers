import shodan
import logging
from Colorer import colorer

class shodan_api():
    def __init__( self, __api_key__, __models__):
        logging.info(" shodan api init")
        __api_key = str(__api_key__).split(",")[0]
        logging.info(" api key : %s ", __api_key.split("@")[1])
        self.api_key = __api_key.split("@")[1]
        logging.debug(" API KEY : %s ", self.api_key)
        self.api = shodan.Shodan(self.api_key)
        self.api.keywords = __models__
        logging.info(" >> decrypted models key :: %s ", __models__)

    def search(self):
        logging.info("search the keywords via shodan API %s", self.api.keywords)
        urld = []
        try:
            for __keyword__ in self.api.keywords.split(','):
                logging.info(" models search = %s", __keyword__)
                try:
                    results = self.api.search(__keyword__)
                    #logging.info(" matches : ", results['matches'])

                    for result in results['matches']:
                        logging.debug("results : %s ", result['ip_str'])

                        if (result['port'] == 80):
                            urld.append('http://{}'.format(result['ip_str']) + ':' + str(result['port']))
                        elif (result['port'] == 443):
                            urld.append('https://{}'.format(result['ip_str']) + ':' + str(result['port']))
                        else:
                            urld.append('http://{}'.format(result['ip_str']) + ':' + str(result['port']))
                except:
                    logging.error(" Error : cannot walkthrough the list")
        except:
            logging.error(" Error : cannot walkthrough the list")

        logging.debug("URL %s", urld)
        return urld;
