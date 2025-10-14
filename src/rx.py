import can
import cantools
from cantools import database
import time
import os
import e2e
from dataclasses import dataclass, field
from can import Message
from typing import List, Tuple, Dict, Optional
from defines import *

# Initialize default CAN messages as module constants
DEFAULT_RADAR_MESSAGE = Message(
    arbitration_id=0x000,
    data=[],
    dlc=0,
    is_extended_id=False,
    is_fd=True
)

DEFAULT_CAR_MESSAGE = Message(
    arbitration_id=0x000,
    data=[],
    dlc=0,
    is_extended_id=False,
    is_fd=True
)

# Global message variables
message_radar = DEFAULT_RADAR_MESSAGE
message_car = DEFAULT_CAR_MESSAGE

# Vehicle CAN IDs - Honda/Volvo compatible
VEHICLE_SPEED = 0x164  # Vehicle Speed
WHEEL_SPEED = 0x309    # Left/Right wheel speeds

@dataclass(frozen=True)
class EgoMotion:
    """Vehicle ego motion data structure"""
    speed: float = 0.0
    left_wheel_speed: float = 0.0
    right_wheel_speed: float = 0.0
    yaw_rate: int = 0
    lat_acc: int = 0
    long_acc: int = 0

# Global ego motion instance
ego_motion_data = EgoMotion()
####################################################################
@dataclass
class ObjectDrawData:
    """Optimized object data for drawing operations"""
    object_id: int
    class_type: int = 0
    data_conf: int = 0
    data_len: float = 0.0
    data_width: float = 0.0
    heading_angle: float = 0.0
    lat_acc: float = 0.0
    lat_pos: int = 0
    lat_velocity: float = 0.0
    lgt_acc: float = 0.0
    lgt_pos: int = 0
    lgt_velocity: float = 0.0
    model_info: int = 0
    quality: int = 0
    
@dataclass
class RadarView:
    """Optimized radar object view container"""
    msg_counter: int = 0
    scan_id: int = 0
    object_list_for_draw: List[ObjectDrawData] = field(
        default_factory=lambda: [ObjectDrawData(object_id=i) for i in range(30)]
    )

# Global radar view instance  
radar_view = RadarView()
####################################################################    
@dataclass(frozen=True)
class ObjectProperty:
    """Immutable object property definition for CAN signals"""
    object_id: int
    class_signal: str
    data_conf_signal: str
    data_len_signal: str
    data_width_signal: str
    heading_angle_signal: str
    lat_acc_signal: str
    lat_pos_signal: str
    lat_velocity_signal: str
    lgt_acc_signal: str
    lgt_pos_signal: str
    lgt_velocity_signal: str
    model_info_signal: str
    quality_signal: str
    
    
@dataclass(frozen=True)
class ObjectPairProperties:
    """Container for paired object properties"""
    first_obj_prop: ObjectProperty
    second_obj_prop: ObjectProperty

@dataclass(frozen=True)
class ObjectList:
    """CAN object list configuration"""
    arbitration_id: int
    e2e_data_id: int
    msg_name: str
    msg_counter_signal: str
    scan_id_signal: str
    msg_obj_prop: ObjectPairProperties
    
@dataclass
class CanSnifferData:
    """Container for CAN sniffer display data"""
    messages: List[str] = field(default_factory=list)
    max_messages: int = 20
    enabled: bool = False
    
    def add_message(self, arbitration_id: int, data: bytes, timestamp: float = None):
        """Add a new CAN message to the display buffer"""
        if not self.enabled:
            return
            
        timestamp_str = f"{time.time():.3f}" if timestamp is None else f"{timestamp:.3f}"
        data_hex = data.hex().upper() if data else "00"
        message_str = f"ID: 0x{arbitration_id:03X} | Data: {data_hex} | Time: {timestamp_str}"
        
        # Add to front of list and limit size
        self.messages.insert(0, message_str)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[:self.max_messages]

