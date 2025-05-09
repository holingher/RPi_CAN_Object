import can
import cantools
from cantools import database
import time
import os
import e2e
import platform
import distro
from dataclasses import dataclass
from can import Message
from defines import *

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
distro_name = distro.name()
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
    object_id: int
    Class: int
    DataConf: int
    DataLen: float
    DataWidth: float
    HeadingAng: float
    LatAcc: float
    LatPos: int
    LatVelo: float
    LgtAcc: float
    LgtPos: int
    LgtVelo: float
    ModelInfo: int
    Qly: int
    
@dataclass
class VIEW_t:
    MsgCntr: int
    ScanID: int
    object_list_for_draw: list[object_list_for_draw_t]

ObjList_VIEW = VIEW_t(
    MsgCntr=0,
    ScanID=0,
    object_list_for_draw=[object_list_for_draw_t(30, 0, 0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0, 0) for _ in range(30)]  # Array of 30 elements
)
####################################################################    
@dataclass
class object_prop_t:
    object_id: int
    Class: str
    DataConf: str
    DataLen: str
    DataWidth: str
    HeadingAng: str
    LatAcc: str
    LatPos: str
    LatVelo: str
    LgtAcc: str
    LgtPos: str
    LgtVelo: str
    ModelInfo: str
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

PID_OBJ0_objects_prop_t = object_prop_t(0, 'FLR2RdrObject0To1Class0', 'FLR2RdrObject0To1DataConf0', 'FLR2RdrObject0To1DataLen0', 'FLR2RdrObject0To1DataWidth0', 'FLR2RdrObject0To1HeadingAng0', 'FLR2RdrObject0To1LatAcc0', 'FLR2RdrObject0To1LatPos0', 'FLR2RdrObject0To1LatVelo0', 'FLR2RdrObject0To1LgtAcc0', 'FLR2RdrObject0To1LgtPos0', 'FLR2RdrObject0To1LgtVelo0', 'FLR2RdrObject0To1ModelInfo0', 'FLR2RdrObject0To1Qly0')
PID_OBJ1_objects_prop_t = object_prop_t(1, 'FLR2RdrObject0To1Class1', 'FLR2RdrObject0To1DataConf1', 'FLR2RdrObject0To1DataLen1', 'FLR2RdrObject0To1DataWidth1', 'FLR2RdrObject0To1HeadingAng1', 'FLR2RdrObject0To1LatAcc1', 'FLR2RdrObject0To1LatPos1', 'FLR2RdrObject0To1LatVelo1', 'FLR2RdrObject0To1LgtAcc1', 'FLR2RdrObject0To1LgtPos1', 'FLR2RdrObject0To1LgtVelo1', 'FLR2RdrObject0To1ModelInfo1', 'FLR2RdrObject0To1Qly1')
PID_OBJ0_to_1_objects_prop_t = objects_prop_t(PID_OBJ0_objects_prop_t, PID_OBJ1_objects_prop_t)
PID_OBJ0_to_1   = ObjectList_t(0x140, 0x8CE, 'FlrFlr1canFr81', 'FLR2RdrObject0To1ScanID', 'FLR2RdrObject0To1MsgCntr', PID_OBJ0_to_1_objects_prop_t)

PID_OBJ2_objects_prop_t = object_prop_t(2, 'FLR2RdrObject2To3Class0', 'FLR2RdrObject2To3DataConf0', 'FLR2RdrObject2To3DataLen0', 'FLR2RdrObject2To3DataWidth0', 'FLR2RdrObject2To3HeadingAng0', 'FLR2RdrObject2To3LatAcc0', 'FLR2RdrObject2To3LatPos0', 'FLR2RdrObject2To3LatVelo0', 'FLR2RdrObject2To3LgtAcc0', 'FLR2RdrObject2To3LgtPos0', 'FLR2RdrObject2To3LgtVelo0', 'FLR2RdrObject2To3ModelInfo0', 'FLR2RdrObject2To3Qly0')
PID_OBJ3_objects_prop_t = object_prop_t(3, 'FLR2RdrObject2To3Class1', 'FLR2RdrObject2To3DataConf1', 'FLR2RdrObject2To3DataLen1', 'FLR2RdrObject2To3DataWidth1', 'FLR2RdrObject2To3HeadingAng1', 'FLR2RdrObject2To3LatAcc1', 'FLR2RdrObject2To3LatPos1', 'FLR2RdrObject2To3LatVelo1', 'FLR2RdrObject2To3LgtAcc1', 'FLR2RdrObject2To3LgtPos1', 'FLR2RdrObject2To3LgtVelo1', 'FLR2RdrObject2To3ModelInfo1', 'FLR2RdrObject2To3Qly1')
PID_OBJ2_to_3_objects_prop_t = objects_prop_t(PID_OBJ2_objects_prop_t, PID_OBJ3_objects_prop_t)
PID_OBJ2_to_3   = ObjectList_t(0x142, 0x8CF, 'FlrFlr1canFr82', 'FLR2RdrObject2To3ScanID', 'FLR2RdrObject2To3MsgCntr', PID_OBJ2_to_3_objects_prop_t)

