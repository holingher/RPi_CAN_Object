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

def update_object_data(decoded_message: database.Message, obj_prop: ObjectProperty, index: int) -> None:
    """Helper function to update object data efficiently"""
    radar_view.object_list_for_draw[index] = ObjectDrawData(
        object_id=obj_prop.object_id,
        class_type=decoded_message.get_signal_by_name(obj_prop.class_signal),
        data_conf=decoded_message.get_signal_by_name(obj_prop.data_conf_signal),
        data_len=decoded_message.get_signal_by_name(obj_prop.data_len_signal),
        data_width=decoded_message.get_signal_by_name(obj_prop.data_width_signal),
        heading_angle=decoded_message.get_signal_by_name(obj_prop.heading_angle_signal),
        lat_acc=decoded_message.get_signal_by_name(obj_prop.lat_acc_signal),
        lat_pos=decoded_message.get_signal_by_name(obj_prop.lat_pos_signal),
        lat_velocity=decoded_message.get_signal_by_name(obj_prop.lat_velocity_signal),
        lgt_acc=decoded_message.get_signal_by_name(obj_prop.lgt_acc_signal),
        lgt_pos=decoded_message.get_signal_by_name(obj_prop.lgt_pos_signal),
        lgt_velocity=decoded_message.get_signal_by_name(obj_prop.lgt_velocity_signal),
        model_info=decoded_message.get_signal_by_name(obj_prop.model_info_signal),
        quality=decoded_message.get_signal_by_name(obj_prop.quality_signal)
    )

def process_radar_rx(radar_dbc: database.Database, can_bus_radar) -> RadarView:
    """Optimized radar message processing with improved error handling"""
    global message_radar
    
    if not object_attribute_list:
        return radar_view
    
    reference_id = object_attribute_list[0].arbitration_id
    max_id = object_attribute_list[-1].arbitration_id

    try:
        if is_raspberrypi():
            message_radar = can_bus_radar.recv(timeout=0.1)
            
        # Quick bounds check before processing
        if not (reference_id <= message_radar.arbitration_id <= max_id):
            return radar_view
            
        # Process matching arbitration ID
        for entry in object_attribute_list:
            if entry.arbitration_id == message_radar.arbitration_id:
                # E2E protection check
                if not e2e.p05.e2e_p05_check(message_radar.data, message_radar.dlc, data_id=entry.e2e_data_id):
                    continue
                
                # Decode message once
                decoded_message = radar_dbc.get_message_by_frame_id(message_radar.arbitration_id)
                
                # Update global message counters
                radar_view.msg_counter = decoded_message.get_signal_by_name(entry.msg_counter_signal)
                radar_view.scan_id = decoded_message.get_signal_by_name(entry.scan_id_signal)
                
                # Calculate array index
                index_entry = entry.arbitration_id - reference_id
                
                # Update object data efficiently
                update_object_data(decoded_message, entry.msg_obj_prop.first_obj_prop, index_entry)
                update_object_data(decoded_message, entry.msg_obj_prop.second_obj_prop, index_entry + 1)
                
                print(f'Processing arbitration_id: 0x{message_radar.arbitration_id:03X}')
                break
                
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
def process_car_rx(can_bus_car) -> EgoMotion:
    """Optimized vehicle CAN message processing"""
    global message_car
    
    # Use immutable replacement pattern for frozen dataclass
    updated_values = {}
    
    try:
        if is_raspberrypi():
            message_car = can_bus_car.recv(timeout=0.1)
            
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

# Legacy compatibility aliases for existing code
list_of_Object_attr = object_attribute_list
#ObjList_VIEW = radar_view
#EgoMotion_data = ego_motion_data

# Export optimized functions with legacy names for compatibility
process_rx_radar = process_radar_rx
process_rx_car = process_car_rx