SIGNAL_STATUS_CAN_ID = 0x45  # 69 decimal - FlrFlr1canFr96
@dataclass
class FlrFlr1canFr96:
    """
    Radar Signal Status Frame (CAN ID: 0x45 / 69 decimal)
    64-byte frame containing radar system status and calibration information
    """
    # CRC and Counter (E2E protection)
    crc: int = 0                           # FLR2SignalStatusCRC: 0|16@1+ (1.0,0.0) [0.0|65535.0] "Unitless"
    counter: int = 0                       # FLR2SignalStatusCounter: 16|8@1+ (1.0,0.0) [0.0|255.0] "Unitless"
    
    # Temperature and Environment
    internal_temp: float = -40.0           # FLR2SignalStatusInternalTemp: 24|15@1+ (0.01,-40.0) [-40.0|215.0] "degC"
    timestamp: int = 0                     # FLR2SignalStatusTimeStamp: 56|64@1+ (1.0,0.0) [0.0|0.0] "Milliseconds"
    
    # Position and Orientation Offsets
    y_axis_offs: float = -25.0             # FLR2SignalStatusYAxisOffs: 120|16@1+ (0.00145,-25.0) [-25.0|25.0] "m"
    z_axis_offs: float = -25.0             # FLR2SignalStatusZAxisOffs: 136|16@1+ (0.00145240648,-25.0) [-25.0|25.0] "m"
    
    # Speed and Motion Estimation
    ego_spd_est: float = 0.0               # FLR2SignalStatusEgoSpdEst: 152|15@1+ (0.00391,0.0) [0.0|125.0] "m/s"
    ego_yaw_rate_est: float = 0.0          # FLR2SignalStatusEgoYawRateEst: 272|16@1- (0.000244140625,0.0) [-6.0|6.0] "rad/s"
    
    # Orientation Angles
    x_orient_ang: float = -180.0           # FLR2SignalStatusXOrientAng: 200|12@1+ (0.1,-180.0) [-180.0|180.0] "Deg"
    y_orient_ang: float = -180.0           # FLR2SignalStatusYOrientAng: 216|12@1+ (0.1,-180.0) [-180.0|180.0] "Deg" 
    z_orient_ang: float = -180.0           # FLR2SignalStatusZOrientAng: 232|12@1+ (0.1,-180.0) [-180.0|180.0] "Deg"
    
    # Angle Corrections
    azi_ang_cor: float = -12.8             # FLR2SignalStatusAziAngCor: 248|8@1+ (0.1,-12.8) [-12.8|12.7] "Deg"
    ele_ang_cor: float = -12.8             # FLR2SignalStatusEleAngCor: 320|8@1+ (0.1,-12.8) [-12.8|12.7] "Deg"
    
    # Position Offset (X-axis)
    x_axis_offs: float = -25.0             # FLR2SignalStatusXAxisOffs: 288|16@1+ (0.00145204372,-25.0) [-25.0|25.0] "m"
    
    # Calibration Status
    cal_prgrss_sts: int = 0                # FLR2SignalStatusCalPrgrsSts: 304|8@1+ (1.0,0.0) [0.0|255.0] "Unitless"
    whl_comp_fact: float = 0.92            # FLR2SignalStatusWhlCompFact: 264|5@1+ (0.005,0.92) [0.92|1.075] "Unitless"
    
    # Software/Interface Versions
    if_vers_major: int = 0                 # FLR2SignalStatusIfVersMajor: 212|4@1+ (1.0,0.0) [0.0|15.0] "Unitless"
    if_vers_minor: int = 0                 # FLR2SignalStatusIfVersMinor: 228|4@1+ (1.0,0.0) [0.0|15.0] "Unitless"
    sw_vers_major: int = 0                 # FLR2SignalStatusSwVersMajor: 184|8@1+ (1.0,0.0) [0.0|255.0] "Unitless"
    sw_vers_minor: int = 0                 # FLR2SignalStatusSwVersMinor: 192|8@1+ (1.0,0.0) [0.0|255.0] "Unitless"
    
    # Status Information
    scan_id_sts: int = 0                   # FLR2SignalStatusScanIDSts: 176|8@1+ (1.0,0.0) [0.0|255.0] "Unitless"
    timestamp_status: bool = False         # FLR2SignalStatusTimeStampStatus: 167|1@1+ (1,0) [0|1] ""
    
    # Fault and Error Flags
    flt_reason: int = 0                    # FLR2SignalStatusFltReason: 168|5@1+ (1,0) [0|31] ""
    comm_flt_reason: int = 0               # FLR2SignalStatusCommFltReason: 312|7@1+ (1,0) [0|127] ""
    rdr_int_sts: int = 0                   # FLR2SignalStatusRdrIntSts: 173|3@1+ (1,0) [0|7] ""
    
    # System Status Flags (2-bit values)
    cal_sts: int = 0                       # FLR2SignalStatusCalSts: 244|2@1+ (1,0) [0|3] ""
    cal_rlt_sts: int = 0                   # FLR2SignalStatusCalRltSts: 260|2@1+ (1,0) [0|3] ""
    blockage: int = 0                      # FLR2SignalStatusBlockage: 258|2@1+ (1,0) [0|3] ""
    interference: int = 0                  # FLR2SignalStatusInterference: 256|2@1+ (1,0) [0|3] ""
    
    # Single-bit Status Flags  
    sys_fail_flag: bool = False            # FLR2SignalStatusSysFailFlag: 246|1@1+ (1,0) [0|1] ""
    rdr_sts: bool = False                  # FLR2SignalStatusRdrSts: 247|1@1+ (1,0) [0|1] ""
    rdr_trans_act: bool = False            # FLR2SignalStatusRdrTransAct: 263|1@1+ (1,0) [0|1] ""
    signal_status_ub: bool = False         # FLR2SignalStatus_UB: 335|1@0+ (1,0) [0|1] ""

