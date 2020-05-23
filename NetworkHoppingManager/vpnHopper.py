import socket
#import openvpn_api.VPN
import logging
import Colorer
from NetworkHoppingManager.cVpnHopper.pycVpnHopper import  pycVpnHopper

class vpnHopper():

    def __init__(self):
        logging.debug(" init network vpnHopper module")
        self.cVpnHopper_instance  = pycVpnHopper()

    def getMacAdddress(self, ifname):
        logging.debug(" get MAC Address of the network device %s", ifname)
        return pycVpnHopper.getMacAddress(self.cVpnHopper_instance, ifname)
#    self.connection = openvpn_api.VPN('localhost', 7505)
