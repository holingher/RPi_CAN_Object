import can
import cantools
import time
import os
import e2e
import platform
import time
from dataclasses import dataclass
from can import Message

# Declare message_radar as a CAN message
message_radar = Message(
    arbitration_id=0x000,  # Default arbitration ID
    data=[],               # Empty data payload
    dlc=0,                 # Data length code
    is_extended_id=False,  # Standard ID (not extended)
    is_fd=True             # CAN FD message
)

# Declare message_car as a CAN message
message_car = Message(
    arbitration_id=0x000,  # Default arbitration ID
    data=[],               # Empty data payload
    dlc=0,                 # Data length code
    is_extended_id=False,  # Standard ID (not extended)
    is_fd=True             # CAN FD message
)

os_name = 'Windows'
# For a list of PIDs visit https://en.wikipedia.org/wiki/OBD-II_PIDs
####################################################################
#https://github.com/Knio/carhack/blob/master/Cars/Honda.markdown
VEHICLE_SPEED = 0x164 # E,F - Vehicle Speed
WHEEL_SPEED = 0x309 # C - Left wheel speed (km/h); D - Right wheel speed (km/h)
@dataclass
class egomotion_t:
    Speed: float
    Left_wheel_speed: float
    Right_wheel_speed: float
    YawRate: int
    LatAcc: int
    LongAcc: int
EgoMotion_data = egomotion_t(0.0, 0.0, 0.0, 0, 0, 0)
####################################################################
@dataclass
class object_list_for_draw_t:
    Class: int
    DataConf: int
    Qly: int
    
@dataclass
class VIEW_t:
    MsgCntr: int
    ScanID: int
    object_list_for_draw: list[object_list_for_draw_t]

ObjList_VIEW = VIEW_t(
    MsgCntr=0,
    ScanID=0,
    object_list_for_draw=[object_list_for_draw_t(0, 0, 0) for _ in range(30)]  # Array of 30 elements
)
####################################################################    
@dataclass
class object_prop_t:
    Class: str
    DataConf: str
    Qly: str
    
@dataclass
class objects_prop_t:
    first_obj_prop: object_prop_t
    second_obj_prop: object_prop_t

@dataclass
class ObjectList_t:
    arbitration_id: int
    e2e_DataId: int
    msg_name: str
    MsgCntr: str
    ScanID: str
    msg_obj_prop: objects_prop_t

PID_OBJ0_objects_prop_t = object_prop_t('FLR2RdrObject0To1Class0', 'FLR2RdrObject0To1DataConf0', 'FLR2RdrObject0To1Qly0')
PID_OBJ1_objects_prop_t = object_prop_t('FLR2RdrObject0To1Class1', 'FLR2RdrObject0To1DataConf1', 'FLR2RdrObject0To1Qly1')
PID_OBJ0_to_1_objects_prop_t = objects_prop_t(PID_OBJ0_objects_prop_t, PID_OBJ1_objects_prop_t)
PID_OBJ0_to_1   = ObjectList_t(0x140, 0x8CE, 'FlrFlr1canFr81', 'FLR2RdrObject0To1ScanID', 'FLR2RdrObject0To1MsgCntr', PID_OBJ0_to_1_objects_prop_t)

PID_OBJ2_objects_prop_t = object_prop_t('FLR2RdrObject2To3Class0', 'FLR2RdrObject2To3DataConf0', 'FLR2RdrObject2To3Qly0')
PID_OBJ3_objects_prop_t = object_prop_t('FLR2RdrObject2To3Class1', 'FLR2RdrObject2To3DataConf1', 'FLR2RdrObject2To3Qly1')
PID_OBJ2_to_3_objects_prop_t = objects_prop_t(PID_OBJ2_objects_prop_t, PID_OBJ3_objects_prop_t)
PID_OBJ2_to_3   = ObjectList_t(0x142, 0x8CF, 'FlrFlr1canFr82', 'FLR2RdrObject2To3ScanID', 'FLR2RdrObject2To3MsgCntr', PID_OBJ2_to_3_objects_prop_t)

