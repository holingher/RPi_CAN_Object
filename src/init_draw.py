import os
import random
import distro
from pygame import quit as screen_quit
from pygame import time
from pygame import sprite
from pygame import display
from pygame import QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN, DOUBLEBUF, SRCALPHA, FULLSCREEN
from pygame.sprite import Group
from defines import *
from rx import ObjectDrawData

########################################################################################
def init_draw():
    distro_name = distro.name()
    print('Distro_init: ', distro_name)
    if(distro_name == 'Raspbian GNU/Linux'):
        # Allow running from ssh
        os.putenv("DISPLAY", ":0")

        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print("I'm running under X display = {0}".format(disp_no))
        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['x11', 'fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                # Initialize the mixer
                pygame.mixer.pre_init(buffer=4096)
                pygame.display.init()
                # Allowing only Certain events
                pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN])
            except pygame.error:
                print("Driver: {0} failed.".format(driver))
                continue
            found = True
            break

        if not found:
            raise Exception('No suitable video driver found!')
    pygame.font.init()
    # Set up the clock
    clock = time.Clock()
    
    if(distro_name == 'Raspbian GNU/Linux'):
        flags = DOUBLEBUF | SRCALPHA | FULLSCREEN
    else:
        flags = DOUBLEBUF | SRCALPHA | FULLSCREEN
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
            yellow if object_entry.class_type == 0 else # Unknown
            red if object_entry.class_type == 1 else # Car
            green if object_entry.class_type == 2 else # Bicycle
            gray # Pedestrian
        )
        label = (
            'Unknown' if object_entry.class_type == 0 else
            'Car' if object_entry.class_type == 1 else
            'Bicycle' if object_entry.class_type == 2 else
            'Pedestrian'
        )
        vehicle = Vehicle(
            id_object=object_entry.object_id,
            color=color,
            x=int(object_entry.lat_pos),
            y=int(object_entry.lgt_pos),
            width=object_entry.data_width,
            height=object_entry.data_len,
            speed=object_entry.lgt_velocity,
            dataConfidence=object_entry.data_conf,
            label=label
        )
        vehicle_group.add(vehicle)
        '''

def deinit_draw(): 
    screen_quit()   