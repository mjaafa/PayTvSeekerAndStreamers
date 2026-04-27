#!/usr/bin/env python
import logging
from logging.config import fileConfig

from Colorer import colorer
from Seeker.seeker import seeker

fileConfig('configuration/log_conf.ini')
logger = logging.getLogger()


def __boot__():
    print(" ")
    logging.info(" # Booting The modules # ")
    logging.info(" * Booting Seeker module : ")
    instance = seeker()
    instance.set_browser_visibility(False)
    logging.info(
        "    |->  Booting  component seeker browser        : %s",
        "Visible" if instance.get_browser_visibility() else "Hidden",
    )
    if instance.init_config() is not None:
        logging.info("    |->  Booting  component Seeker configuration : Done")
        return instance
    logging.info("    |->  Booting  component Seeker configuration : NOK ")
    return None


def main():
    logging.info(" *** PayTV BlackMamba seeker ***")
    instance = __boot__()
    if instance is None:
        return
    instance.search()


if __name__ == "__main__":
    import sys
    main()
    sys.exit(0)
