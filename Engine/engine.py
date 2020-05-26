import signal
import threading
import os
from multiprocessing import Process
import sys
from Engine.shodan_api import shodan_api
from Engine.censys_api import censys
from Engine.zoomeye_api import zoomeye
from oss.customProxySock.customProxySock import customProxySock
import logging

class engine():
    proxyUsername = 'username'
    proxyPassword = 'password'

    def __init__(self):
        logging.debug("starting Search Engine");
        pass

    def configureProxy(self):
        logging.debug("configure proxy for selenium");
        self.proxyProcessor = customProxySock(1080, self.proxyUsername, self.proxyPassword)

    def startProxy(self):
        pass
        ## threading maybe used to avoid blocking
#        customProxySock.launcher(self.proxyProcessor)
        self.threadProxy = threading.Thread(target=customProxySock.launchProxySock,
                                            name="customProxySock.launchProxySock",args=(self.proxyProcessor,))
#        self.threadProxy.start()
#        self.threadProxy = Process(target=customProxySock.launcher(self.proxyProcessor))
        self.threadProxy.setDaemon( True)
        self.threadProxy.start()

    def stopProxy(self):
        logging.debug("Stopping Engine ")
#        sys.exit(0)
        PID=self.threadProxy.ident
        #os.kill(PID,signal.SIGTERM)
        self.threadProxy.join()
        customProxySock.shutdownProxySock(self.proxyProcessor)
