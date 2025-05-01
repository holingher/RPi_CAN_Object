import pygame
from pygame.locals import *
import random
from rx import ObjList_VIEW, EgoMotion_data, process_rx
from rx import object_list_for_draw_t
from draw_3D import draw_3d_vehicle, draw_3d_road, draw_3d_rays
from draw_2D import draw_vehicle, draw_own, draw_environment, draw_rays, add_or_update_vehicle
from menu import draw_extraInfo, draw_simple_checkbox, toggle_rays, is_rays_enabled
from defines import *
        
def main():
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
                
        # Process the RX data
        scanID = process_rx()
        
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
                if object.object_id is not None:  # Ensure object_id is valid
                    add_or_update_vehicle(object, vehicle_group)

        # Draw the checkbox
        #draw_simple_checkbox(screen, 50, screen.get_height() - 100, 20, is_rays_enabled[0], white, toggle_rays, label="Enable Rays")
        
        # Use the menu state
        if is_rays_enabled[0]:
            draw_rays(screen, ego_vehicle, vehicle_group)
            
        draw_extraInfo(screen, EgoMotion_data, vehicle_group, scanID)
        
        draw_vehicle(screen, vehicle_group)
        
        pygame.display.update()
        
    pygame.quit()

if __name__=="__main__":
    main()