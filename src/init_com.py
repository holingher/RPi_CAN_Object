import os
import distro
import time
import can
import cantools
from defines import *

########################################################################################
def init_com():
    dbc_radar = cantools.database.can.database.Database()
    global os_name, distro_name
    distro_name = distro.name()
    print('Distro: ', distro_name)
    try:
        print('Loading DBC....')
        
        if(distro_name == 'Raspbian GNU/Linux'):
            dbc_radar = cantools.db.load_file("../database/volvo_MRR.dbc")
            print('Bring up CAN Tx....')
            os.system("sudo ifconfig can0 down")
            os.system("sudo ifconfig can1 down")
            time.sleep(0.1)
            os.system("sudo ip link set can0 up type can bitrate 500000 dbitrate 2000000 restart-ms 1000 berr-reporting on fd on")
            time.sleep(0.1)
            os.system("sudo ip link set can1 up type can bitrate 500000 dbitrate 2000000 restart-ms 1000 berr-reporting on fd on")
            time.sleep(0.1)
            can_bus_radar = can.interface.Bus(channel='can0', interface='socketcan', bitrate=500000, data_bitrate=2000000, fd=True)
            can_bus_radar = can.interface.Bus(channel='can1', interface='socketcan', bitrate=500000, data_bitrate=2000000, fd=True)
        elif(os_name == 'Windows') or (distro_name == 'Ubuntu'):
            dbc_radar = cantools.db.load_file("database/volvo_MRR.dbc")
            print('Bring up CAN Tx....')
            can_bus_radar = can.interface.Bus(channel='vcan0', interface='virtual', bitrate=500000, data_bitrate=2000000, fd=True)
            can_bus_car = can.interface.Bus(channel='vcan1', interface='virtual', bitrate=500000, data_bitrate=2000000, fd=True)
        
            print(f"CAN bus object: {can_bus_radar}")
        time.sleep(0.1)
        print('Ready')
    except OSError as e:
        print(f'Cannot find CAN board: {e}')
        os._exit(0)
    print('Ready')
    return can_bus_radar, can_bus_car, dbc_radar

########################################################################################
def deinit_com():
    if(distro_name == 'Raspbian GNU/Linux'):
        print('\n\rClosing interface...')
        os.system("sudo ip link set can0 down")
        os.system("sudo ip link set can1 down")
    print('\n\rKeyboard interrtupt')
    os._exit(0)