'''
Created on 2020. 6. 04.

@author: KangSH
'''

import sys
import os
import binascii

# Flash Programming Start Address
#fl_addr = 0x01050000  # siwthch1
fl_addr = 0x01090000 # switch2
if __name__ == '__main__':

    # path = os.getcwd()
    # excelist = glob.glob(path + '\\' + '*.img')
    # print(excelist)
    # read_length = int(sys.argv[1])
    read_length = 28
    # img_name  = sys.argv[2]

    if fl_addr == 0x01050000:
        img_name = "bcm89530c1_br100_evk_avb-switch_erika_S1.img"
        srec_name = img_name.split('.')[0] + '_sw1.srec'
    elif fl_addr == 0x01090000:
        img_name = "bcm89530c1_br100_evk_avb-switch_erika_S2.img"
        srec_name = img_name.split('.')[0] + '_sw2.srec'

    with open(img_name, 'rb') as img:
        with open(srec_name, 'w') as srec:

            # Header Record
            srec.write('S017000062636D383935333063315F62723130305F65766BB0\n')

            while True:

                b = img.read(read_length)
                if b == '': break;

                data_len = len(b) + 5  # Data Length + Address Length + Checksum Length
                srec.write('S3' + '{:02x}'.format(data_len))  # Data Record, 33-bytes Record Count

                # Calculate Checksum
                # Address
                line_addr = '{:08x}'.format(fl_addr).upper()
                a_list = [line_addr[i:i + 2] for i in range(0, len(line_addr), 2)]

                # Data
                line = binascii.b2a_hex(b)
                d_list = [line[i:i + 2] for i in range(0, len(line), 2)]

                chksum = data_len

                # Add
                for hex_str in a_list:
                    chksum += int(hex_str, 16)

                for hex_str in d_list:
                    chksum += int(hex_str, 16)

                # Compute one's complement of least significant byte
                chksum = hex(chksum)[-2:]
                chksum = hex(int(chksum, 16) ^ 0xFF)

                # Write to .srec file
                srec.write(line_addr)  # Address
                srec.write(line)  # Data
                srec.write('{:02x}'.format(int(chksum, 16)).upper())  # Checksum
                srec.write('\n')

                fl_addr += 0x1C

            # Start Address Record (Flash Program Purpose Only)
            srec.write('S70500000000FA')

    print
    "make_sre.py: Created '" + srec_name + "'"