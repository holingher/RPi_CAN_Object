#!/usr/bin/env python3
"""
CAN Interrupt Status Monitor
Simple utility to monitor CAN message reception in interrupt mode
"""

import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from defines import is_raspberrypi
from init_com import init_com, deinit_com
from rx import can0_messages, can1_messages, message_lock

def monitor_can_interrupts():
    """Monitor CAN interrupt queues in real-time"""
    print("=== CAN Interrupt Monitor ===")
    print("Press Ctrl+C to stop\n")
    
    if not is_raspberrypi():
        print("WARNING: Not running on Raspberry Pi - GPIO interrupts disabled")
        print("Messages will only be received through simulation mode\n")
    
    try:
        # Initialize CAN
        can_bus_radar, can_bus_car, radar_dbc = init_com()
        
        print("Monitoring CAN message queues...")
        print("Time     | Radar Queue | Car Queue | Status")
        print("-" * 50)
        
        last_radar_count = 0
        last_car_count = 0
        
        while True:
            current_time = time.strftime("%H:%M:%S")
            
            with message_lock:
                radar_queue_size = len(can0_messages)
                car_queue_size = len(can1_messages)
            
            # Show activity indicators
            radar_activity = "📡" if radar_queue_size > last_radar_count else "  "
            car_activity = "🚗" if car_queue_size > last_car_count else "  "
            
            status = "Active" if (radar_queue_size > 0 or car_queue_size > 0) else "Idle"
            
            print(f"{current_time} | {radar_queue_size:^11} | {car_queue_size:^9} | {status} {radar_activity}{car_activity}")
            
            last_radar_count = radar_queue_size
            last_car_count = car_queue_size
            
            time.sleep(1.0)  # Update every second
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"Monitor error: {e}")
    finally:
        try:
            deinit_com()
        except:
            pass

if __name__ == "__main__":
    monitor_can_interrupts()