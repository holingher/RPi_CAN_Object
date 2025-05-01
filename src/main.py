import pygame
from pygame.locals import *
import random
from init_com import init_com, deinit_com
from rx import ObjList_VIEW, EgoMotion_data, process_rx
from rx import object_list_for_draw_t
from tx import process_tx
from draw_3D import draw_3d_vehicle, draw_3d_road, draw_3d_rays
from draw_2D import draw_own, draw_environment, draw_rays, init_vehicles, update_vehicle
from menu import draw_extraInfo, draw_simple_checkbox, toggle_rays, is_rays_enabled
from defines import *
import distro
import os
import platform

os_name = 'Windows'
distro_name = distro.name()
os_name = platform.system()

def map_value(value, from_low, from_high, to_low, to_high):
    # Scale the value from one range to another
    return to_low + (value - from_low) * (to_high - to_low) / (from_high - from_low)
latposition = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
longposition = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
object_class = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
def simulate_object_list():
    global latposition, longposition

    # Ensure the object list is initialized
    if not hasattr(ObjList_VIEW, "object_list_for_draw") or ObjList_VIEW.object_list_for_draw is None:
        ObjList_VIEW.object_list_for_draw = [None] * 30  # Initialize with 30 empty slots

    # Simulate message counter
    ObjList_VIEW.MsgCntr = random.randint(1, 100)  # Random message counter (1-100)
    
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
              
def main():
    try:
        global latposition, longposition, object_class
        # Initialize the game
        pygame.init()
        # Set up the game clock
        clock = pygame.time.Clock()
        # create the screen
        screen = pygame.display.set_mode(screen_size, pygame.SRCALPHA)
        # set the application name
        pygame.display.set_caption('RPi_Object_radar')
        
        # road and edge markers
        #road = (road_width, 0, road_width, screen.get_height())
        
        # Create sprite groups
        ego_group = pygame.sprite.Group()
        vehicle_group = pygame.sprite.Group()
        
        # ego vehicle's starting coordinates
        # half of the screen width
        ego_x = round(surface_width / 2 / 10) * 10 
        #bottom of the screen minus the ego's car height
        ego_y = screen.get_height() - ego_vehicle_bottom_offset
        
        # Create the ego vehicle
        ego_vehicle = EgoVehicle(ego_x, ego_y)
        ego_group.add(ego_vehicle)
        init_vehicles(vehicle_group)  # Add vehicles to the vehicle group
                
        for i in range(len(ObjList_VIEW.object_list_for_draw)):
            # Initialize the object list with None
            latposition[i] = random.randint(50, 1000)
            longposition[i] = random.randint(50, 550)
                    # Smoothly randomize the Class using weighted probabilities
            object_class[i] = random.randint(0, 3)
            
        can_bus_radar, can_bus_car, dbc = init_com()  # Initialize the CAN communication
        
        # loop
        running = True
        while running:
            
            # Set the frame rate
            clock.tick(fps)
            # Get the list of events
            events = pygame.event.get()
            # Check for quit events
            for event in events:
                # Check for quit event
                if event.type == QUIT:
                    # Exit the program
                    running = False
            scanID = 0        
            simulate_object_list()  
             
            # Process the Tx data
            process_tx(can_bus_radar, can_bus_car) 
                
            # Process the RX data
            #scanID = process_rx()
            
            # Fill the screen with a color
            draw_environment(screen)
            
            #draw_3d_road(screen, road_width)
            #draw_3d_rays(screen, ego_vehicle)
            # Draw vehicles with 3D scaling
            #for vehicle in vehicle_group:
            #    draw_3d_vehicle(screen, vehicle)
            #    draw_shadow(screen, vehicle)  # Draw shadow for each vehicle
            
            # Draw own vehicle
            draw_own(screen, ego_vehicle, ego_group)

            if ObjList_VIEW.MsgCntr > 0:
                for object in ObjList_VIEW.object_list_for_draw:
                    if object.object_id != INVALID_OBJECT_ID:  # Ensure object_id is valid
                        update_vehicle(screen, object, vehicle_group)

            # Draw the checkbox
            #draw_simple_checkbox(screen, 50, screen.get_height() - 100, 20, is_rays_enabled[0], white, toggle_rays, label="Enable Rays")
            
            # Use the menu state
            if is_rays_enabled[0]:
                draw_rays(screen, ego_vehicle, vehicle_group)
            
            draw_extraInfo(screen, EgoMotion_data, vehicle_group, scanID)
             
            pygame.display.update()
            
        pygame.quit()
    except KeyboardInterrupt:
        deinit_com()
        pygame.quit()
        
if __name__=="__main__":
    main()
    
