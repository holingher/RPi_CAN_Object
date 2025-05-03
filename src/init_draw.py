import random
from pygame import init as screen_init
from pygame import quit as screen_quit
from pygame import event
from pygame import time
from pygame import sprite
from pygame import display
from pygame import QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN, DOUBLEBUF, SRCALPHA, FULLSCREEN
from pygame.sprite import Group
from defines import *

########################################################################################
def init_draw():
    # Initialize the game
    screen_init()
    # Allowing only Certain events
    event.set_allowed([QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN])
    # Set up the game clock
    clock = time.Clock()
    flags = DOUBLEBUF | SRCALPHA #| FULLSCREEN
    # create the screen
    screen = display.set_mode(screen_size, flags, 16)
    # set the application name
    display.set_caption('RPi_Object_radar')

    # Create sprite groups
    ego_group = sprite.Group()
    vehicle_group = sprite.Group()
    
    # ego vehicle's starting coordinates
    # half of the screen width
    ego_x = round(surface_width / 2 / 10) * 10 
    #bottom of the screen minus the ego's car height
    ego_y = screen.get_height() - ego_vehicle_bottom_offset
    
    # Create the ego vehicle
    ego_vehicle = EgoVehicle(ego_x, ego_y)
    ego_group.add(ego_vehicle)
    init_vehicles(vehicle_group)  # Add vehicles to the vehicle group
    
    # Set the frame rate
    clock.tick(fps)

    return screen, ego_group, vehicle_group, ego_vehicle

########################################################################################
def init_vehicles(vehicle_group: Group):
    # Initialize 30 vehicles in the vehicle_group
    for i in range(30):
        vehicle = Vehicle(
            id_object=i,
            color=random.choice([red, green, yellow, gray]),  # Random color
            x=-200,#random.randint(0, surface_width),  # Random x position
            y=-200,#random.randint(-300, -50),  # Random y position above the screen
            width=1,#random.randint(20, 50),  # Random width
            height=1,#random.randint(20, 50),  # Random height
            speed=0,#random.randint(1, 5),  # Random speed
            dataConfidence=0,#random.randint(0, 100),  # Random confidence
            label=f"Unknown {i}"  # Label for the vehicle
        )
        vehicle_group.add(vehicle)
    '''
    # If no matching vehicle exists, add a new one
    if object_entry and vehicle.id == 30:
        print("Adding vehicle with ID:", object_entry.object_id)
        color = (
            yellow if object_entry.Class == 0 else # Unknown
            red if object_entry.Class == 1 else # Car
            green if object_entry.Class == 2 else # Bicycle
            gray # Pedestrian
        )
        label = (
            'Unknown' if object_entry.Class == 0 else
            'Car' if object_entry.Class == 1 else
            'Bicycle' if object_entry.Class == 2 else
            'Pedestrian'
        )
        vehicle = Vehicle(
            id_object=object_entry.object_id,
            color=color,
            x=int(object_entry.LatPos),
            y=int(object_entry.LgtPos),
            width=object_entry.DataWidth,
            height=object_entry.DataLen,
            speed=object_entry.LgtVelo,
            dataConfidence=object_entry.DataConf,
            label=label
        )
        vehicle_group.add(vehicle)
        '''

def deinit_draw(): 
    screen_quit()   