PID_OBJ4_objects_prop_t = object_prop_t('FLR2RdrObject4To5Class0', 'FLR2RdrObject4To5DataConf0', 'FLR2RdrObject4To5Qly0')
PID_OBJ5_objects_prop_t = object_prop_t('FLR2RdrObject4To5Class1', 'FLR2RdrObject4To5DataConf1', 'FLR2RdrObject4To5Qly1')
PID_OBJ4_to_5_objects_prop_t = objects_prop_t(PID_OBJ4_objects_prop_t, PID_OBJ5_objects_prop_t)
PID_OBJ4_to_5   = ObjectList_t(0x144, 0x8D0, 'FlrFlr1canFr83', 'FLR2RdrObject4To5ScanID', 'FLR2RdrObject4To5MsgCntr', PID_OBJ4_to_5_objects_prop_t)

PID_OBJ6_objects_prop_t = object_prop_t('FLR2RdrObject6To7Class0', 'FLR2RdrObject6To7DataConf0', 'FLR2RdrObject6To7Qly0')
PID_OBJ7_objects_prop_t = object_prop_t('FLR2RdrObject6To7Class1', 'FLR2RdrObject6To7DataConf1', 'FLR2RdrObject6To7Qly1')
PID_OBJ6_to_7_objects_prop_t = objects_prop_t(PID_OBJ6_objects_prop_t, PID_OBJ7_objects_prop_t)
PID_OBJ6_to_7   = ObjectList_t(0x146, 0x8D1, 'FlrFlr1canFr84', 'FLR2RdrObject6To7ScanID', 'FLR2RdrObject6To7MsgCntr', PID_OBJ6_to_7_objects_prop_t)

PID_OBJ8_objects_prop_t = object_prop_t('FLR2RdrObject8To9Class0', 'FLR2RdrObject8To9DataConf0', 'FLR2RdrObject8To9Qly0')
PID_OBJ9_objects_prop_t = object_prop_t('FLR2RdrObject8To9Class1', 'FLR2RdrObject8To9DataConf1', 'FLR2RdrObject8To9Qly1')
PID_OBJ8_to_9_objects_prop_t = objects_prop_t(PID_OBJ8_objects_prop_t, PID_OBJ9_objects_prop_t)
PID_OBJ8_to_9   = ObjectList_t(0x148, 0x8D2, 'FlrFlr1canFr85', 'FLR2RdrObject8To9ScanID', 'FLR2RdrObject8To9MsgCntr', PID_OBJ8_to_9_objects_prop_t)

PID_OBJ10_objects_prop_t = object_prop_t('FLR2RdrObject10To11Class0', 'FLR2RdrObject10To11DataConf0', 'FLR2RdrObject10To11Qly0')
PID_OBJ11_objects_prop_t = object_prop_t('FLR2RdrObject10To11Class1', 'FLR2RdrObject10To11DataConf1', 'FLR2RdrObject10To11Qly1')
PID_OBJ10_to_11_objects_prop_t = objects_prop_t(PID_OBJ10_objects_prop_t, PID_OBJ11_objects_prop_t)
PID_OBJ10_to_11 = ObjectList_t(0x14A, 0x8D3, 'FlrFlr1canFr86', 'FLR2RdrObject10To11ScanID', 'FLR2RdrObject10To11MsgCntr', PID_OBJ10_to_11_objects_prop_t)

PID_OBJ12_objects_prop_t = object_prop_t('FLR2RdrObject12To13Class0', 'FLR2RdrObject12To13DataConf0', 'FLR2RdrObject12To13Qly0')
PID_OBJ13_objects_prop_t = object_prop_t('FLR2RdrObject12To13Class1', 'FLR2RdrObject12To13DataConf1', 'FLR2RdrObject12To13Qly1')
PID_OBJ12_to_13_objects_prop_t = objects_prop_t(PID_OBJ12_objects_prop_t, PID_OBJ13_objects_prop_t)
PID_OBJ12_to_13 = ObjectList_t(0x14C, 0x8D4, 'FlrFlr1canFr87', 'FLR2RdrObject12To13ScanID', 'FLR2RdrObject12To13MsgCntr', PID_OBJ12_to_13_objects_prop_t)

