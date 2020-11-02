import os
import binascii
import shutil
import re

Curruntpath = os.getcwd()

filepath = os.path.join(Curruntpath, 'file')

switch1_file = "bcm89530c1_br100_evk_avb-switch_erika_S1.img"
switch2_file = "bcm89530c1_br100_evk_avb-switch_erika_S2.img"

def Switch_BinaryToSre(img_path):
    read_length = 28
    img_name = os.path.basename(img_path)
    if img_name == switch1_file:
        fl_addr = 0x01050000 #  MCU flash start address of switch1
        srec_name = img_name.split('.')[0] + '_sw1.srec'
    elif img_name == switch2_file:
        fl_addr = 0x01090000 # MCU flash start address of switch2
        srec_name = img_name.split('.')[0] + '_sw2.srec'

    with open(img_path, 'rb') as img:
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

    print("make_sre.py: Created '" + srec_name + "'")


    if (os.path.exists(Curruntpath + '\\'+srec_name)) : # created file is moved to 'file' foler for integrating
        src_dir = Curruntpath + '\\'+ srec_name
        des_dir = filepath + '\\'+ srec_name
        shutil.move(src_dir, des_dir)
        return srec_name
    else :
        print("no creat Switch1 file")

def MCU_File_serch(path):
    filelist = os.listdir(path)

    for filename in filelist:
        m = re.match('.+swp.*[.]sre$', filename)
        if m:
            #rint('match found', m.group())
            return m.group()
        else:
            pass

def file_integrate(path, switch1, switch2, MCU):
    with open(os.path.join(path,switch1), 'r') as f:
       Switch1_image = f.read()

    with open(os.path.join(path,switch2), 'r') as f:
       Switch2_image = f.read()

    with open(os.path.join(path,MCU), 'r') as f:
        MCU_image = f.read()

    integrate_name = MCU.split('.')[0] + "_S1S2.sre"
    #print(integrate_name)
    with open(os.path.join(path, integrate_name), 'w') as f:
        integrated_image = MCU_image + Switch1_image + Switch2_image
        f.write(integrated_image)
        print("%s file integrating finish"% (integrate_name))

def main():
    if(os.path.isdir(filepath)):
        print("OK")
        if(os.path.exists(filepath + "\\" + switch1_file)):
            print("switch1 file exist")
            img_path = filepath + "\\" + switch1_file
            Switch1Name = Switch_BinaryToSre(img_path)
            if (os.path.exists(filepath + "\\" + switch2_file)):
                print("switch2 file exist")
                img_path2 = filepath + "\\" + switch2_file
                Switch2Name = Switch_BinaryToSre(img_path2)

                MCU_file_name = MCU_File_serch(filepath) # MCU File serching

                if MCU_file_name == None:
                    print("Please add to MCU file")
                else:
                    print("MCU file exist")
                    file_integrate(filepath, Switch1Name, Switch2Name, MCU_file_name)

            else:
                print("Please add to switch1 file, Be sure that file nane -> bcm89530c1_br100_evk_avb-switch_erika_S2.img")
        else:
          print("Please add to switch1 file, Be sure that file nane -> bcm89530c1_br100_evk_avb-switch_erika_S1.img")
    else:
        print("you need to put on integrated file after creat folder")
        os.makedirs(filepath)

if __name__ == '__main__':
    main()