# Global radar signal status instance
radar_signal_status = FlrFlr1canFr96()

'''
BO_ 69 FlrFlr1canFr96 : 64 FLR
 SG_ FLR2SignalStatus_UB : 335|1@0+ (1,0) [0|1] "" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusAziAngCor : 248|8@1+ (0.1,-12.8) [-12.8|12.7] "Deg" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusBlockage : 258|2@1+ (1,0) [0|3] "" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusCalPrgrsSts : 304|8@1+ (1.0,0.0) [0.0|255.0] "Unitless" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusCalRltSts : 260|2@1+ (1,0) [0|3] "" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusCalSts : 244|2@1+ (1,0) [0|3] "" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusCommFltReason : 312|7@1+ (1,0) [0|127] "" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusCounter : 16|8@1+ (1.0,0.0) [0.0|255.0] "Unitless" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusCRC : 0|16@1+ (1.0,0.0) [0.0|65535.0] "Unitless" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusEgoSpdEst : 152|15@1+ (0.00391,0.0) [0.0|125.0027] "m/s" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusEgoYawRateEst : 272|16@1- (0.000244140625,0.0) [-6.0|6.0] "rad/s" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusEleAngCor : 320|8@1+ (0.1,-12.8) [-12.8|12.7] "Deg" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusFltReason : 168|5@1+ (1,0) [0|31] "" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusIfVersMajor : 212|4@1+ (1.0,0.0) [0.0|15.0] "Unitless" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusIfVersMinor : 228|4@1+ (1.0,0.0) [0.0|15.0] "Unitless" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusInterference : 256|2@1+ (1,0) [0|3] "" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusInternalTemp : 24|15@1+ (0.01,-40.0) [-40.0|215.0] "degC" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusRdrIntSts : 173|3@1+ (1,0) [0|7] "" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusRdrSts : 247|1@1+ (1,0) [0|1] "" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusRdrTransAct : 263|1@1+ (1,0) [0|1] "" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusScanIDSts : 176|8@1+ (1.0,0.0) [0.0|255.0] "Unitless" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusSwVersMajor : 184|8@1+ (1.0,0.0) [0.0|255.0] "Unitless" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusSwVersMinor : 192|8@1+ (1.0,0.0) [0.0|255.0] "Unitless" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusSysFailFlag : 246|1@1+ (1,0) [0|1] "" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusTimeStamp : 56|64@1+ (1.0,0.0) [0.0|0.0] "Milliseconds" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusTimeStampStatus : 167|1@1+ (1,0) [0|1] "" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusWhlCompFact : 264|5@1+ (0.005,0.92) [0.92|1.075] "Unitless" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusXAxisOffs : 288|16@1+ (0.00145204372,-25.0) [-25.0|25.001125498200004] "m" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusXOrientAng : 200|12@1+ (0.1,-180.0) [-180.0|180.0] "Deg" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusYAxisOffs : 120|16@1+ (0.00145,-25.0) [-25.0|25.000349999999997] "m" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusYOrientAng : 216|12@1+ (0.1,-180.0) [-180.0|180.0] "Deg" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusZAxisOffs : 136|16@1+ (0.00145240648,-25.0) [-25.0|25.00054548048] "m" FLRdpHPA,FLRdpHPB
 SG_ FLR2SignalStatusZOrientAng : 232|12@1+ (0.1,-180.0) [-180.0|180.0] "Deg" FLRdpHPA,FLRdpHPB
 '''