PID_OBJ4_objects_prop_t = object_prop_t(4, 'FLR2RdrObject4To5Class0', 'FLR2RdrObject4To5DataConf0', 'FLR2RdrObject4To5DataLen0', 'FLR2RdrObject4To5DataWidth0', 'FLR2RdrObject4To5HeadingAng0', 'FLR2RdrObject4To5LatAcc0', 'FLR2RdrObject4To5LatPos0', 'FLR2RdrObject4To5LatVelo0', 'FLR2RdrObject4To5LgtAcc0', 'FLR2RdrObject4To5LgtPos0', 'FLR2RdrObject4To5LgtVelo0', 'FLR2RdrObject4To5ModelInfo0', 'FLR2RdrObject4To5Qly0')
PID_OBJ5_objects_prop_t = object_prop_t(5, 'FLR2RdrObject4To5Class1', 'FLR2RdrObject4To5DataConf1', 'FLR2RdrObject4To5DataLen1', 'FLR2RdrObject4To5DataWidth1', 'FLR2RdrObject4To5HeadingAng1', 'FLR2RdrObject4To5LatAcc1', 'FLR2RdrObject4To5LatPos1', 'FLR2RdrObject4To5LatVelo1', 'FLR2RdrObject4To5LgtAcc1', 'FLR2RdrObject4To5LgtPos1', 'FLR2RdrObject4To5LgtVelo1', 'FLR2RdrObject4To5ModelInfo1', 'FLR2RdrObject4To5Qly1')
PID_OBJ4_to_5_objects_prop_t = objects_prop_t(PID_OBJ4_objects_prop_t, PID_OBJ5_objects_prop_t)
PID_OBJ4_to_5   = ObjectList_t(0x144, 0x8D0, 'FlrFlr1canFr83', 'FLR2RdrObject4To5ScanID', 'FLR2RdrObject4To5MsgCntr', PID_OBJ4_to_5_objects_prop_t)

PID_OBJ6_objects_prop_t = object_prop_t(6, 'FLR2RdrObject6To7Class0', 'FLR2RdrObject6To7DataConf0', 'FLR2RdrObject6To7DataLen0', 'FLR2RdrObject6To7DataWidth0', 'FLR2RdrObject6To7HeadingAng0', 'FLR2RdrObject6To7LatAcc0', 'FLR2RdrObject6To7LatPos0', 'FLR2RdrObject6To7LatVelo0', 'FLR2RdrObject6To7LgtAcc0', 'FLR2RdrObject6To7LgtPos0', 'FLR2RdrObject6To7LgtVelo0', 'FLR2RdrObject6To7ModelInfo0', 'FLR2RdrObject6To7Qly0')
PID_OBJ7_objects_prop_t = object_prop_t(7, 'FLR2RdrObject6To7Class1', 'FLR2RdrObject6To7DataConf1', 'FLR2RdrObject6To7DataLen1', 'FLR2RdrObject6To7DataWidth1', 'FLR2RdrObject6To7HeadingAng1', 'FLR2RdrObject6To7LatAcc1', 'FLR2RdrObject6To7LatPos1', 'FLR2RdrObject6To7LatVelo1', 'FLR2RdrObject6To7LgtAcc1', 'FLR2RdrObject6To7LgtPos1', 'FLR2RdrObject6To7LgtVelo1', 'FLR2RdrObject6To7ModelInfo1', 'FLR2RdrObject6To7Qly1')
PID_OBJ6_to_7_objects_prop_t = objects_prop_t(PID_OBJ6_objects_prop_t, PID_OBJ7_objects_prop_t)
PID_OBJ6_to_7   = ObjectList_t(0x146, 0x8D1, 'FlrFlr1canFr84', 'FLR2RdrObject6To7ScanID', 'FLR2RdrObject6To7MsgCntr', PID_OBJ6_to_7_objects_prop_t)