PID_OBJ14_objects_prop_t = object_prop_t('FLR2RdrObject14To15Class0', 'FLR2RdrObject14To15DataConf0', 'FLR2RdrObject14To15Qly0')
PID_OBJ15_objects_prop_t = object_prop_t('FLR2RdrObject14To15Class1', 'FLR2RdrObject14To15DataConf1', 'FLR2RdrObject14To15Qly1')
PID_OBJ14_to_15_objects_prop_t = objects_prop_t(PID_OBJ14_objects_prop_t, PID_OBJ15_objects_prop_t)
PID_OBJ14_to_15 = ObjectList_t(0x14E, 0x8D5, 'FlrFlr1canFr88', 'FLR2RdrObject14To15ScanID', 'FLR2RdrObject14To15MsgCntr', PID_OBJ14_to_15_objects_prop_t)

PID_OBJ16_objects_prop_t = object_prop_t('FLR2RdrObject16To17Class0', 'FLR2RdrObject16To17DataConf0', 'FLR2RdrObject16To17Qly0')
PID_OBJ17_objects_prop_t = object_prop_t('FLR2RdrObject16To17Class1', 'FLR2RdrObject16To17DataConf1', 'FLR2RdrObject16To17Qly1')
PID_OBJ16_to_17_objects_prop_t = objects_prop_t(PID_OBJ16_objects_prop_t, PID_OBJ17_objects_prop_t)
PID_OBJ16_to_17 = ObjectList_t(0x150, 0x8D6, 'FlrFlr1canFr89', 'FLR2RdrObject16To17ScanID', 'FLR2RdrObject16To17MsgCntr', PID_OBJ16_to_17_objects_prop_t)

PID_OBJ18_objects_prop_t = object_prop_t('FLR2RdrObject18To19Class0', 'FLR2RdrObject18To19DataConf0', 'FLR2RdrObject18To19Qly0')
PID_OBJ19_objects_prop_t = object_prop_t('FLR2RdrObject18To19Class1', 'FLR2RdrObject18To19DataConf1', 'FLR2RdrObject18To19Qly1')
PID_OBJ18_to_19_objects_prop_t = objects_prop_t(PID_OBJ18_objects_prop_t, PID_OBJ19_objects_prop_t)
PID_OBJ18_to_19 = ObjectList_t(0x152, 0x8D7, 'FlrFlr1canFr90', 'FLR2RdrObject18To19ScanID', 'FLR2RdrObject18To19MsgCntr', PID_OBJ18_to_19_objects_prop_t)

PID_OBJ20_objects_prop_t = object_prop_t('FLR2RdrObject20To21Class0', 'FLR2RdrObject20To21DataConf0', 'FLR2RdrObject20To21Qly0')
PID_OBJ21_objects_prop_t = object_prop_t('FLR2RdrObject20To21Class1', 'FLR2RdrObject20To21DataConf1', 'FLR2RdrObject20To21Qly1')
PID_OBJ20_to_21_objects_prop_t = objects_prop_t(PID_OBJ20_objects_prop_t, PID_OBJ21_objects_prop_t)
PID_OBJ20_to_21 = ObjectList_t(0x154, 0x8A9, 'FlrFlr1canFr91', 'FLR2RdrObject20To21ScanID', 'FLR2RdrObject20To21MsgCntr', PID_OBJ20_to_21_objects_prop_t)

PID_OBJ22_objects_prop_t = object_prop_t('FLR2RdrObject22To23Class0', 'FLR2RdrObject22To23DataConf0', 'FLR2RdrObject22To23Qly0')
PID_OBJ23_objects_prop_t = object_prop_t('FLR2RdrObject22To23Class1', 'FLR2RdrObject22To23DataConf1', 'FLR2RdrObject22To23Qly1')
PID_OBJ22_to_23_objects_prop_t = objects_prop_t(PID_OBJ22_objects_prop_t, PID_OBJ23_objects_prop_t)
PID_OBJ22_to_23 = ObjectList_t(0x156, 0x8AA, 'FlrFlr1canFr92', 'FLR2RdrObject22To23ScanID', 'FLR2RdrObject22To23MsgCntr', PID_OBJ22_to_23_objects_prop_t)

PID_OBJ24_objects_prop_t = object_prop_t('FLR2RdrObject24To25Class0', 'FLR2RdrObject24To25DataConf0', 'FLR2RdrObject24To25Qly0')
PID_OBJ25_objects_prop_t = object_prop_t('FLR2RdrObject24To25Class1', 'FLR2RdrObject24To25DataConf1', 'FLR2RdrObject24To25Qly1')
PID_OBJ24_to_25_objects_prop_t = objects_prop_t(PID_OBJ24_objects_prop_t, PID_OBJ25_objects_prop_t)
PID_OBJ24_to_25 = ObjectList_t(0x158, 0x8AB, 'FlrFlr1canFr93', 'FLR2RdrObject24To25ScanID', 'FLR2RdrObject24To25MsgCntr', PID_OBJ24_to_25_objects_prop_t)