# Global CAN sniffer instance
can_sniffer = CanSnifferData()

# Optimized object configuration with type annotations
OBJECT_CONFIG: Dict[Tuple[int, int], Tuple[int, int, str, str, str]] = {
    (0, 1): (0x140, 0x8CF, 'FlrFlr1canFr82', 'FLR2RdrObject0To1ScanID', 'FLR2RdrObject0To1MsgCntr'),
    (2, 3): (0x142, 0x8D0, 'FlrFlr1canFr83', 'FLR2RdrObject2To3ScanID', 'FLR2RdrObject2To3MsgCntr'),
    (4, 5): (0x144, 0x8D1, 'FlrFlr1canFr84', 'FLR2RdrObject4To5ScanID', 'FLR2RdrObject4To5MsgCntr'),
    (6, 7): (0x146, 0x8D2, 'FlrFlr1canFr85', 'FLR2RdrObject6To7ScanID', 'FLR2RdrObject6To7MsgCntr'),
    (8, 9): (0x148, 0x8D3, 'FlrFlr1canFr86', 'FLR2RdrObject8To9ScanID', 'FLR2RdrObject8To9MsgCntr'),
    (10, 11): (0x14A, 0x8D3, 'FlrFlr1canFr86', 'FLR2RdrObject10To11ScanID', 'FLR2RdrObject10To11MsgCntr'),
    (12, 13): (0x14C, 0x8D4, 'FlrFlr1canFr87', 'FLR2RdrObject12To13ScanID', 'FLR2RdrObject12To13MsgCntr'),
    (14, 15): (0x14E, 0x8D5, 'FlrFlr1canFr88', 'FLR2RdrObject14To15ScanID', 'FLR2RdrObject14To15MsgCntr'),
    (16, 17): (0x150, 0x8D6, 'FlrFlr1canFr89', 'FLR2RdrObject16To17ScanID', 'FLR2RdrObject16To17MsgCntr'),
    (18, 19): (0x152, 0x8D7, 'FlrFlr1canFr90', 'FLR2RdrObject18To19ScanID', 'FLR2RdrObject18To19MsgCntr'),
    (20, 21): (0x154, 0x8A9, 'FlrFlr1canFr91', 'FLR2RdrObject20To21ScanID', 'FLR2RdrObject20To21MsgCntr'),
    (22, 23): (0x156, 0x8AA, 'FlrFlr1canFr92', 'FLR2RdrObject22To23ScanID', 'FLR2RdrObject22To23MsgCntr'),
    (24, 25): (0x158, 0x8AB, 'FlrFlr1canFr93', 'FLR2RdrObject24To25ScanID', 'FLR2RdrObject24To25MsgCntr'),
    (26, 27): (0x15A, 0x8AC, 'FlrFlr1canFr94', 'FLR2RdrObject26To27ScanID', 'FLR2RdrObject26To27MsgCntr'),
    (28, 29): (0x15C, 0x8AD, 'FlrFlr1canFr95', 'FLR2RdrObject28To29ScanID', 'FLR2RdrObject28To29MsgCntr'),
}

