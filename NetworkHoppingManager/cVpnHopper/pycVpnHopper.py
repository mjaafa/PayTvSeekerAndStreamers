from ctypes import *
import ctypes

class pycVpnHopper():

    def __init__(self):
        so_file = 'libcVpnHopper.so'
        self.cVpnHopper = CDLL(so_file)
        self.charptr = POINTER(c_char)
        print("pycVpnHopper : init")

    def getMacAddress(self, ifname):
        func = self.cVpnHopper.get_hardware_mac_address
        func.argtypes = []
        func.restype  =  self.charptr
        __ifname__ = ctypes.create_string_buffer(str.encode(ifname))
        result = self.cVpnHopper.get_hardware_mac_address(__ifname__)
        c_result = ctypes.cast(result,ctypes.c_char_p)
        if (c_result.value != -1):
            return c_result.value;
        else:
            return "C Function failed, check inputs"
