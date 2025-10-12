import io
import os
import time
import can
import cantools
from defines import *
from rx import setup_can_interrupts

########################################################################################
def init_com():
    dbc_radar = cantools.database.can.database.Database()
    try:
        print('Loading DBC....')
        
        if(is_raspberrypi()):
            dbc_radar = cantools.db.load_file("database/radar.dbc")
            print('Bring up CAN Tx....')
            os.system("sudo ifconfig can0 down")
            os.system("sudo ifconfig can1 down")
            time.sleep(0.1)
            os.system("sudo ip link set can0 up type can bitrate 500000 dbitrate 2000000 restart-ms 1000 berr-reporting on fd on")
            time.sleep(0.1)
            os.system("sudo ip link set can1 up type can bitrate 500000 dbitrate 2000000 restart-ms 1000 berr-reporting on fd on")
            time.sleep(0.1)
            can_bus_radar = can.interface.Bus(channel='can0', interface='socketcan', bitrate=500000, data_bitrate=2000000, fd=True)
            can_bus_car = can.interface.Bus(channel='can1', interface='socketcan', bitrate=500000, data_bitrate=2000000, fd=True)
        else:
            dbc_radar = cantools.db.load_file("database/radar.dbc")
            print('Bring up virtual CAN Tx....')
            can_bus_radar = can.interface.Bus(channel='vcan0', interface='virtual', bitrate=500000, data_bitrate=2000000, fd=True)
            can_bus_car = can.interface.Bus(channel='vcan1', interface='virtual', bitrate=500000, data_bitrate=2000000, fd=True)
        
            print(f"CAN bus object: {can_bus_radar}")
        time.sleep(0.1)
        
        # Setup CAN interrupts for KaMami CAN FD HAT
        if setup_can_interrupts(can_bus_radar, can_bus_car, dbc_radar):
            print('CAN interrupt mode enabled')
        else:
            print('CAN interrupt setup failed - check GPIO availability')
            
        print('Ready')
    except OSError as e:
        print(f'Cannot find CAN board: {e}')
        os._exit(0)
    print('Ready')
    return can_bus_radar, can_bus_car, dbc_radar

########################################################################################
def deinit_com():
    # Clean up CAN interrupts first
    from rx import cleanup_can_interrupts
    cleanup_can_interrupts()
    
    if(is_raspberrypi()):
        print('\n\rClosing interface...')
        os.system("sudo ip link set can0 down")
        os.system("sudo ip link set can1 down")
    print('\n\rKeyboard interrupt')
    os._exit(0)