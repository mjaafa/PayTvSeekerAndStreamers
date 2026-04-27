import logging


class alexa_api:
    """Deprecated Alexa ranking enrichment placeholder.

    The legacy Alexa Internet site-ranking service is no longer available.  This
    class is kept only so old imports do not fail.  It returns the input list
    unchanged.
    """

    use_rest_api = False
    visibility = False

    def __init__(self, __api_name__, __engine__=None):
        self.api_name = __api_name__
        self.searchEngineProxy = __engine__
        logging.info("Alexa enrichment is deprecated and disabled")

    def search(self, results):
        logging.warning("Alexa enrichment skipped: service is deprecated")
        return results or []