PID_OBJ8_objects_prop_t = object_prop_t(8, 'FLR2RdrObject8To9Class0', 'FLR2RdrObject8To9DataConf0', 'FLR2RdrObject8To9DataLen0', 'FLR2RdrObject8To9DataWidth0', 'FLR2RdrObject8To9HeadingAng0', 'FLR2RdrObject8To9LatAcc0', 'FLR2RdrObject8To9LatPos0', 'FLR2RdrObject8To9LatVelo0', 'FLR2RdrObject8To9LgtAcc0', 'FLR2RdrObject8To9LgtPos0', 'FLR2RdrObject8To9LgtVelo0', 'FLR2RdrObject8To9ModelInfo0', 'FLR2RdrObject8To9Qly0')
PID_OBJ9_objects_prop_t = object_prop_t(9, 'FLR2RdrObject8To9Class1', 'FLR2RdrObject8To9DataConf1', 'FLR2RdrObject8To9DataLen1', 'FLR2RdrObject8To9DataWidth1', 'FLR2RdrObject8To9HeadingAng1', 'FLR2RdrObject8To9LatAcc1', 'FLR2RdrObject8To9LatPos1', 'FLR2RdrObject8To9LatVelo1', 'FLR2RdrObject8To9LgtAcc1', 'FLR2RdrObject8To9LgtPos1', 'FLR2RdrObject8To9LgtVelo1', 'FLR2RdrObject8To9ModelInfo1', 'FLR2RdrObject8To9Qly1')
PID_OBJ8_to_9_objects_prop_t = objects_prop_t(PID_OBJ8_objects_prop_t, PID_OBJ9_objects_prop_t)
PID_OBJ8_to_9   = ObjectList_t(0x148, 0x8D2, 'FlrFlr1canFr85', 'FLR2RdrObject8To9ScanID', 'FLR2RdrObject8To9MsgCntr', PID_OBJ8_to_9_objects_prop_t)

PID_OBJ10_objects_prop_t = object_prop_t(10, 'FLR2RdrObject10To11Class0', 'FLR2RdrObject10To11DataConf0', 'FLR2RdrObject10To11DataLen0', 'FLR2RdrObject10To11DataWidth0', 'FLR2RdrObject10To11HeadingAng0', 'FLR2RdrObject10To11LatAcc0', 'FLR2RdrObject10To11LatPos0', 'FLR2RdrObject10To11LatVelo0', 'FLR2RdrObject10To11LgtAcc0', 'FLR2RdrObject10To11LgtPos0', 'FLR2RdrObject10To11LgtVelo0', 'FLR2RdrObject10To11ModelInfo0', 'FLR2RdrObject10To11Qly0')
PID_OBJ11_objects_prop_t = object_prop_t(11, 'FLR2RdrObject10To11Class1', 'FLR2RdrObject10To11DataConf1', 'FLR2RdrObject10To11DataLen1', 'FLR2RdrObject10To11DataWidth1', 'FLR2RdrObject10To11HeadingAng1', 'FLR2RdrObject10To11LatAcc1', 'FLR2RdrObject10To11LatPos1', 'FLR2RdrObject10To11LatVelo1', 'FLR2RdrObject10To11LgtAcc1', 'FLR2RdrObject10To11LgtPos1', 'FLR2RdrObject10To11LgtVelo1', 'FLR2RdrObject10To11ModelInfo1', 'FLR2RdrObject10To11Qly1')
PID_OBJ10_to_11_objects_prop_t = objects_prop_t(PID_OBJ10_objects_prop_t, PID_OBJ11_objects_prop_t)
PID_OBJ10_to_11 = ObjectList_t(0x14A, 0x8D3, 'FlrFlr1canFr86', 'FLR2RdrObject10To11ScanID', 'FLR2RdrObject10To11MsgCntr', PID_OBJ10_to_11_objects_prop_t)

