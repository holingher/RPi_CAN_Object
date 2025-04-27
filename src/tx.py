import can
import e2e
import time
import os
import platform
from datetime import datetime

os_name = 'Windows'
# Getting the current date and time
dt = datetime.now()
# getting the timestamp
ts = datetime.timestamp(dt)
################# TX ################
# 0x200
PID_VEHMOTIONSTATE       = 0x200
data_200_tx_msg = bytearray(b"\x00\x00\x00\xe0\x3f\xe0\x3f\xe0\x3f\x00\x80\x00\x00\x00\x80\x00\x24\x42\x3f\x00\x00\x80\x7f\x80\x7f\x80\x7f\x80\x7f\x24\x24\x00\x04\x24\x24\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
length_200 = len(data_200_tx_msg) - 2
offset_200 = 0
data_id_200 = 0xA33

# 0x210
PID_CARCONFIG       = 0x210
data_210_tx_msg = bytearray(b"\x00\x00\x00\x09\x00\x00\x00\x00\x01\x03\x00\x00")
length_210 = len(data_210_tx_msg)
# 0x210 CarConfig
data_210_tx_msg_carConfig = bytearray(b"\x00\x00\x00\x09\x00")
length_210_carConfig = len(data_210_tx_msg_carConfig) - 2
offset_210_carConfig = 0
data_id_210_carConfig = 0xA35
# 0x210 PowerMode
data_210_tx_msg_PowerMode = bytearray(b"\x00\x00\x00\x01")
length_210_PowerMode = len(data_210_tx_msg_PowerMode) - 2
offset_210_PowerMode = 0
data_id_210_PowerMode = 0xD0B

# 0x220
PID_GLOBALSNAPSHOT        = 0x220
data_220_tx_msg = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
length_220 = len(data_220_tx_msg) - 2
offset_220 = 0
data_id_220 = 0xD1C

# 0x230
PID_VEHMODES        = 0x230
data_230_tx_msg = bytearray(b"\x00\x00\x00\xf8\x08")
length_230 = len(data_230_tx_msg) - 2
offset_230 = 0
data_id_230 = 0xA47

# 0x240
PID_FUNCINFO        = 0x240
data_240_tx_msg = bytearray(b"\x00\x00\x00\x00")
length_240 = len(data_240_tx_msg) - 2
offset_240 = 0
data_id_240 = 0xB7A

if(os_name != 'Windows'):
    print('Bring up CAN0....')
    os.system("sudo ifconfig can0 down")
    time.sleep(0.1)
    os.system("sudo ip link set can0 up type can bitrate 500000 dbitrate 2000000 restart-ms 1000 berr-reporting on fd on")
    time.sleep(0.1)
    can_bus = can.interface.Bus(channel='can0', interface='socketcan', bitrate=500000, data_bitrate=2000000, fd=True)
elif(os_name == 'Windows'):
    print('Bring up CAN0....')
    can_bus = can.interface.Bus(channel='vcan0', interface='virtual', bitrate=500000, data_bitrate=2000000, fd=True)
time.sleep(0.1)
print('Ready')

period = 0.06
os_name = platform.system()

data_210_tx_msg_carConfig = data_210_tx_msg[:5]
data_210_tx_msg_PowerMode = data_210_tx_msg[5:] 

##############################################################
def process_200(ts):
    # Send Vehicle motion state
    e2e.p05.e2e_p05_protect(data=data_200_tx_msg,
                            length=length_200,
                            offset=offset_200,
                            data_id=data_id_200,
                            increment_counter=True)
    #print('data_200_tx_msg crc:')
    #print(data_200_tx_msg.hex()) 
    msg_200 = can.Message(arbitration_id=PID_VEHMOTIONSTATE, 
                        data=data_200_tx_msg, 
                        is_extended_id=False, 
                        dlc=len(data_200_tx_msg), 
                        is_fd=True,
                        timestamp=ts)
    try:
        can_bus.send(msg=msg_200)
        print("Tx:  {}".format(msg_200))
    except can.CanError:
        print("Message NOT sent")
         
##############################################################
def process_210(ts):  
    # Send a CarConfig
    e2e.p05.e2e_p05_protect(data=data_210_tx_msg_carConfig,
                            length=length_210_carConfig,
                            data_id=data_id_210_carConfig,
                            offset=offset_210_carConfig,
                            increment_counter=True)
    e2e.p05.e2e_p05_protect(data=data_210_tx_msg_PowerMode,
                                    length=length_210_PowerMode,
                                    data_id=data_id_210_PowerMode,
                                    offset=offset_210_PowerMode,
                                    increment_counter=True)
    data_210_tx_msg = data_210_tx_msg_carConfig + data_210_tx_msg_PowerMode  
    #print('data_210_tx_msg crc:')
    #print(data_210_tx_msg.hex())
    msg_210 = can.Message(arbitration_id=PID_CARCONFIG, 
                                    data=data_210_tx_msg, 
                                    is_extended_id= False, 
                                    dlc=len(data_210_tx_msg), 
                                    is_fd=True,
                                    timestamp=ts)
    try:
        #can_bus.send_periodic(msgs = message_CarConfig, period = 0.06 )
        can_bus.send(msg=msg_210)
        print("Tx:  {}".format(msg_210))
    except can.CanError:
        print("Message NOT sent") 
        
##############################################################
def process_220(ts): 
        # Send Global Snapshot
        e2e.p05.e2e_p05_protect(data=data_220_tx_msg,
                                length=length_220,
                                offset=offset_220,
                                data_id=data_id_220,
                                increment_counter=True)
        #print('data_220_tx_msg crc:')
        #print(data_220_tx_msg.hex()) 
        msg_220 = can.Message(arbitration_id=PID_GLOBALSNAPSHOT, 
                            data=data_220_tx_msg, 
                            is_extended_id=False, 
                            dlc=len(data_220_tx_msg), 
                            is_fd=True,
                            timestamp=ts)
        try:                                                                                                                                                        
            can_bus.send(msg=msg_220)
            print("Tx:  {}".format(msg_220))
        except can.CanError:
            print("Message NOT sent") 
            
##############################################################
def process_230(ts): 
    # Send a VehMode
    e2e.p05.e2e_p05_protect(data=data_230_tx_msg,
                            length=length_230,
                            offset=offset_230,
                            data_id=data_id_230,
                            increment_counter=True)
    #print('data_230_tx_msg crc:')
    #print(data_230_tx_msg.hex()) 
    msg_230 = can.Message(timestamp=ts,
                          arbitration_id=PID_VEHMODES, 
                          is_extended_id=False,
                          dlc=len(data_230_tx_msg), 
                          data=data_230_tx_msg,  
                          is_fd=True)
    try: 
        can_bus.send(msg=msg_230) 
        print("Tx:  {}".format(msg_230))
    except can.CanError:
        print("Message NOT sent")
        
##############################################################
def process_240(ts): 
        # Send Func info
        e2e.p05.e2e_p05_protect(data=data_240_tx_msg,
                                length=length_240,
                                offset=offset_240,
                                data_id=data_id_240,
                                increment_counter=True)
        #print('data_240_tx_msg crc:')
        #print(data_240_tx_msg.hex()) 
        msg_240 = can.Message(arbitration_id=PID_FUNCINFO, 
                            data=data_240_tx_msg, 
                            is_extended_id=False, 
                            dlc=len(data_240_tx_msg), 
                            is_fd=True,
                            timestamp=ts)
        try:
            can_bus.send(msg=msg_240)
            print("Tx:  {}".format(msg_240))
        except can.CanError:
            print("Message NOT sent") 
            
##############################################################
# Main loop
def main():
    try:
        while True:
            dt = datetime.now()
            ts = datetime.timestamp(dt)
            process_200(ts)
            process_210(ts)
            process_220(ts)
            process_230(ts)  
            process_240(ts) 
            time.sleep(0.06) 

    except KeyboardInterrupt:
        #Catch keyboard interrupt
        if(os_name != 'Windows'):
            print('\n\rClosing interface...')
            os.system("sudo ip link set can0 down")
        print('\n\rKeyboard interrtupt')
        os._exit(0)
    
if __name__ == '__main__':
    main()