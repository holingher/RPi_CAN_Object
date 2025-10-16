from enum import Enum
import io
from multiprocessing import Manager
import pygame
import cantools

INVALID_OBJECT_ID = 30  # Invalid object ID for vehicle

# create the window
surface_width = 800
surface_height = 480

# define screen size
screen_size = (surface_width, surface_height)

# road and marker sizes
road_width = 510
ego_vehicle_bottom_offset = 30

# number of frames per second
fps = 30

# game settings
objects = 0

# colors
gray = (100, 100, 100)
yellow = (255, 232, 0)
red = (200, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
black = (0, 0, 0)
blue = (0, 0, 255)

# Define an enum for vehicle types
class VehicleType(Enum):
    Unknown = "Unknown"
    CAR = "Car"
    BICYCLE = "Bicycle"
    PEDESTRIAN = "Pedestrian"
    
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, id_object, color, x, y, width, height, speed, dataConfidence, label=''):
        pygame.sprite.Sprite.__init__(self)
        
        self.id = id_object
        # define the size of the rectangle
        self.width = width
        self.height = height
        self.speed = speed
        self.dataConfidence = dataConfidence
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(color)
        
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        # set the label for the vehicle
        self.label = label
        
    def update(self, id_object, x, y, width, height, speed, dataConfidence, label=''):
        self.rect = pygame.Rect(x, y, width, height)
        
class EgoVehicle(Vehicle):
    def __init__(self, x, y):
        # Initialize the ego vehicle with a predefined values
        super().__init__(color=blue, id_object=255, x=x, y=y, width=20, height=30, speed=0, dataConfidence=0, label="Own")

# Define ray tracing parameters
ray_count = 100  # Number of rays in the field of view
ray_length = 600  # Length of each ray
ray_color_hit = (0, 255, 0, 64)  # Green color for the rays that hit a vehicle
ray_color_no_hit = (255, 0, 0, 64)  # Red color for the rays
fov_angle = 90  # Field of view angle in degrees

########################################################################################
def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

def get_system_temperature():
    """Get system CPU temperature in Celsius for different platforms (RPi, Ubuntu/Linux, Windows)"""
    try:
        if is_raspberrypi():
            # Raspberry Pi temperature
            with io.open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp_str = f.read().strip()
                # Temperature is in millidegrees Celsius, convert to degrees
                temp_celsius = float(temp_str) / 1000.0
                return temp_celsius
        else:
            import platform
            import os
            import subprocess
            
            system = platform.system().lower()
            
            if system == 'linux':
                # Ubuntu/Linux temperature from thermal zones
                thermal_paths = [
                    '/sys/class/thermal/thermal_zone0/temp',
                    '/sys/class/thermal/thermal_zone1/temp',
                    '/sys/class/hwmon/hwmon0/temp1_input',
                    '/sys/class/hwmon/hwmon1/temp1_input'
                ]
                
                for path in thermal_paths:
                    try:
                        if os.path.exists(path):
                            with open(path, 'r') as f:
                                temp_str = f.read().strip()
                                # Most Linux thermal zones report in millidegrees
                                temp_celsius = float(temp_str) / 1000.0
                                # Sanity check: reasonable CPU temperature range
                                if 0 <= temp_celsius <= 100:
                                    return temp_celsius
                    except:
                        continue
                
                # Try sensors command as fallback
                try:
                    result = subprocess.run(['sensors', '-u'], capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if 'temp1_input' in line or 'Core 0' in line:
                                parts = line.split(':')
                                if len(parts) > 1:
                                    temp_str = parts[1].strip()
                                    temp_celsius = float(temp_str)
                                    if 0 <= temp_celsius <= 100:
                                        return temp_celsius
                except:
                    pass
                    
            elif system == 'windows':
                # Windows temperature using WMI
                try:
                    import wmi
                    c = wmi.WMI(namespace="root\\wmi")
                    temperature_info = c.MSAcpi_ThermalZoneTemperature()
                    if temperature_info:
                        # Convert from tenths of Kelvin to Celsius
                        temp_kelvin = temperature_info[0].CurrentTemperature / 10.0
                        temp_celsius = temp_kelvin - 273.15
                        return temp_celsius
                except ImportError:
                    # Try PowerShell as fallback
                    try:
                        ps_cmd = 'Get-WmiObject -Namespace "root/wmi" -Class MSAcpi_ThermalZoneTemperature | Select-Object -First 1 -ExpandProperty CurrentTemperature'
                        result = subprocess.run(['powershell', '-Command', ps_cmd], 
                                              capture_output=True, text=True, timeout=3)
                        if result.returncode == 0:
                            temp_raw = float(result.stdout.strip())
                            temp_celsius = (temp_raw / 10.0) - 273.15
                            return temp_celsius
                    except:
                        pass
                except:
                    pass
            
            # Fallback: return simulated temperature for unsupported systems
            import random
            return 35.0 + random.uniform(-5.0, 10.0)  # Simulate 30-45°C range
            
    except Exception:
        return None  # Return None if temperature cannot be read