PID_OBJ12_objects_prop_t = object_prop_t(12, 'FLR2RdrObject12To13Class0', 'FLR2RdrObject12To13DataConf0', 'FLR2RdrObject12To13DataLen0', 'FLR2RdrObject12To13DataWidth0', 'FLR2RdrObject12To13HeadingAng0', 'FLR2RdrObject12To13LatAcc0', 'FLR2RdrObject12To13LatPos0', 'FLR2RdrObject12To13LatVelo0', 'FLR2RdrObject12To13LgtAcc0', 'FLR2RdrObject12To13LgtPos0', 'FLR2RdrObject12To13LgtVelo0', 'FLR2RdrObject12To13ModelInfo0', 'FLR2RdrObject12To13Qly0')
PID_OBJ13_objects_prop_t = object_prop_t(13, 'FLR2RdrObject12To13Class1', 'FLR2RdrObject12To13DataConf1', 'FLR2RdrObject12To13DataLen1', 'FLR2RdrObject12To13DataWidth1', 'FLR2RdrObject12To13HeadingAng1', 'FLR2RdrObject12To13LatAcc1', 'FLR2RdrObject12To13LatPos1', 'FLR2RdrObject12To13LatVelo1', 'FLR2RdrObject12To13LgtAcc1', 'FLR2RdrObject12To13LgtPos1', 'FLR2RdrObject12To13LgtVelo1', 'FLR2RdrObject12To13ModelInfo1', 'FLR2RdrObject12To13Qly1')
PID_OBJ12_to_13_objects_prop_t = objects_prop_t(PID_OBJ12_objects_prop_t, PID_OBJ13_objects_prop_t)
PID_OBJ12_to_13 = ObjectList_t(0x14C, 0x8D4, 'FlrFlr1canFr87', 'FLR2RdrObject12To13ScanID', 'FLR2RdrObject12To13MsgCntr', PID_OBJ12_to_13_objects_prop_t)

PID_OBJ14_objects_prop_t = object_prop_t(14, 'FLR2RdrObject14To15Class0', 'FLR2RdrObject14To15DataConf0', 'FLR2RdrObject14To15DataLen0', 'FLR2RdrObject14To15DataWidth0', 'FLR2RdrObject14To15HeadingAng0', 'FLR2RdrObject14To15LatAcc0', 'FLR2RdrObject14To15LatPos0', 'FLR2RdrObject14To15LatVelo0', 'FLR2RdrObject14To15LgtAcc0', 'FLR2RdrObject14To15LgtPos0', 'FLR2RdrObject14To15LgtVelo0', 'FLR2RdrObject14To15ModelInfo0', 'FLR2RdrObject14To15Qly0')
PID_OBJ15_objects_prop_t = object_prop_t(15, 'FLR2RdrObject14To15Class1', 'FLR2RdrObject14To15DataConf1', 'FLR2RdrObject14To15DataLen1', 'FLR2RdrObject14To15DataWidth1', 'FLR2RdrObject14To15HeadingAng1', 'FLR2RdrObject14To15LatAcc1', 'FLR2RdrObject14To15LatPos1', 'FLR2RdrObject14To15LatVelo1', 'FLR2RdrObject14To15LgtAcc1', 'FLR2RdrObject14To15LgtPos1', 'FLR2RdrObject14To15LgtVelo1', 'FLR2RdrObject14To15ModelInfo1', 'FLR2RdrObject14To15Qly1')
PID_OBJ14_to_15_objects_prop_t = objects_prop_t(PID_OBJ14_objects_prop_t, PID_OBJ15_objects_prop_t)
PID_OBJ14_to_15 = ObjectList_t(0x14E, 0x8D5, 'FlrFlr1canFr88', 'FLR2RdrObject14To15ScanID', 'FLR2RdrObject14To15MsgCntr', PID_OBJ14_to_15_objects_prop_t)

PID_OBJ16_objects_prop_t = object_prop_t(16, 'FLR2RdrObject16To17Class0', 'FLR2RdrObject16To17DataConf0', 'FLR2RdrObject16To17DataLen0', 'FLR2RdrObject16To17DataWidth0', 'FLR2RdrObject16To17HeadingAng0', 'FLR2RdrObject16To17LatAcc0', 'FLR2RdrObject16To17LatPos0', 'FLR2RdrObject16To17LatVelo0', 'FLR2RdrObject16To17LgtAcc0', 'FLR2RdrObject16To17LgtPos0', 'FLR2RdrObject16To17LgtVelo0', 'FLR2RdrObject16To17ModelInfo0', 'FLR2RdrObject16To17Qly0')
PID_OBJ17_objects_prop_t = object_prop_t(17, 'FLR2RdrObject16To17Class1', 'FLR2RdrObject16To17DataConf1', 'FLR2RdrObject16To17DataLen1', 'FLR2RdrObject16To17DataWidth1', 'FLR2RdrObject16To17HeadingAng1', 'FLR2RdrObject16To17LatAcc1', 'FLR2RdrObject16To17LatPos1', 'FLR2RdrObject16To17LatVelo1', 'FLR2RdrObject16To17LgtAcc1', 'FLR2RdrObject16To17LgtPos1', 'FLR2RdrObject16To17LgtVelo1', 'FLR2RdrObject16To17ModelInfo1', 'FLR2RdrObject16To17Qly1')
PID_OBJ16_to_17_objects_prop_t = objects_prop_t(PID_OBJ16_objects_prop_t, PID_OBJ17_objects_prop_t)
PID_OBJ16_to_17 = ObjectList_t(0x150, 0x8D6, 'FlrFlr1canFr89', 'FLR2RdrObject16To17ScanID', 'FLR2RdrObject16To17MsgCntr', PID_OBJ16_to_17_objects_prop_t)

