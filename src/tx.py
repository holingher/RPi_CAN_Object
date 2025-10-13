import can
import e2e.p05
import time
from defines import *
from typing import Callable

# Global counter for sync time messages  
sync_time_counter = 15  # Starting value matching trace data

# Global reference time for seconds synchronization - set when first called
sync_epoch_time = None

# Global variables to track timing deltas
last_timesync_send_time = None
last_can0_tx_send_time = None

# Getting the current date and time
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

data_210_tx_msg_carConfig = data_210_tx_msg[:5]
data_210_tx_msg_PowerMode = data_210_tx_msg[5:] 

# 0x702_10
PID_TS       = 0x702
data_702_seconds_tx_msg = bytearray(b"\x10\x00\x00\x00\x00\x00\x00\x00")
length_702_seconds = len(data_702_seconds_tx_msg)
offset_702_seconds = 0

# 0x702_18
data_702_millis_tx_msg = bytearray(b"\x18\x00\x00\x00\x00\x00\x00\x00")
length_702_millis = len(data_702_millis_tx_msg)
offset_702_millis = 0
##############################################################
def process_200(can_bus:can.BusABC, ts):
    # Send Vehicle motion state
    e2e.p05.e2e_p05_protect(data=data_200_tx_msg,
                            length=length_200,
                            offset=offset_200,
                            data_id=data_id_200,
                            increment_counter=True)

    msg_200 = can.Message(arbitration_id=PID_VEHMOTIONSTATE, 
                        data=data_200_tx_msg, 
                        is_extended_id=False, 
                        dlc=len(data_200_tx_msg), 
                        is_fd=True,
                        timestamp=ts)
    try:
        can_bus.send(msg=msg_200)
        #print("Tx:  {}".format(msg_200))
    except can.CanError:
        print("Message NOT sent")
         
##############################################################
def process_210(can_bus:can.BusABC, ts):  
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

    msg_210 = can.Message(arbitration_id=PID_CARCONFIG, 
                                    data=data_210_tx_msg, 
                                    is_extended_id= False, 
                                    dlc=len(data_210_tx_msg), 
                                    is_fd=True,
                                    timestamp=ts)
    try:
        can_bus.send(msg=msg_210)
        #print("Tx:  {}".format(msg_210))
    except can.CanError:
        print("Message NOT sent") 
        
##############################################################
def process_220(can_bus:can.BusABC, ts): 
    # Send Global Snapshot
    e2e.p05.e2e_p05_protect(data=data_220_tx_msg,
                            length=length_220,
                            offset=offset_220,
                            data_id=data_id_220,
                            increment_counter=True)

    msg_220 = can.Message(arbitration_id=PID_GLOBALSNAPSHOT, 
                        data=data_220_tx_msg, 
                        is_extended_id=False, 
                        dlc=len(data_220_tx_msg), 
                        is_fd=True,
                        timestamp=ts)
    try:                                                                                                                                                        
        can_bus.send(msg=msg_220)
        #print("Tx:  {}".format(msg_220))
    except can.CanError as e:
        print("Message NOT sent", e)
            
##############################################################
def process_230(can_bus:can.BusABC, ts): 
    # Send a VehMode
    e2e.p05.e2e_p05_protect(data=data_230_tx_msg,
                            length=length_230,
                            offset=offset_230,
                            data_id=data_id_230,
                            increment_counter=True)

    msg_230 = can.Message(timestamp=ts,
                          arbitration_id=PID_VEHMODES, 
                          is_extended_id=False,
                          dlc=len(data_230_tx_msg), 
                          data=data_230_tx_msg,  
                          is_fd=True)
    try: 
        can_bus.send(msg=msg_230) 
        #print("Tx:  {}".format(msg_230))
    except can.CanError as e:
        print("Message NOT sent", e)
        
##############################################################
def process_240(can_bus:can.BusABC, ts): 
    # Send Func info
    e2e.p05.e2e_p05_protect(data=data_240_tx_msg,
                            length=length_240,
                            offset=offset_240,
                            data_id=data_id_240,
                            increment_counter=True)

    msg_240 = can.Message(arbitration_id=PID_FUNCINFO, 
                        data=data_240_tx_msg, 
                        is_extended_id=False, 
                        dlc=len(data_240_tx_msg), 
                        is_fd=True,
                        timestamp=ts)
    try:
        can_bus.send(msg=msg_240)
        #print("Tx:  {}".format(msg_240))
    except can.CanError:
        print("Message NOT sent") 
            
# process the TX messages to radar
def process_CAN0_tx(can_bus:can.BusABC):
    global last_can0_tx_send_time
    
    if can_bus is None:
        print("CAN bus is not initialized.")
        return
    '''
    # Calculate delta time since last send
    current_send_time = time.time()
    if last_can0_tx_send_time is not None:
        delta_ms = (current_send_time - last_can0_tx_send_time) * 1000
        print(f"CAN0_TX Delta: {delta_ms:.2f} ms")
    last_can0_tx_send_time = current_send_time
    '''
    # Get the current time in milliseconds
    current_time = time.time() * 1000  # Convert to milliseconds

    process_200(can_bus, current_time)
    process_210(can_bus, current_time)
    process_220(can_bus, current_time)
    process_230(can_bus, current_time)  
    process_240(can_bus, current_time)
##############################################################

