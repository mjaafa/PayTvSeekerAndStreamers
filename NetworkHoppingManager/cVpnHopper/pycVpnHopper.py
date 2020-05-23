from ctypes import *

so_file = 'libcVpnHopper.so'
cVpnHopper = CDLL(so_file)

def getMacAddress(ifname):
  c_return = cVpnHopper.get_hardware_mac_address(ifname)
  if (c_return != -1):
      return c_return
  else:
      return "C Function failed, check inputs"