PID_OBJ18_objects_prop_t = object_prop_t(18, 'FLR2RdrObject18To19Class0', 'FLR2RdrObject18To19DataConf0', 'FLR2RdrObject18To19DataLen0', 'FLR2RdrObject18To19DataWidth0', 'FLR2RdrObject18To19HeadingAng0', 'FLR2RdrObject18To19LatAcc0', 'FLR2RdrObject18To19LatPos0', 'FLR2RdrObject18To19LatVelo0', 'FLR2RdrObject18To19LgtAcc0', 'FLR2RdrObject18To19LgtPos0', 'FLR2RdrObject18To19LgtVelo0', 'FLR2RdrObject18To19ModelInfo0', 'FLR2RdrObject18To19Qly0')
PID_OBJ19_objects_prop_t = object_prop_t(19, 'FLR2RdrObject18To19Class1', 'FLR2RdrObject18To19DataConf1', 'FLR2RdrObject18To19DataLen1', 'FLR2RdrObject18To19DataWidth1', 'FLR2RdrObject18To19HeadingAng1', 'FLR2RdrObject18To19LatAcc1', 'FLR2RdrObject18To19LatPos1', 'FLR2RdrObject18To19LatVelo1', 'FLR2RdrObject18To19LgtAcc1', 'FLR2RdrObject18To19LgtPos1', 'FLR2RdrObject18To19LgtVelo1', 'FLR2RdrObject18To19ModelInfo1', 'FLR2RdrObject18To19Qly1')
PID_OBJ18_to_19_objects_prop_t = objects_prop_t(PID_OBJ18_objects_prop_t, PID_OBJ19_objects_prop_t)
PID_OBJ18_to_19 = ObjectList_t(0x152, 0x8D7, 'FlrFlr1canFr90', 'FLR2RdrObject18To19ScanID', 'FLR2RdrObject18To19MsgCntr', PID_OBJ18_to_19_objects_prop_t)

PID_OBJ20_objects_prop_t = object_prop_t(20, 'FLR2RdrObject20To21Class0', 'FLR2RdrObject20To21DataConf0', 'FLR2RdrObject20To21DataLen0', 'FLR2RdrObject20To21DataWidth0', 'FLR2RdrObject20To21HeadingAng0', 'FLR2RdrObject20To21LatAcc0', 'FLR2RdrObject20To21LatPos0', 'FLR2RdrObject20To21LatVelo0', 'FLR2RdrObject20To21LgtAcc0', 'FLR2RdrObject20To21LgtPos0', 'FLR2RdrObject20To21LgtVelo0', 'FLR2RdrObject20To21ModelInfo0', 'FLR2RdrObject20To21Qly0')
PID_OBJ21_objects_prop_t = object_prop_t(21, 'FLR2RdrObject20To21Class1', 'FLR2RdrObject20To21DataConf1', 'FLR2RdrObject20To21DataLen1', 'FLR2RdrObject20To21DataWidth1', 'FLR2RdrObject20To21HeadingAng1', 'FLR2RdrObject20To21LatAcc1', 'FLR2RdrObject20To21LatPos1', 'FLR2RdrObject20To21LatVelo1', 'FLR2RdrObject20To21LgtAcc1', 'FLR2RdrObject20To21LgtPos1', 'FLR2RdrObject20To21LgtVelo1', 'FLR2RdrObject20To21ModelInfo1', 'FLR2RdrObject20To21Qly1')
PID_OBJ20_to_21_objects_prop_t = objects_prop_t(PID_OBJ20_objects_prop_t, PID_OBJ21_objects_prop_t)
PID_OBJ20_to_21 = ObjectList_t(0x154, 0x8A9, 'FlrFlr1canFr91', 'FLR2RdrObject20To21ScanID', 'FLR2RdrObject20To21MsgCntr', PID_OBJ20_to_21_objects_prop_t)

