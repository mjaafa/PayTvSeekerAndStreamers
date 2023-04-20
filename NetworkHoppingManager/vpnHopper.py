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
import mmap
import enum
import re
#import massedit
import hashlib
import base64
from cryptography.hazmat.primitives import kdf
from cryptography.hazmat.primitives import hashes
from ast import literal_eval
import sys
#import sh
import subprocess

class vpnConfiguration:
    use_interfaces    = "interfaces_use"
    ignore_interfaces = "interfaces_ignore"

from NetworkHoppingManager.cVpnHopper.pycVpnHopper import  pycVpnHopper

urllib3_custom_connection = connection.create_connection

class network_interfaces :
    net_interface_1 = "wlp59s0"
    net_interface_2 = "enp0s20f0u5"

CONFIGURATION_VPN_FILE="strongswan.conf"

class vpnHopper():

    def __init__(self):
        logging.debug(" init network vpnHopper module")
        self.cVpnHopper_instance  = pycVpnHopper()

    def vpnBounceConfManagement(self, device="wlp59s0"):
        filenames = ['/etc/strongswan.conf']
        if (device is network_interfaces.net_interface_1):
            subprocess.run(["ipsec", "down", "protonvpn-connection"], stdout=subprocess.DEVNULL)
            logging.debug(" patching configuration file for use %s ", network_interfaces.net_interface_1)
            massedit.command_line([CONFIGURATION_VPN_FILE, "-w", "-e", "re.sub('.*interfaces_use=.*', '        interfaces_use=wlp59s0', line)",     "-w", "-s", "/etc/", CONFIGURATION_VPN_FILE])
            subprocess.run(["ipsec", "up", "protonvpn-connection"], stdout=subprocess.DEVNULL)
        elif (device is network_interfaces.net_interface_2):
            subprocess.run(["ipsec", "down", "protonvpn-connection"], stdout=subprocess.DEVNULL)
            #sh.run(['ipsec down protonvpn-connection'])
            logging.debug(" patching configuration file for use %s ", network_interfaces.net_interface_2)
            massedit.command_line([CONFIGURATION_VPN_FILE, "-w", "-e", "re.sub('.*interfaces_use=.*', '        interfaces_use=enp0s20f0u5', line)", "-w", "-s", "/etc/", CONFIGURATION_VPN_FILE])
            subprocess.run(["ipsec", "up","protonvpn-connection"], stdout=subprocess.DEVNULL)
        else:
            logging.debug(" no device found for patching interface hopping ")

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