#send seconds - SYNC not CRC secured message format
def process_702_10(can_bus:can.BusABC, ts, current_time_seconds):

    # Byte 0: Type = 0x10
    data_702_seconds_tx_msg[0] = 0x10
    
    # Byte 1: User Byte 1, default: 0
    data_702_seconds_tx_msg[1] = 0
    
    # Byte 2: Based on trace data, this appears to be just the sequence counter (0-15)
    sequence_counter = data_702_seconds_tx_msg[2]
    sequence_counter += 1
    # Reset counter to 0 when it reaches 16
    if sequence_counter >= 16:
        sequence_counter = 0
    data_702_seconds_tx_msg[2] = sequence_counter
    
    # Byte 3: User Byte 0, default: 0
    data_702_seconds_tx_msg[3] = 0
    
    # Byte 4-7: SyncTimeSec = 32 bit LSB of the 48 bits seconds part of the time (big-endian)
    # Calculate seconds relative to sync epoch (starts from 0)
    global sync_epoch_time
    if sync_epoch_time is None:
        sync_epoch_time = current_time_seconds  # Set epoch on first call
    
    # Calculate elapsed seconds since epoch
    elapsed_seconds = int(current_time_seconds - sync_epoch_time)
    seconds_32bit = elapsed_seconds & 0xFFFFFFFF
    data_702_seconds_tx_msg[4:8] = seconds_32bit.to_bytes(4, byteorder='big', signed=False)
    
    #print("CAN 702 SYNC: Seq={:02x}, Seconds={}, Data={}".format(sequence_counter, seconds_32bit, data_702_seconds_tx_msg.hex()))
    # Send Func info
    msg_702_10 = can.Message(arbitration_id=PID_TS, 
                        data=data_702_seconds_tx_msg, 
                        is_extended_id=False, 
                        dlc=8,#len(data_702_seconds_tx_msg), 
                        is_fd=True,
                        timestamp=ts)
    try:
        can_bus.send(msg=msg_702_10)
        #print("Tx:  {}".format(msg_702_10))
    except can.CanError:
        print("Message NOT sent") 

#send milis - FUP not CRC secured message format
def process_702_18(can_bus:can.BusABC, ts, current_time_ns):
    
    # Byte 0: Type = 0x18
    data_702_millis_tx_msg[0] = 0x18
    
    # Byte 1: User Byte 2, default: 0
    data_702_millis_tx_msg[1] = 0
    
    # Byte 2: Sequence Counter (based on examples: 09, 0a, 0b, 0c, 0d, 0e, 0f, 00)
    sequence_counter = data_702_millis_tx_msg[2]
    sequence_counter += 1
    # Reset counter to 0 when it reaches 16 (0x10)
    if sequence_counter >= 16:
        sequence_counter = 0
    data_702_millis_tx_msg[2] = sequence_counter
    
    # Byte 3: Fixed value 0x04 (based on examples)
    data_702_millis_tx_msg[3] = 0x04
    
    # Byte 4-7: SyncTimeNSec = 32 Bit time value in nanoseconds (big-endian)
    # Use the passed current_time_ns parameter and get only the fractional part within a second
    nanoseconds_in_second = current_time_ns % 1_000_000_000  # Get nanoseconds within current second
    data_702_millis_tx_msg[4:8] = nanoseconds_in_second.to_bytes(4, byteorder='big', signed=False)
    
    #print("CAN 702: Seq={:02x}, NS={}, Data={}".format(sequence_counter, nanoseconds_in_second, data_702_millis_tx_msg.hex()))
    # Send Func info
    msg_702_18 = can.Message(arbitration_id=PID_TS, 
                        data=data_702_millis_tx_msg, 
                        is_extended_id=False, 
                        dlc=8,#len(data_702_millis_tx_msg), 
                        is_fd=True,
                        timestamp=ts)
    try:
        can_bus.send(msg=msg_702_18)
        #print("Tx:  {}".format(msg_702_18))
    except can.CanError:
        print("Message NOT sent")

def periodic_TimeSync_125ms_task(can_bus:can.BusABC):
    '''
    global last_timesync_send_time
    
    # Calculate delta time since last send
    current_send_time = time.time()
    if last_timesync_send_time is not None:
        delta_ms = (current_send_time - last_timesync_send_time) * 1000
        print(f"TimeSync_125ms Delta: {delta_ms:.2f} ms")
    last_timesync_send_time = current_send_time
    '''
    # Get the current time
    current_time = time.time()

    current_time_ns = time.time_ns()
    current_time_seconds = int(current_time)  # Use time.time() directly for seconds
    
    process_702_10(can_bus, current_time, current_time_seconds)
    process_702_18(can_bus, current_time, current_time_ns)
    pass
##############################################################


def periodic_task(interval_ms: float, task: Callable, stop_event, *args, **kwargs):
    next_run_time = time.time()
    while not stop_event.is_set():
        current_time = time.time()
        if current_time >= next_run_time:
            task(*args, **kwargs)
            next_run_time += interval_ms / 1000.0
        else:
            time_to_sleep = next_run_time - current_time
            time.sleep(time_to_sleep)
            
def process_CAN0_tx_60ms_wrapper(interval_ms: float, stop_event, can_bus_CAN1):
    """Wrapper function for TX process using existing CAN bus"""
    try:
        if can_bus_CAN1 is None:
            print("CAN bus not provided to TX process")
            return
            
        # Run the periodic TX task every 60ms
        periodic_task(interval_ms, process_CAN0_tx, stop_event, can_bus_CAN1)
        
    except Exception as e:
        print(f"TX process error: {e}")

def periodic_CAN0_tx_TimeSync_125ms_wrapper(interval_ms: float, stop_event, can_bus_CAN1):
    """Wrapper function for 125ms periodic process"""
    try:
        # Run the periodic task every 125ms
        periodic_task(interval_ms, periodic_TimeSync_125ms_task, stop_event, can_bus_CAN1)
        
    except Exception as e:
        print(f"125ms periodic process error: {e}")