import math
import random
import numpy as np
from typing import List
from rx import radar_view, ego_motion_data, ObjectDrawData
from defines import *


def map_value(value: float, from_low: float, from_high: float, to_low: float, to_high: float) -> float:
    """Optimized value mapping with type hints"""
    return to_low + (value - from_low) * (to_high - to_low) / (from_high - from_low)

# Use numpy arrays for better performance
latposition: np.ndarray = np.zeros(30, dtype=np.int16)
longposition: np.ndarray = np.zeros(30, dtype=np.int16)
object_class: np.ndarray = np.zeros(30, dtype=np.uint8)
longvelo_speed: np.ndarray = np.full(30, 30.0, dtype=np.float32)

def init_process_sim_radar() -> None:
    """Initialize radar simulation with optimized data structures"""
    global ego_motion_data
    
    # Create new ego motion data since it's frozen
    ego_motion_data = ego_motion_data.__class__(speed=60.0)

    # Initialize arrays with vectorized operations
    latposition[:] = np.random.randint(50, 1001, size=30)
    longposition[:] = np.random.randint(50, 551, size=30)
    object_class[:] = np.random.randint(0, 4, size=30)
    longvelo_speed[:] = np.random.uniform(0.0, 10.0, size=30)
        
def process_sim_radar(radar_dbc, can_bus_radar, can_bus_car) -> None:
    """Optimized radar simulation with vectorized operations"""
    global latposition, longposition

    # Update message counter (optimized)
    radar_view.msg_counter = 1  # Could be random.randint(1, 100) if needed

    # Vectorized position updates
    longposition += 1
    
    # Handle boundary conditions with numpy operations
    mask_lat_high = latposition > surface_width
    mask_lat_low = latposition < 0
    mask_long_high = longposition > surface_height
    mask_long_low = longposition < 0
    
    latposition[mask_lat_high] = np.random.randint(200, 1001, size=np.sum(mask_lat_high))
    latposition[mask_lat_low] = 0
    longposition[mask_long_high] = np.random.randint(100, 601, size=np.sum(mask_long_high))
    longposition[mask_long_low] = 0

    # Update objects in batch
    for i in range(len(radar_view.object_list_for_draw)):
        radar_view.object_list_for_draw[i] = ObjectDrawData(
            object_id=i,
            class_type=int(object_class[i]),
            data_conf=random.randint(50, 100),
            data_len=30.0,
            data_width=20.0,
            heading_angle=random.uniform(-180.0, 180.0),
            lat_acc=random.uniform(-2.0, 2.0),
            lat_pos=int(latposition[i]),
            lat_velocity=random.uniform(-5.0, 5.0),
            lgt_acc=random.uniform(-2.0, 2.0),
            lgt_pos=int(longposition[i]),
            lgt_velocity=float(longvelo_speed[i]),
            model_info=random.randint(0, 10),
            quality=random.randint(50, 100)
        )

def process_sim_car(main_can_bus_car):
    """Optimized car simulation with immutable data structures"""
    global ego_motion_data
    
    # Create new EgoMotion instance since it's frozen
    new_speed = round(random.uniform(30.0, 32.0), 2)
    new_yaw_rate = random.uniform(-5.0, 5.0)
    
    ego_motion_data = ego_motion_data.__class__(
        speed=new_speed,
        left_wheel_speed=0.0,
        right_wheel_speed=0.0,
        yaw_rate=int(new_yaw_rate),
        lat_acc=ego_motion_data.lat_acc,
        long_acc=ego_motion_data.long_acc
    )
    
    return ego_motion_data

base_speed = 30.0

def process_sim_car_speed() -> None:
    """Optimized speed simulation using vectorized numpy operations"""
    global longvelo_speed
    
    # Create speed variations using vectorized operations
    indices = np.arange(len(radar_view.object_list_for_draw))
    
    # Apply different patterns based on index modulo 5
    speed_variations = np.zeros_like(longvelo_speed)
    
    # Pattern 0: Small random walk
    mask0 = indices % 5 == 0
    speed_variations[mask0] = np.sum(np.random.uniform(-2, 2, (10, np.sum(mask0))), axis=0)
    
    # Pattern 1: Sinusoidal variation
    mask1 = indices % 5 == 1
    speed_variations[mask1] = 10 * np.sin(indices[mask1])
    
    # Pattern 2: Pulse-like jumps
    mask2 = indices % 5 == 2
    speed_variations[mask2] = np.random.choice([-20, -10, 0, 10, 20], size=np.sum(mask2))
    
    # Pattern 3: Gaussian variation
    mask3 = indices % 5 == 3
    speed_variations[mask3] = np.random.normal(0, 5, size=np.sum(mask3))
    
    # Pattern 4: Linear ramp
    mask4 = indices % 5 == 4
    slopes = np.random.choice([-2, 2], size=np.sum(mask4))
    speed_variations[mask4] = slopes * indices[mask4]
    
    # Update speeds with clamping
    longvelo_speed[:] = np.clip(base_speed + speed_variations, 0, 180)
    
    # For testing, set to constant value
    longvelo_speed[:] = 10.0  # Simplified for now