PID_OBJ22_objects_prop_t = object_prop_t(22, 'FLR2RdrObject22To23Class0', 'FLR2RdrObject22To23DataConf0', 'FLR2RdrObject22To23DataLen0', 'FLR2RdrObject22To23DataWidth0', 'FLR2RdrObject22To23HeadingAng0', 'FLR2RdrObject22To23LatAcc0', 'FLR2RdrObject22To23LatPos0', 'FLR2RdrObject22To23LatVelo0', 'FLR2RdrObject22To23LgtAcc0', 'FLR2RdrObject22To23LgtPos0', 'FLR2RdrObject22To23LgtVelo0', 'FLR2RdrObject22To23ModelInfo0', 'FLR2RdrObject22To23Qly0')
PID_OBJ23_objects_prop_t = object_prop_t(23, 'FLR2RdrObject22To23Class1', 'FLR2RdrObject22To23DataConf1', 'FLR2RdrObject22To23DataLen1', 'FLR2RdrObject22To23DataWidth1', 'FLR2RdrObject22To23HeadingAng1', 'FLR2RdrObject22To23LatAcc1', 'FLR2RdrObject22To23LatPos1', 'FLR2RdrObject22To23LatVelo1', 'FLR2RdrObject22To23LgtAcc1', 'FLR2RdrObject22To23LgtPos1', 'FLR2RdrObject22To23LgtVelo1', 'FLR2RdrObject22To23ModelInfo1', 'FLR2RdrObject22To23Qly1')
PID_OBJ22_to_23_objects_prop_t = objects_prop_t(PID_OBJ22_objects_prop_t, PID_OBJ23_objects_prop_t)
PID_OBJ22_to_23 = ObjectList_t(0x156, 0x8AA, 'FlrFlr1canFr92', 'FLR2RdrObject22To23ScanID', 'FLR2RdrObject22To23MsgCntr', PID_OBJ22_to_23_objects_prop_t)

PID_OBJ24_objects_prop_t = object_prop_t(24, 'FLR2RdrObject24To25Class0', 'FLR2RdrObject24To25DataConf0', 'FLR2RdrObject24To25DataLen0', 'FLR2RdrObject24To25DataWidth0', 'FLR2RdrObject24To25HeadingAng0', 'FLR2RdrObject24To25LatAcc0', 'FLR2RdrObject24To25LatPos0', 'FLR2RdrObject24To25LatVelo0', 'FLR2RdrObject24To25LgtAcc0', 'FLR2RdrObject24To25LgtPos0', 'FLR2RdrObject24To25LgtVelo0', 'FLR2RdrObject24To25ModelInfo0', 'FLR2RdrObject24To25Qly0')
PID_OBJ25_objects_prop_t = object_prop_t(25, 'FLR2RdrObject24To25Class1', 'FLR2RdrObject24To25DataConf1', 'FLR2RdrObject24To25DataLen1', 'FLR2RdrObject24To25DataWidth1', 'FLR2RdrObject24To25HeadingAng1', 'FLR2RdrObject24To25LatAcc1', 'FLR2RdrObject24To25LatPos1', 'FLR2RdrObject24To25LatVelo1', 'FLR2RdrObject24To25LgtAcc1', 'FLR2RdrObject24To25LgtPos1', 'FLR2RdrObject24To25LgtVelo1', 'FLR2RdrObject24To25ModelInfo1', 'FLR2RdrObject24To25Qly1')
PID_OBJ24_to_25_objects_prop_t = objects_prop_t(PID_OBJ24_objects_prop_t, PID_OBJ25_objects_prop_t)
PID_OBJ24_to_25 = ObjectList_t(0x158, 0x8AB, 'FlrFlr1canFr93', 'FLR2RdrObject24To25ScanID', 'FLR2RdrObject24To25MsgCntr', PID_OBJ24_to_25_objects_prop_t)

PID_OBJ26_objects_prop_t = object_prop_t(26, 'FLR2RdrObject26To27Class0', 'FLR2RdrObject26To27DataConf0', 'FLR2RdrObject26To27DataLen0', 'FLR2RdrObject26To27DataWidth0', 'FLR2RdrObject26To27HeadingAng0', 'FLR2RdrObject26To27LatAcc0', 'FLR2RdrObject26To27LatPos0', 'FLR2RdrObject26To27LatVelo0', 'FLR2RdrObject26To27LgtAcc0', 'FLR2RdrObject26To27LgtPos0', 'FLR2RdrObject26To27LgtVelo0', 'FLR2RdrObject26To27ModelInfo0', 'FLR2RdrObject26To27Qly0')
PID_OBJ27_objects_prop_t = object_prop_t(27, 'FLR2RdrObject26To27Class1', 'FLR2RdrObject26To27DataConf1', 'FLR2RdrObject26To27DataLen1', 'FLR2RdrObject26To27DataWidth1', 'FLR2RdrObject26To27HeadingAng1', 'FLR2RdrObject26To27LatAcc1', 'FLR2RdrObject26To27LatPos1', 'FLR2RdrObject26To27LatVelo1', 'FLR2RdrObject26To27LgtAcc1', 'FLR2RdrObject26To27LgtPos1', 'FLR2RdrObject26To27LgtVelo1', 'FLR2RdrObject26To27ModelInfo1', 'FLR2RdrObject26To27Qly1')
PID_OBJ26_to_27_objects_prop_t = objects_prop_t(PID_OBJ26_objects_prop_t, PID_OBJ27_objects_prop_t)
PID_OBJ26_to_27 = ObjectList_t(0x15A, 0x8AC, 'FlrFlr1canFr94', 'FLR2RdrObject26To27ScanID', 'FLR2RdrObject26To27MsgCntr', PID_OBJ26_to_27_objects_prop_t)

