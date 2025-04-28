import pygame
from pygame.locals import *
import random
from rx import ObjList_VIEW, EgoMotion_data, process_rx
from rx import object_list_for_draw_t
from draw_3D import draw_3d_vehicle, draw_3d_road, draw_3d_rays
from draw_2D import draw_vehicle, draw_own, draw_environment, draw_rays
from menu import draw_extraInfo, draw_simple_checkbox, toggle_rays, is_rays_enabled
from defines import *

random_data = True

pygame.init()

screen_size = (surface_width, surface_height)
screen = pygame.display.set_mode(screen_size, pygame.SRCALPHA)
pygame.display.set_caption('RPi_Object_radar')

# road and marker sizes
road_width = 510
marker_height = 50

# road and edge markers
road = (road_width, 0, road_width, screen.get_height())

# for animating movement of the lane markers
lane_marker_move_y = 0

# player's starting coordinates
player_x = round(surface_width / 2 / 10) * 10
player_y = screen.get_height() - marker_height

# frame settings
clock = pygame.time.Clock()
     
# sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

# create the player's car
player = PlayerVehicle(player_x, player_y)
player_group.add(player)
     
def add_vehicle(object_entry: object_list_for_draw_t):
    speed = 2
    dataConfidence = 0
    color = (0, 255, 0)  # green color for the vehicles
    # add a vehicle
    if len(vehicle_group) < 30:
        #print('obj count', ObjList_VIEW.object_list_for_draw.count())
        # ensure there's enough gap between vehicles
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height:
                add_vehicle = False

        if add_vehicle:
            if random_data == True:
                # select a random horizontal position within the road boundaries
                x_position = random.randint(int(road_width/3), int(road_width + road_width - 10))  # Ensure the vehicle stays within the road
                # select a random vertical position above the screen
                y_position = random.randint(-300, -50)
                # select a random vehicle color
                color = [random.randint(0, 255) for _ in range(3)]
                
                # select a random label from the VehicleType enum
                label = random.choice(list(VehicleType)).value
                dataConfidence = random.randint(0, 100)
            else:
                color = [random.randint(0, 255) for _ in range(3)]
                # use the real x position from the data
                x_position = object_entry.LatPos
                # use the real y position from the data
                y_position = object_entry.LgtPos
                # use the label classification from the data
                # get the label of the object
                if object_entry.Class == 0:
                    label = 'Unknown'
                elif object_entry.Class == 1: 
                    label = 'Car'
                elif object_entry.Class == 2:
                    label = 'Bicycle'
                elif object_entry.Class == 3: 
                    label = 'Pedestrian'
                speed = object_entry.LgtVelo
                dataConfidence = object_entry.DataConf
                
            vehicle = Vehicle(color, x_position, y_position, label)
            vehicle_group.add(vehicle)
            
    draw_vehicle(screen, vehicle_group, speed, dataConfidence)

# game loop
running = True
while running:
    
    clock.tick(fps)
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            running = False
    scanID = process_rx()
    '''
    # move the player's car using the left/right arrow keys
    if event.type == KEYDOWN:
        
        if event.key == K_LEFT and player.rect.center[0] > left_lane:
            player.rect.x -= 100
        elif event.key == K_RIGHT and player.rect.center[0] < right_lane:
            player.rect.x += 100
            
        # check if there's a side swipe collision after changing lanes
        for vehicle in vehicle_group:
            if pygame.sprite.collide_rect(player, vehicle):
                
                gameover = True
                
                # place the player's car next to other vehicle
                # and determine where to position the crash image
                if event.key == K_LEFT:
                    player.rect.left = vehicle.rect.right
                    crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                elif event.key == K_RIGHT:
                    player.rect.right = vehicle.rect.left
                    crash_rect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
    '''
    draw_environment(screen)
    
    #draw_3d_road(screen, road_width)
    #draw_3d_rays(screen, player)
    # Draw vehicles with 3D scaling
    #for vehicle in vehicle_group:
    #    draw_3d_vehicle(screen, vehicle)
    #    draw_shadow(screen, vehicle)  # Draw shadow for each vehicle
        
    draw_own(screen, player, player_group)
    if random_data == True:
        # add a vehicle for random data
        add_vehicle(None)
    else:
        if ObjList_VIEW.MsgCntr > 0:
            for object in ObjList_VIEW.object_list_for_draw:
                # add a vehicle
                add_vehicle(object)

    # Draw the checkbox
    #draw_simple_checkbox(screen, 50, screen.get_height() - 100, 20, is_rays_enabled[0], white, toggle_rays, label="Enable Rays")
    # Use the menu state
    if is_rays_enabled[0]:
        draw_rays(screen, player, vehicle_group)
        
    draw_extraInfo(screen, EgoMotion_data, vehicle_group, scanID)
    
    # check if there's a head on collision
    if pygame.sprite.spritecollide(player, vehicle_group, True):
        gameover = True
        crash_rect.center = [player.rect.center[0], player.rect.top]
    '''
    # display game over
    if gameover:
        screen.blit(screen, crash_rect)
        
        pygame.draw.rect(screen, red, (0, 50, width, 100))
        
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Game over. Play again? (Enter Y or N)', True, white)
        text_rect = text.get_rect()
        text_rect.center = (width / 2, 100)
        screen.blit(text, text_rect)
    '''  
    pygame.display.update()
    '''
    # wait for user's input to play again or exit
    while gameover:
        
        clock.tick(fps)
        
        for event in pygame.event.get():
            
            if event.type == QUIT:
                gameover = False
                running = False
                
            # get the user's input (y or n)
            if event.type == KEYDOWN:
                if event.key == K_y:
                    # reset the game
                    gameover = False
                    speed = 2
                    objects = 0
                    vehicle_group.empty()
                    player.rect.center = [player_x, player_y]
                elif event.key == K_n:
                    # exit the loops
                    gameover = False
                    running = False
    '''
pygame.quit()