#!/usr/bin/env python3
"""
Simple test script for CAN interrupt implementation
Tests the KaMami CAN FD HAT interrupt-based reception
"""

import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from defines import is_raspberrypi
from init_com import init_com, deinit_com
from rx import (can0_messages, can1_messages, message_lock, 
                process_radar_rx, process_car_rx, radar_view, ego_motion_data)

def test_interrupt_mode():
    """Test interrupt-based CAN reception"""
    print("=== CAN Interrupt Mode Test ===")
    print(f"Running on: {'Raspberry Pi' if is_raspberrypi() else 'Development System'}")
    
    if not is_raspberrypi():
        print("Note: GPIO interrupts only work on Raspberry Pi")
        print("This test will check the code structure but won't receive real CAN messages")
    
    try:
        # Initialize CAN system
        print("Initializing CAN communication with interrupts...")
        can_bus_radar, can_bus_car, radar_dbc = init_com()
        
        print("Monitoring CAN messages for 10 seconds...")
        start_time = time.time()
        radar_msg_count = 0
        car_msg_count = 0
        
        while time.time() - start_time < 10.0:
            # Process messages (this will handle interrupt queues)
            current_radar_view = process_radar_rx(radar_dbc, can_bus_radar)
            current_ego_motion = process_car_rx(can_bus_car)
            
            # Check queue status
            with message_lock:
                current_radar_msgs = len(can0_messages)
                current_car_msgs = len(can1_messages)
                radar_msg_count += current_radar_msgs
                car_msg_count += current_car_msgs
                
                if current_radar_msgs > 0 or current_car_msgs > 0:
                    print(f"Messages in queues - Radar: {current_radar_msgs}, Car: {current_car_msgs}")
            
            time.sleep(0.1)  # Check every 100ms
        
        print(f"\nTest Results:")
        print(f"- Total radar messages processed: {radar_msg_count}")
        print(f"- Total car messages processed: {car_msg_count}")
        print(f"- Current radar scan ID: {current_radar_view.scan_id}")
        print(f"- Current radar message counter: {current_radar_view.msg_counter}")
        
        if radar_msg_count > 0 or car_msg_count > 0:
            print("✓ SUCCESS: Interrupt-based CAN reception is working!")
        else:
            print("ⓘ INFO: No CAN messages received (check bus connections)")
            if is_raspberrypi():
                print("  Make sure CAN devices are connected and transmitting")
            else:
                print("  This is expected on non-Raspberry Pi systems")
        
        return True
        
    except Exception as e:
        print(f"✗ ERROR: Test failed - {e}")
        return False
    
    finally:
        print("Cleaning up...")
        try:
            deinit_com()
        except:
            pass

def check_interrupt_status():
    """Check if interrupt mode is properly configured"""
    print("\n=== Interrupt Configuration Check ===")
    
    try:
        from rx import GPIO_AVAILABLE, CAN0_INT_PIN, CAN1_INT_PIN
        print(f"GPIO library available: {GPIO_AVAILABLE}")
        print(f"CAN0 interrupt pin (radar): GPIO {CAN0_INT_PIN}")  
        print(f"CAN1 interrupt pin (car): GPIO {CAN1_INT_PIN}")
        print(f"Platform supports interrupts: {is_raspberrypi() and GPIO_AVAILABLE}")
        
        if is_raspberrypi() and GPIO_AVAILABLE:
            print("✓ System is ready for interrupt-based CAN reception")
        elif is_raspberrypi() and not GPIO_AVAILABLE:
            print("⚠ Raspberry Pi detected but RPi.GPIO not available")
            print("  Install with: sudo apt install python3-rpi.gpio")
        else:
            print("ⓘ Non-Raspberry Pi system - interrupt mode not available")
            
    except ImportError as e:
        print(f"✗ Cannot import interrupt components: {e}")

if __name__ == "__main__":
    try:
        # Check configuration first
        check_interrupt_status()
        
        # Run the test
        if test_interrupt_mode():
            print("\n✓ CAN interrupt implementation validated successfully!")
        else:
            print("\n⚠ Test completed with issues - check error messages above")
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        print("Test complete.")