def create_object_property(obj_id: int, start_obj: int, end_obj: int, prop_index: int) -> ObjectProperty:
    """Create object properties dynamically with improved naming"""
    base_name = f'FLR2RdrObject{start_obj}To{end_obj}'
    return ObjectProperty(
        object_id=obj_id,
        class_signal=f'{base_name}Class{prop_index}',
        data_conf_signal=f'{base_name}DataConf{prop_index}',
        data_len_signal=f'{base_name}DataLen{prop_index}',
        data_width_signal=f'{base_name}DataWidth{prop_index}',
        heading_angle_signal=f'{base_name}HeadingAng{prop_index}',
        lat_acc_signal=f'{base_name}LatAcc{prop_index}',
        lat_pos_signal=f'{base_name}LatPos{prop_index}',
        lat_velocity_signal=f'{base_name}LatVelo{prop_index}',
        lgt_acc_signal=f'{base_name}LgtAcc{prop_index}',
        lgt_pos_signal=f'{base_name}LgtPos{prop_index}',
        lgt_velocity_signal=f'{base_name}LgtVelo{prop_index}',
        model_info_signal=f'{base_name}ModelInfo{prop_index}',
        quality_signal=f'{base_name}Qly{prop_index}'
    )

def create_object_lists() -> Tuple[ObjectList, ...]:
    """Create all object lists dynamically with optimized structure"""
    object_lists = []
    
    for (start_obj, end_obj), (arb_id, e2e_id, frame_name, scan_id, msg_cntr) in OBJECT_CONFIG.items():
        # Create object properties for both objects in the pair
        obj_prop_0 = create_object_property(start_obj, start_obj, end_obj, 0)
        obj_prop_1 = create_object_property(end_obj, start_obj, end_obj, 1)
        
        # Create objects property container
        objects_prop = ObjectPairProperties(obj_prop_0, obj_prop_1)
        
        # Create object list
        obj_list = ObjectList(arb_id, e2e_id, frame_name, scan_id, msg_cntr, objects_prop)
        object_lists.append(obj_list)
    
    return tuple(object_lists)

# Create all object lists dynamically (cached at module level)
object_attribute_list: Tuple[ObjectList, ...] = create_object_lists()

def update_object_data(decoded_message: dict, obj_prop: ObjectProperty, index: int) -> None:
    """Helper function to update object data efficiently"""
    radar_view.object_list_for_draw[index] = ObjectDrawData(
        object_id=obj_prop.object_id,
        class_type=decoded_message.get(obj_prop.class_signal, 0),
        data_conf=decoded_message.get(obj_prop.data_conf_signal, 0),
        data_len=decoded_message.get(obj_prop.data_len_signal, 0.0),
        data_width=decoded_message.get(obj_prop.data_width_signal, 0.0),
        heading_angle=decoded_message.get(obj_prop.heading_angle_signal, 0.0),
        lat_acc=decoded_message.get(obj_prop.lat_acc_signal, 0.0),
        lat_pos=decoded_message.get(obj_prop.lat_pos_signal, 0),
        lat_velocity=decoded_message.get(obj_prop.lat_velocity_signal, 0.0),
        lgt_acc=decoded_message.get(obj_prop.lgt_acc_signal, 0.0),
        lgt_pos=decoded_message.get(obj_prop.lgt_pos_signal, 0),
        lgt_velocity=decoded_message.get(obj_prop.lgt_velocity_signal, 0.0),
        model_info=decoded_message.get(obj_prop.model_info_signal, 0),
        quality=decoded_message.get(obj_prop.quality_signal, 0)
    )