PID_OBJ28_objects_prop_t = object_prop_t(28, 'FLR2RdrObject28To29Class0', 'FLR2RdrObject28To29DataConf0', 'FLR2RdrObject28To29DataLen0', 'FLR2RdrObject28To29DataWidth0', 'FLR2RdrObject28To29HeadingAng0', 'FLR2RdrObject28To29LatAcc0', 'FLR2RdrObject28To29LatPos0', 'FLR2RdrObject28To29LatVelo0', 'FLR2RdrObject28To29LgtAcc0', 'FLR2RdrObject28To29LgtPos0', 'FLR2RdrObject28To29LgtVelo0', 'FLR2RdrObject28To29ModelInfo0', 'FLR2RdrObject28To29Qly0')
PID_OBJ29_objects_prop_t = object_prop_t(29, 'FLR2RdrObject28To29Class1', 'FLR2RdrObject28To29DataConf1', 'FLR2RdrObject28To29DataLen1', 'FLR2RdrObject28To29DataWidth1', 'FLR2RdrObject28To29HeadingAng1', 'FLR2RdrObject28To29LatAcc1', 'FLR2RdrObject28To29LatPos1', 'FLR2RdrObject28To29LatVelo1', 'FLR2RdrObject28To29LgtAcc1', 'FLR2RdrObject28To29LgtPos1', 'FLR2RdrObject28To29LgtVelo1', 'FLR2RdrObject28To29ModelInfo1', 'FLR2RdrObject28To29Qly1')
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

def process_rx_radar(radar_dbc:database.database.Database, can_bus_radar):
    global message_radar, message_car
    reference_ID = list_of_Object_attr[0].arbitration_id

    #treat Object list 
    try:
        if(os_name != 'Windows') and distro_name != 'Ubuntu':
            message_radar = can_bus_radar.recv(timeout=0.1)
        # treat only specific range of messages
        if message_radar.arbitration_id >= list_of_Object_attr[0].arbitration_id and message_radar.arbitration_id < list_of_Object_attr[-1].arbitration_id:
            for entry in list_of_Object_attr:
                if(entry.arbitration_id == message_radar.arbitration_id):
                    if e2e.p05.e2e_p05_check(message_radar.data, message_radar.dlc, data_id=entry.e2e_DataId) is True:
                        # Retrieve the decoded message once
                        decoded_message = radar_dbc.get_message_by_frame_id(message_radar.arbitration_id)

                        # Update ObjList_VIEW MsgCntr and ScanID
                        ObjList_VIEW.MsgCntr = decoded_message.get_signal_by_name(entry.MsgCntr)
                        ObjList_VIEW.ScanID = decoded_message.get_signal_by_name(entry.ScanID)

                        # Calculate the index for object_list_for_draw
                        index_entry = entry.arbitration_id - reference_ID

                        # Update the first object properties
                        first_obj_prop = entry.msg_obj_prop.first_obj_prop
                        ObjList_VIEW.object_list_for_draw[index_entry] = object_list_for_draw_t(
                            object_id=first_obj_prop.object_id,
                            Class=decoded_message.get_signal_by_name(first_obj_prop.Class),
                            DataConf=decoded_message.get_signal_by_name(first_obj_prop.DataConf),
                            DataLen=decoded_message.get_signal_by_name(first_obj_prop.DataLen),
                            DataWidth=decoded_message.get_signal_by_name(first_obj_prop.DataWidth),
                            HeadingAng=decoded_message.get_signal_by_name(first_obj_prop.HeadingAng),
                            LatAcc=decoded_message.get_signal_by_name(first_obj_prop.LatAcc),
                            LatPos=decoded_message.get_signal_by_name(first_obj_prop.LatPos),
                            LatVelo=decoded_message.get_signal_by_name(first_obj_prop.LatVelo),
                            LgtAcc=decoded_message.get_signal_by_name(first_obj_prop.LgtAcc),
                            LgtPos=decoded_message.get_signal_by_name(first_obj_prop.LgtPos),
                            LgtVelo=decoded_message.get_signal_by_name(first_obj_prop.LgtVelo),
                            ModelInfo=decoded_message.get_signal_by_name(first_obj_prop.ModelInfo),
                            Qly=decoded_message.get_signal_by_name(first_obj_prop.Qly)
                        )
                        
                        # Update the second object properties
                        second_obj_prop = entry.msg_obj_prop.second_obj_prop
                        ObjList_VIEW.object_list_for_draw[index_entry + 1] = object_list_for_draw_t(
                            object_id=second_obj_prop.object_id,
                            Class=decoded_message.get_signal_by_name(second_obj_prop.Class),
                            DataConf=decoded_message.get_signal_by_name(second_obj_prop.DataConf),
                            DataLen=decoded_message.get_signal_by_name(second_obj_prop.DataLen),
                            DataWidth=decoded_message.get_signal_by_name(second_obj_prop.DataWidth),
                            HeadingAng=decoded_message.get_signal_by_name(second_obj_prop.HeadingAng),
                            LatAcc=decoded_message.get_signal_by_name(second_obj_prop.LatAcc),
                            LatPos=decoded_message.get_signal_by_name(second_obj_prop.LatPos),
                            LatVelo=decoded_message.get_signal_by_name(second_obj_prop.LatVelo),
                            LgtAcc=decoded_message.get_signal_by_name(second_obj_prop.LgtAcc),
                            LgtPos=decoded_message.get_signal_by_name(second_obj_prop.LgtPos),
                            LgtVelo=decoded_message.get_signal_by_name(second_obj_prop.LgtVelo),
                            ModelInfo=decoded_message.get_signal_by_name(second_obj_prop.ModelInfo),
                            Qly=decoded_message.get_signal_by_name(second_obj_prop.Qly)
                        )
                        print('arbitration_id:', message_radar.arbitration_id)
    except OSError as e:
        print(f'\n\rNo bus from radar!!: {e}')
        os._exit(0)
  
    return ObjList_VIEW
