from ctypes import *
import ctypes

so_file = 'libcVpnHopper.so'
cVpnHopper = CDLL(so_file)
charptr = POINTER(c_char)

def getMacAddress(ifname):
  func = cVpnHopper.get_hardware_mac_address
  func.argtypes = []
  func.restype  =  charptr
  __ifname__ = ctypes.create_string_buffer(str.encode(ifname))
  result = cVpnHopper.get_hardware_mac_address(__ifname__)
  c_result = ctypes.cast(result,ctypes.c_char_p)
  if (c_result.value != -1):
      return c_result.value;
  else:
      return "C Function failed, check inputs"