PID_OBJ26_objects_prop_t = object_prop_t('FLR2RdrObject26To27Class0', 'FLR2RdrObject26To27DataConf0', 'FLR2RdrObject26To27Qly0')
PID_OBJ27_objects_prop_t = object_prop_t('FLR2RdrObject26To27Class1', 'FLR2RdrObject26To27DataConf1', 'FLR2RdrObject26To27Qly1')
PID_OBJ26_to_27_objects_prop_t = objects_prop_t(PID_OBJ26_objects_prop_t, PID_OBJ27_objects_prop_t)
PID_OBJ26_to_27 = ObjectList_t(0x15A, 0x8AC, 'FlrFlr1canFr94', 'FLR2RdrObject26To27ScanID', 'FLR2RdrObject26To27MsgCntr', PID_OBJ26_to_27_objects_prop_t)

PID_OBJ28_objects_prop_t = object_prop_t('FLR2RdrObject28To29Class0', 'FLR2RdrObject28To29DataConf0', 'FLR2RdrObject28To29Qly0')
PID_OBJ29_objects_prop_t = object_prop_t('FLR2RdrObject28To29Class1', 'FLR2RdrObject28To29DataConf1', 'FLR2RdrObject28To29Qly1')
PID_OBJ28_to_29_objects_prop_t = objects_prop_t(PID_OBJ28_objects_prop_t, PID_OBJ29_objects_prop_t)
PID_OBJ28_to_29 = ObjectList_t(0x15C, 0x8AD, 'FlrFlr1canFr95', 'FLR2RdrObject28To29ScanID', 'FLR2RdrObject28To29MsgCntr', PID_OBJ28_to_29_objects_prop_t)

list_of_Object_attr = (
    PID_OBJ0_to_1,
    PID_OBJ2_to_3,
    PID_OBJ4_to_5,
    PID_OBJ6_to_7,
    PID_OBJ8_to_9,
    PID_OBJ10_to_11,
    PID_OBJ12_to_13,
    PID_OBJ14_to_15,
    PID_OBJ16_to_17,
    PID_OBJ18_to_19,
    PID_OBJ20_to_21,
    PID_OBJ22_to_23,
    PID_OBJ24_to_25,
    PID_OBJ26_to_27,
    PID_OBJ28_to_29
)
################# RX ################

os_name = platform.system()
print(os_name)
try:
    # Bring up can0 interface at 500kbps
    print('Loading DBC....')
    db = cantools.db.load_file("database/volvo_MRR.dbc")
    if(os_name != 'Windows'):
        print('Bring up CAN....')
        os.system("sudo ifconfig can0 down")
        os.system("sudo ifconfig can1 down")
        time.sleep(0.1)
        os.system("sudo ip link set can0 up type can bitrate 500000 dbitrate 2000000 restart-ms 1000 berr-reporting on fd on")
        time.sleep(0.1)
        os.system("sudo ip link set can1 up type can bitrate 500000 dbitrate 2000000 restart-ms 1000 berr-reporting on fd on")
        time.sleep(0.1)
        can_bus_radar = can.interface.Bus(channel='can0', interface='socketcan', bitrate=500000, data_bitrate=2000000, fd=True)
        can_bus_car = can.interface.Bus(channel='can1', interface='socketcan', bitrate=500000, data_bitrate=2000000, fd=True)
    elif(os_name == 'Windows'):
        print('Bring up CAN....')
        can_bus_radar = can.interface.Bus(channel='vcan0', interface='virtual', bitrate=500000, data_bitrate=2000000, fd=True)
        can_bus_car = can.interface.Bus(channel='vcan1', interface='virtual', bitrate=500000, data_bitrate=2000000, fd=True)
    time.sleep(0.1)
except OSError as e:
    print(f'Cannot find CAN board: {e}')
    os._exit(0)
print('Ready')

