from enum import Enum

import pygame

# create the window
surface_width = 1024
surface_height = 600

fps = 120

# game settings
gameover = False
objects = 0
running = True

# colors
gray = (100, 100, 100)
yellow = (255, 232, 0)
red = (200, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
black = (0, 0, 0)

# Define an enum for vehicle types
class VehicleType(Enum):
    Unknown = "Unknown"
    CAR = "Car"
    BICYCLE = "Bicycle"
    PEDESTRIAN = "Pedestrian"
    
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, id, color, x, y, width, label=''):
        pygame.sprite.Sprite.__init__(self)
        
        self.id = id
        # define the size of the rectangle
        self.width = width
        self.height = 20
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(color)
        
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        
        # set the label for the vehicle
        self.label = label
        
class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        color = (0, 0, 255)  # blue color for the player's car
        super().__init__(color, 255, x, y, 20, label="Own")

# load the crash image
crash_color = (255, 0, 0)  # red for crash indication
crash_rect = pygame.Rect(0, 0, 40, 40)  # Placeholder rectangle for crash

# Define ray tracing parameters
ray_count = 100  # Number of rays in the field of view
ray_length = 600  # Length of each ray
ray_color_hit = (0, 255, 0, 64)  # Green color for the rays that hit a vehicle
ray_color_no_hit = (255, 0, 0, 64)  # Red color for the rays
fov_angle = 90  # Field of view angle in degrees