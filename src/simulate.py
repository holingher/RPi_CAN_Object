import random
from rx import ObjList_VIEW, object_list_for_draw_t
from defines import *


def map_value(value, from_low, from_high, to_low, to_high):
    # Scale the value from one range to another
    return to_low + (value - from_low) * (to_high - to_low) / (from_high - from_low)

latposition = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
longposition = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
object_class = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

def init_simulate_object_list():
    for i in range(len(ObjList_VIEW.object_list_for_draw)):
        # Initialize the object list with None
        latposition[i] = random.randint(50, 1000)
        longposition[i] = random.randint(50, 550)
        object_class[i] = random.randint(0, 3)
        
def simulate_object_list(radar_dbc, can_bus_radar, can_bus_car):
    global latposition, longposition

    # Ensure the object list is initialized
    if not hasattr(ObjList_VIEW, "object_list_for_draw") or ObjList_VIEW.object_list_for_draw is None:
        ObjList_VIEW.object_list_for_draw = [None] * 30  # Initialize with 30 empty slots

    # Simulate message counter
    ObjList_VIEW.MsgCntr = 1#random.randint(1, 100)  # Random message counter (1-100)
    
    # Simulate objects in the list
    for i in range(len(ObjList_VIEW.object_list_for_draw)):
        # Generate random or sequential positions
        # Smoothly randomize latposition
        #latposition[i] += 1  # Add a small random offset (-5 to 5)
        longposition[i] += 1  # Add a small random offset (-3 to 3)

        # Reset positions if they exceed screen boundaries
        if latposition[i] > surface_width:
            latposition[i] = random.randint(200, 1000)
        elif latposition[i] < 0:
            latposition[i] = 0

        if longposition[i] > surface_height:
            longposition[i] = random.randint(100, 600)
        elif longposition[i] < 0:
            longposition[i] = 0

        # Update or create a new object entry
        ObjList_VIEW.object_list_for_draw[i] = object_list_for_draw_t(
            object_id=i,
            Class=object_class[i],  # Random class (0: Unknown, 1: Car, 2: Bicycle, 3: Pedestrian)
            DataConf=random.randint(50, 100),  # Random confidence value (50-100 for higher confidence)
            DataLen=30,
            DataWidth=20,
            HeadingAng=random.uniform(-180.0, 180.0),  # Random heading angle (-180 to 180 degrees)
            LatAcc=random.uniform(-2.0, 2.0),  # Random lateral acceleration (-2 to 2 m/s^2)
            LatPos=latposition[i],  # Lateral position
            LatVelo=random.uniform(-5.0, 5.0),  # Random lateral velocity (-5 to 5 m/s)
            LgtAcc=random.uniform(-2.0, 2.0),  # Random longitudinal acceleration (-2 to 2 m/s^2)
            LgtPos=longposition[i],  # Longitudinal position
            LgtVelo=random.uniform(0.0, 10.0),  # Random longitudinal velocity (0 to 10 m/s)
            ModelInfo=random.randint(0, 10),  # Random model info (0-10)
            Qly=random.randint(50, 100)  # Random quality value (50-100 for higher quality)
        )
    return 2