'''
| CAN ID (hex)    | Function (Suspected / Confirmed)                    |
| --------------- | --------------------------------------------------- |
| `0x1A6`         | Engine RPM (tachometer signal)                      |
| `0x1F0`         | Vehicle speed                                       |
| `0x329`         | Steering angle                                      |
| `0x17C`         | Accelerator pedal position                          |
| `0x324`         | Brake pedal status                                  |
| `0x1A0`         | Gear position (on automatic)                        |
| `0x30C`         | Wheel speeds (individual or averaged)               |
| `0x18F`         | Fuel level / fuel-related data                      |
| `0x280`         | Lights, indicators (turn signals, headlight status) |
| `0x130`         | Door open/close status                              |
| `0x1D0`         | HVAC / climate control                              |
| `0x100`–`0x120` | Dashboard-related signals (varies by model)         |

or

https://github.com/Knio/carhack/blob/master/Cars/Honda.markdown
'''
def process_rx_car(can_bus_car):
    global message_car
        
    try:
        if(os_name != 'Windows') and distro_name != 'Ubuntu':
            message_car = can_bus_car.recv(timeout=0.1)
        if message_car.arbitration_id == VEHICLE_SPEED:
            EgoMotion_data.Speed = 0#radar_dbc.get_message_by_frame_id(message_car.arbitration_id).get_signal_by_name('FLR2RdrVehicleSpeed')
        
        if message_car.arbitration_id == WHEEL_SPEED:
            EgoMotion_data.Left_wheel_speed = 0#radar_dbc.get_message_by_frame_id(message_car.arbitration_id).get_signal_by_name('FLR2RdrLeftWheelSpeed')
            EgoMotion_data.Right_wheel_speed = 0#radar_dbc.get_message_by_frame_id(message_car.arbitration_id).get_signal_by_name('FLR2RdrRightWheelSpeed')
            #EgoMotion_data.YawRate = db.get_message_by_frame_id(message_car.arbitration_id).get_signal_by_name('FLR2RdrYawRate')
            #EgoMotion_data.LatAcc = db.get_message_by_frame_id(message_car.arbitration_id).get_signal_by_name('FLR2RdrLatAcc')
            #EgoMotion_data.LongAcc = db.get_message_by_frame_id(message_car.arbitration_id).get_signal_by_name('FLR2RdrLongAcc')
            print('arbitration_id:', message_car.arbitration_id)
            print('Decoded:', message_car.data)
    except OSError as e:
        print(f'\n\rNo bus from car!!: {e}')
        os._exit(0)

    return EgoMotion_data