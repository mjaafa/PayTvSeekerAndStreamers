from ctypes import *
import ctypes
import os
import Colorer
import logging

class pycVpnHopper():

    def __init__(self):
        logging.debug(" current directory : %s", os.getcwd())
        so_file = os.getcwd() + '/libcVpnHopper.so'
        self.cVpnHopper = CDLL(so_file)
        self.charptr = POINTER(c_char)

    def get_if_mac_address(self, ifname):
        func = self.cVpnHopper.get_hardware_mac_address
        func.argtypes = []
        func.restype  =  self.charptr
        __ifname__ = ctypes.create_string_buffer(str.encode(ifname))
        result = self.cVpnHopper.get_hardware_mac_address(__ifname__)
        c_result = ctypes.cast(result,ctypes.c_char_p)
        if (c_result.value != -1):
            return c_result.value;
        else:
            return None

    def get_if_conf(self, __socket__, ifname):
        func = self.cVpnHopper.get_interface_configuration
        func.argtypes = [c_int, self.charptr]
        func.restype  = c_int
        __ifname__ = ctypes.create_string_buffer(str.encode(ifname))
        c_result = self.cVpnHopper.get_interface_configuration(__socket__, __ifname__)
        print(" result ", c_result)
        if (c_result != -1):
            return c_result;
        else:
            return None;
