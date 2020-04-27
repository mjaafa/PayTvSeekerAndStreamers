import shodan
import logging

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
        logging.info("search the keywords via shodan API")
        urld = []
        for __keyword__ in self.api.keywords.split(','):
            logging.info(" models search = %s", __keyword__)
            try:
                results = self.api.search(__keyword__)
                for result in results['matches']:
                    logging.debug("results : %s ", result['data'])
                    # logging.debug("results : %s ", result)

                    if (result['port'] == 80):
                        urld.append('http://{}'.format(result['ip_str']) + ':' + str(result['port']))
                        logging.debug("URL %s ", urld)
                    elif (result['port'] == 443):
                        urld.append('https://{}'.format(result['ip_str']) + ':' + str(result['port']))
                        logging.debug("URL %s", urld)
                    else:
                        urld.append('http://{}'.format(result['ip_str']) + ':' + str(result['port']))
                        logging.debug("URL %s", urld)
            except:
                logging.error(" Error : cannot walkthrough the list")

            return urld;