reference_ID = list_of_Object_attr[0].arbitration_id
# Main loop
try:
    while True:
        #treat Object list 
        try:
            if(os_name != 'Windows'):
                message_radar = can_bus_radar.recv(timeout=0.1)
            # treat only specific range of messages
            if message_radar.arbitration_id >= list_of_Object_attr[0].arbitration_id and message_radar.arbitration_id < list_of_Object_attr[-1].arbitration_id:
                for entry in list_of_Object_attr:
                    if(entry.arbitration_id == message_radar.arbitration_id):
                        if e2e.p05.e2e_p05_check(message_radar.data, message_radar.dlc, data_id=entry.e2e_DataId) is True:
                            #decoded_message = db.get_message_by_frame_id(message_radar.arbitration_id).get_signal_by_name(entry.ScanID)
                            ObjList_VIEW.MsgCntr = db.get_message_by_frame_id(message_radar.arbitration_id).get_signal_by_name(entry.MsgCntr)
                            ObjList_VIEW.ScanID = db.get_message_by_frame_id(message_radar.arbitration_id).get_signal_by_name(entry.ScanID)
                            
                            index_entry = entry.arbitration_id - reference_ID
                            ObjList_VIEW.object_list_for_draw[index_entry].Class = db.get_message_by_frame_id(message_radar.arbitration_id).get_signal_by_name(entry.msg_obj_prop.first_obj_prop.Class)
                            ObjList_VIEW.object_list_for_draw[index_entry].DataConf = db.get_message_by_frame_id(message_radar.arbitration_id).get_signal_by_name(entry.msg_obj_prop.first_obj_prop.DataConf)
                            ObjList_VIEW.object_list_for_draw[index_entry].Qly = db.get_message_by_frame_id(message_radar.arbitration_id).get_signal_by_name(entry.msg_obj_prop.first_obj_prop.Qly)
                            ObjList_VIEW.object_list_for_draw[index_entry + 1].Class = db.get_message_by_frame_id(message_radar.arbitration_id).get_signal_by_name(entry.msg_obj_prop.second_obj_prop.Class)
                            ObjList_VIEW.object_list_for_draw[index_entry + 1].DataConf = db.get_message_by_frame_id(message_radar.arbitration_id).get_signal_by_name(entry.msg_obj_prop.second_obj_prop.DataConf)
                            ObjList_VIEW.object_list_for_draw[index_entry + 1].Qly = db.get_message_by_frame_id(message_radar.arbitration_id).get_signal_by_name(entry.msg_obj_prop.second_obj_prop.Qly)
                            print('arbitration_id:', message_radar.arbitration_id)
                            #print('Decoded:', decoded_message)
        except OSError as e:
            print(f'\n\rNo bus from radar!!: {e}')
            os._exit(0)
            
        try:
            if(os_name != 'Windows'):
                message_car = can_bus_car.recv(timeout=0.1)
            if message_car.arbitration_id == VEHICLE_SPEED:
                EgoMotion_data.Speed = db.get_message_by_frame_id(message_car.arbitration_id).get_signal_by_name('FLR2RdrVehicleSpeed')
            
            if message_car.arbitration_id == WHEEL_SPEED:
                EgoMotion_data.Left_wheel_speed = db.get_message_by_frame_id(message_car.arbitration_id).get_signal_by_name('FLR2RdrLeftWheelSpeed')
                EgoMotion_data.Right_wheel_speed = db.get_message_by_frame_id(message_car.arbitration_id).get_signal_by_name('FLR2RdrRightWheelSpeed')
                #EgoMotion_data.YawRate = db.get_message_by_frame_id(message_car.arbitration_id).get_signal_by_name('FLR2RdrYawRate')
                #EgoMotion_data.LatAcc = db.get_message_by_frame_id(message_car.arbitration_id).get_signal_by_name('FLR2RdrLatAcc')
                #EgoMotion_data.LongAcc = db.get_message_by_frame_id(message_car.arbitration_id).get_signal_by_name('FLR2RdrLongAcc')
                print('arbitration_id:', message_car.arbitration_id)
                print('Decoded:', message_car.data)
        except OSError as e:
            print(f'\n\rNo bus from car!!: {e}')
            os._exit(0)
            
except KeyboardInterrupt:
    #Catch keyboard interrupt
    if(os_name != 'Windows'):
        print('\n\rClosing interface...')
        os.system("sudo ip link set can0 down")
        os.system("sudo ip link set can1 down")
    print('\n\rKeyboard interrtupt')
    os._exit(0)
