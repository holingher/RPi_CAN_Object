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