def process_RadarStatus_CAN0(radar_dbc: database.Database, message_radar) -> FlrFlr1canFr96:
    """
    Process radar signal status frame (CAN ID: 0x45 / 69 decimal)
    Decodes FlrFlr1canFr96 frame and updates global radar_signal_status
    """
    global radar_signal_status  # Add this line to access the global instance
    
    try:
        print(f'Received signal status frame 0x{SIGNAL_STATUS_CAN_ID:03X} with {len(message_radar.data)} bytes')
        '''       
        # E2E protection check (temporarily disabled for debugging)
        # TODO: Enable E2E protection with correct data_id once confirmed
        try:
            if not e2e.p05.e2e_p05_check(message_radar.data, message_radar.dlc-2, data_id=0x8D8):
                print(f'E2E protection failed for signal status frame 0x{SIGNAL_STATUS_CAN_ID:03X}, continuing anyway...')
                # Continue processing even if E2E fails for now
        except Exception as e:
            print(f'E2E check error: {e}, continuing anyway...')
        '''   
        # Decode the message using DBC
        decoded_message = radar_dbc.decode_message(message_radar.arbitration_id, message_radar.data)

        # Helper function to safely get and convert values from decoded message
        def safe_get(signal_name, default_value, value_type=None):
            try:
                # Cantools decoded message can be accessed like a dictionary
                value = decoded_message[signal_name] if signal_name in decoded_message else default_value
                
                # Convert to appropriate type with explicit casting
                if value_type == int:
                    return int(float(value))  # Convert via float first to handle scientific notation
                elif value_type == float:
                    return float(value)
                elif value_type == bool:
                    return bool(int(value)) if isinstance(value, (int, float)) else bool(value)
                else:
                    return value
            except (KeyError, TypeError, ValueError) as e:
                print(f"Warning: Could not decode {signal_name}, using default {default_value}. Error: {e}")
                return default_value

        # Update radar signal status with decoded values - MODIFY the global instance
        radar_signal_status.crc = safe_get('FLR2SignalStatusCRC', 0, int)  # type: ignore
        radar_signal_status.counter = safe_get('FLR2SignalStatusCounter', 0, int)  # type: ignore
        radar_signal_status.internal_temp = safe_get('FLR2SignalStatusInternalTemp', -40.0, float)  # type: ignore
        radar_signal_status.timestamp = safe_get('FLR2SignalStatusTimeStamp', 0, int)  # type: ignore
        radar_signal_status.y_axis_offs = safe_get('FLR2SignalStatusYAxisOffs', -25.0, float)  # type: ignore
        radar_signal_status.z_axis_offs = safe_get('FLR2SignalStatusZAxisOffs', -25.0, float)  # type: ignore
        radar_signal_status.x_axis_offs = safe_get('FLR2SignalStatusXAxisOffs', -25.0, float)  # type: ignore
        radar_signal_status.ego_spd_est = safe_get('FLR2SignalStatusEgoSpdEst', 0.0, float)  # type: ignore
        radar_signal_status.ego_yaw_rate_est = safe_get('FLR2SignalStatusEgoYawRateEst', 0.0, float)  # type: ignore
        radar_signal_status.x_orient_ang = safe_get('FLR2SignalStatusXOrientAng', -180.0, float)  # type: ignore
        radar_signal_status.y_orient_ang = safe_get('FLR2SignalStatusYOrientAng', -180.0, float)  # type: ignore
        radar_signal_status.z_orient_ang = safe_get('FLR2SignalStatusZOrientAng', -180.0, float)  # type: ignore
        radar_signal_status.azi_ang_cor = safe_get('FLR2SignalStatusAziAngCor', -12.8, float)  # type: ignore
        radar_signal_status.ele_ang_cor = safe_get('FLR2SignalStatusEleAngCor', -12.8, float)  # type: ignore
        radar_signal_status.cal_prgrss_sts = safe_get('FLR2SignalStatusCalPrgrsSts', 0, int)  # type: ignore
        radar_signal_status.whl_comp_fact = safe_get('FLR2SignalStatusWhlCompFact', 0.92, float)  # type: ignore
        radar_signal_status.if_vers_major = safe_get('FLR2SignalStatusIfVersMajor', 0, int)  # type: ignore
        radar_signal_status.if_vers_minor = safe_get('FLR2SignalStatusIfVersMinor', 0, int)  # type: ignore
        radar_signal_status.sw_vers_major = safe_get('FLR2SignalStatusSwVersMajor', 0, int)  # type: ignore
        radar_signal_status.sw_vers_minor = safe_get('FLR2SignalStatusSwVersMinor', 0, int)  # type: ignore
        radar_signal_status.scan_id_sts = safe_get('FLR2SignalStatusScanIDSts', 0, int)  # type: ignore
        radar_signal_status.timestamp_status = safe_get('FLR2SignalStatusTimeStampStatus', False, bool)  # type: ignore
        radar_signal_status.flt_reason = safe_get('FLR2SignalStatusFltReason', 0, int)  # type: ignore
        radar_signal_status.comm_flt_reason = safe_get('FLR2SignalStatusCommFltReason', 0, int)  # type: ignore
        radar_signal_status.rdr_int_sts = safe_get('FLR2SignalStatusRdrIntSts', 0, int)  # type: ignore
        radar_signal_status.cal_sts = safe_get('FLR2SignalStatusCalSts', 0, int)  # type: ignore
        radar_signal_status.cal_rlt_sts = safe_get('FLR2SignalStatusCalRltSts', 0, int)  # type: ignore
        radar_signal_status.blockage = safe_get('FLR2SignalStatusBlockage', 0, int)  # type: ignore
        radar_signal_status.interference = safe_get('FLR2SignalStatusInterference', 0, int)  # type: ignore
        radar_signal_status.sys_fail_flag = safe_get('FLR2SignalStatusSysFailFlag', False, bool)  # type: ignore
        radar_signal_status.rdr_sts = safe_get('FLR2SignalStatusRdrSts', False, bool)  # type: ignore
        radar_signal_status.rdr_trans_act = safe_get('FLR2SignalStatusRdrTransAct', False, bool)  # type: ignore
        radar_signal_status.signal_status_ub = safe_get('FLR2SignalStatus_UB', False, bool)  # type: ignore
        
        print(f'Updated global radar_signal_status: Temp={radar_signal_status.internal_temp:.1f}°C, Counter={radar_signal_status.counter}')
        
    except Exception as e:
        print(f'Error processing radar signal status: {e}')
    
    return radar_signal_status

