import socket
#import openvpn_api.VPN
import logging
import Colorer
import _socket
from _socket import *
import os, sys, io, selectors
from enum import IntEnum, IntFlag
from typing import overload
import sys
import socket
from NetworkHoppingManager.cVpnHopper.pycVpnHopper import  pycVpnHopper
#sys.modules['socket'] = pycVpnHopper

_GLOBAL_DEFAULT_TIMEOUT = object()

create_connection_socket = socket.create_connection

class vpnHopper():

    def __init__(self):
        logging.debug(" init network vpnHopper module")
        self.cVpnHopper_instance  = pycVpnHopper()

    def get_mac_address(self, ifname):
        logging.debug(" get MAC Address of the network device %s", ifname)
        return pycVpnHopper.get_if_mac_address(self.cVpnHopper_instance, ifname)
#    self.connection = openvpn_api.VPN('localhost', 7505)

    def setup_if_conf_selenium(self, ifname):
        logging.debug(" get socket on the network device %s", ifname)
        self.ifname = ifname;
        # patching socket module for selenium.
        #self.create_connection_vpn(socket, ifname)
        socket.create_connection = self.create_connection_vpn

    def setup_if_conf_socket(self, socket, ifname):
        logging.debug(" get socket on the network device %s", ifname)
        self.ifname = ifname;
        # patching socket module for selenium.
        return pycVpnHopper.get_if_conf(self.cVpnHopper_instance, socket, ifname)

    def setup_if_conf(self, socket, ifname):
        logging.debug(" get socket on the network device %s", ifname)
        self.ifname = ifname;
        # patching socket module for selenium.
        self.create_connection_vpn(socket, ifname)
        #socket.create_connection = self.create_connection_vpn

    def create_connection_vpn(address, timeout=_GLOBAL_DEFAULT_TIMEOUT,
                      source_address=None):
        #return create_connection(address, timeout=_GLOBAL_DEFAULT_TIMEOUT, source_address=None)

        host, port = address
        err = None
        for res in getaddrinfo(host, port, 0, SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            sock = None
            try:
                sock = socket(af, socktype, proto)
                 #PATCH tikythera-techs for selenium driver : socket driver.
                setup_if_conf(self.cVpnHopper_instance, sock.fileno(), self.ifname)
                if timeout is not _GLOBAL_DEFAULT_TIMEOUT:
                    sock.settimeout(timeout)
                if source_address:
                    sock.bind(source_address)
                sock.connect(sa)
                 # Break explicitly a reference cycle
                err = None
                return sock

            except error as _:
                err = _
                if sock is not None:
                    sock.close()

        if err is not None:
            try:
                raise err
            finally:
                 # Break explicitly a reference cycle
                err = None
        else:
            raise error("getaddrinfo returns an empty list")



