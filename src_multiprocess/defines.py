from dataclasses import dataclass
from enum import Enum
import cantools.database
import pygame
import can
import cantools

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

INVALID_OBJECT_ID = 30  # Invalid object ID for vehicle

dbc = cantools.database.can.database.Database()

os_name = 'Windows'
distro_name = 'Ubuntu'
# create the window
surface_width = 1024
surface_height = 600

# define screen size
screen_size = (surface_width, surface_height)

# road and marker sizes
road_width = 510
ego_vehicle_bottom_offset = 30

# number of frames per second
fps = 120

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