def process_ObjectList_CAN0(radar_dbc: database.Database) -> None:  
    if not object_attribute_list:
        return radar_view
    
    reference_id = object_attribute_list[0].arbitration_id
    max_id = object_attribute_list[-1].arbitration_id
                   
    # Quick bounds check before processing object data
    if not (reference_id <= message_radar.arbitration_id <= max_id):
        return radar_view 
    
    # Process matching arbitration ID
    for entry in object_attribute_list:
        if entry.arbitration_id == message_radar.arbitration_id:
            # E2E protection check
            #if not e2e.p05.e2e_p05_check(message_radar.data, message_radar.dlc, data_id=entry.e2e_data_id):
            #    continue
            
            # Decode message once
            decoded_message = radar_dbc.decode_message(message_radar.arbitration_id, message_radar.data)
            
            # Update global message counters
            radar_view.msg_counter = decoded_message.get(entry.msg_counter_signal, 0)
            radar_view.scan_id = decoded_message.get(entry.scan_id_signal, 0)
            
            # Calculate array index
            index_entry = entry.arbitration_id - reference_id
            
            # Update object data efficiently
            update_object_data(decoded_message, entry.msg_obj_prop.first_obj_prop, index_entry)
            update_object_data(decoded_message, entry.msg_obj_prop.second_obj_prop, index_entry + 1)
            
            print(f'Processing arbitration_id: 0x{message_radar.arbitration_id:03X}')
            break
            
