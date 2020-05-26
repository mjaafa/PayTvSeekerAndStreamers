import socket
#import openvpn_api.VPN
import logging
from Colorer import colorer
import _socket
from _socket import *
import os, sys, io, selectors
from enum import IntEnum, IntFlag
from typing import overload
import sys
import socket
from urllib3.util import connection

from NetworkHoppingManager.cVpnHopper.pycVpnHopper import  pycVpnHopper
#sys.modules['socket'] = pycVpnHopper

_GLOBAL_DEFAULT_TIMEOUT = object()

urllib3_custom_connection = connection.create_connection

class vpnHopper():

    def __init__(self):
        logging.debug(" init network vpnHopper module")
        self.cVpnHopper_instance  = pycVpnHopper()

    def get_mac_address(self, ifname):
        logging.debug(" get MAC Address of the network device %s", ifname)
        return pycVpnHopper.get_if_mac_address(self.cVpnHopper_instance, ifname)

    def setup_if_conf_socket(self, socket, ifname):
        logging.debug(" get socket on the network device %s", ifname)
        self.ifname = ifname;
        # patching socket module for urllib3.
        return pycVpnHopper.get_if_conf(self.cVpnHopper_instance, socket, ifname)

    def setup_if_conf(self, socket, ifname):
        logging.debug(" get socket on the network device %s", ifname)
        self.ifname = ifname;
        # patching socket module for urlib3.
        return self.setup_if_conf_socket(socket, self.ifname)

    def create_connection_vpn(
        self,
        address,
        timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
        source_address=None,
        socket_options=None):

        host, port = address
        if host.startswith("["):
            host = host.strip("[]")
        err = None
        # Using the value from allowed_gai_family() in the context of getaddrinfo lets
        # us select whether to work with IPv4 DNS records, IPv6 records, or both.
        # The original create_connection function always returns all records.
        family = connection.allowed_gai_family()

        for res in socket.getaddrinfo(host, port, family, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            sock = None
            try:
                sock = socket.socket(af, socktype, proto)

                #PATCH antikythera-techs for urllib3 driver : socket driver.
                if(host != "127.0.0.1"):
                    ret = pycVpnHopper.get_if_conf(self.cVpnHopper_instance, sock.fileno(), self.ifname)
                    if ret is None:
                        sock.close()
                        return;

                # If provided, set socket level options before connecting.
                connection._set_socket_options(sock, socket_options)

                if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                    sock.settimeout(timeout)
                if source_address:
                    sock.bind(source_address)
                sock.connect(sa)
                return sock

            except socket.error as e:
                err = e
                if sock is not None:
                    sock.close()
                    sock = None

        if err is not None:
            raise err

        raise socket.error("getaddrinfo returns an empty list")

    def setup_if_conf_urllib3(self, ifname):
        logging.debug(" get socket on the network device %s", ifname)
        self.ifname = ifname;
        # patching socket module for urllib3.
        connection.create_connection = self.create_connection_vpn
        logging.debug(" get socket on the network device %s", ifname)