def process_CAN0_rx(radar_dbc: database.Database, can_bus_radar) -> RadarView:
    """Optimized radar message processing with improved error handling"""
    global message_radar
    
    try:
        if is_raspberrypi():
            message_radar = can_bus_radar.recv(timeout=0.1)
        
        # Check if message is None (timeout or no message)
        if message_radar is None:
            return radar_view
        

        # Add message to sniffer regardless of processing
        can_sniffer.add_message(
            message_radar.arbitration_id, 
            message_radar.data, 
            getattr(message_radar, 'timestamp', None)
        )

        # Special handling for signal status frame
        if message_radar.arbitration_id == SIGNAL_STATUS_CAN_ID:
            print(f'  → Signal Status Frame (0x45): {len(message_radar.data)} bytes received')
                 
        # Process signal status frame regardless of sniffer state
        if message_radar.arbitration_id == SIGNAL_STATUS_CAN_ID:
            # Print detailed radar data in CLI
            print(f'Radar CAN Message: ID=0x{message_radar.arbitration_id:03X} ({message_radar.arbitration_id}) | '
                f'DLC={message_radar.dlc} | Data={message_radar.data.hex().upper()} | '
                f'Bytes=[{", ".join(f"0x{b:02X}" for b in message_radar.data)}]')
            
            process_RadarStatus_CAN0(radar_dbc, message_radar)
            return radar_view

        # If sniffer is enabled, skip other processing
        if can_sniffer.enabled:
            return radar_view

        # Process object list frames
        process_ObjectList_CAN0(radar_dbc)   
             
    except OSError as e:
        print(f'Radar CAN bus error: {e}')
        # Don't exit, just return current state
    except Exception as e:
        print(f'Unexpected radar processing error: {e}')
        
    return radar_view
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
def process_CAN1_rx(can_bus_car) -> EgoMotion:
    """Optimized vehicle CAN message processing"""
    global message_car
    
    # Use immutable replacement pattern for frozen dataclass
    updated_values = {}
    
    try:
        if is_raspberrypi():
            message_car = can_bus_car.recv(timeout=0.1)
        
        # Check if message is None (timeout or no message)
        if message_car is None:
            return ego_motion_data
        
        # Add message to sniffer
        can_sniffer.add_message(
            message_car.arbitration_id, 
            message_car.data, 
            getattr(message_car, 'timestamp', None)
        )
            
        # If sniffer is enabled, skip processing
        if can_sniffer.enabled:
            return ego_motion_data
            
        # Process vehicle speed
        if message_car.arbitration_id == VEHICLE_SPEED:
            # TODO: Implement proper DBC decoding when available
            updated_values['speed'] = 0  # radar_dbc.decode_message(...)
            
        # Process wheel speeds
        elif message_car.arbitration_id == WHEEL_SPEED:
            # TODO: Implement proper DBC decoding when available
            updated_values.update({
                'left_wheel_speed': 0,   # radar_dbc.decode_message(...)
                'right_wheel_speed': 0   # radar_dbc.decode_message(...)
            })
            print(f'Vehicle CAN ID: 0x{message_car.arbitration_id:03X}, Data: {message_car.data.hex()}')
            
    except OSError as e:
        print(f'Vehicle CAN bus error: {e}')
        # Don't exit, return current state
    except Exception as e:
        print(f'Unexpected vehicle processing error: {e}')
    
    # Return updated ego motion data (immutable replacement)
    if updated_values:
        return EgoMotion(**{**ego_motion_data.__dict__, **updated_values})
    
    return ego_motion_data

def toggle_can_sniffer():
    """Toggle CAN sniffer mode"""
    can_sniffer.enabled = not can_sniffer.enabled
    if can_sniffer.enabled:
        can_sniffer.messages.clear()  # Clear old messages when enabling
    print(f"CAN Sniffer {'enabled' if can_sniffer.enabled else 'disabled'}")

# Legacy compatibility aliases for existing code
#list_of_Object_attr = object_attribute_list

# Export optimized functions with legacy names for compatibility
#process_rx_radar = process_CAN0_rx
#process_rx_car = process_CAN1_rx

# Export radar signal status for external access
__all__ = [
    'radar_view', 'radar_signal_status', 'ego_motion_data', 'can_sniffer',
    'process_CAN0_rx', 'process_CAN1_rx', 'process_RadarStatus_CAN0',
    'toggle_can_sniffer', 'FlrFlr1canFr96', 'ObjectDrawData', 'EgoMotion'
]