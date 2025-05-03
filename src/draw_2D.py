import pygame
import math
from pygame import Surface
from pygame import display as pygame_display
from pygame import event as pygame_event
from pygame import QUIT
from pygame.sprite import Group
from rx import ObjList_VIEW, object_list_for_draw_t
from defines import *

########################################################################################
def draw_update():
    pygame_display.update()

######################################################################################## 
def draw_get_events(): 
    # Get the list of events
    return pygame_event.get()


########################################################################################
def draw_environment(screen: Surface):
    # draw the background
    screen.fill(black)
    # draw the road
    #pygame.draw.rect(screen, black, road)
    
    # draw the edge markers
    #pygame.draw.rect(screen, yellow, left_edge_marker)
    #pygame.draw.rect(screen, yellow, right_edge_marker)

    # draw the lane markers
    #lane_marker_move_y += speed * 2
    #if lane_marker_move_y >= marker_height * 2:
    #    lane_marker_move_y = 0
    #for y in range(marker_height * -2, height, marker_height * 2):
    #    pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
    #    pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))


########################################################################################
# Function to calculate rays based on FOV
def calculate_rays(screen: Surface, ego_vehicle: EgoVehicle):
    rays = []
    start_angle = -fov_angle*1.5  # Start angle relative to the ego vehicle's forward direction
    angle_step = fov_angle / (ray_count - 1)  # Angle between each ray

    for i in range(ray_count):
        angle = math.radians(start_angle + i * angle_step)
        # Calculate the maximum ray length based on the screen edges
        if math.cos(angle) > 0:  # Ray pointing right
            max_x = screen.get_width() - ego_vehicle.rect.centerx
        else:  # Ray pointing left
            max_x = -ego_vehicle.rect.centerx

        if math.sin(angle) > 0:  # Ray pointing down
            max_y = screen.get_height() - ego_vehicle.rect.centery
        else:  # Ray pointing up
            max_y = -ego_vehicle.rect.centery

        # Calculate the ray length to the edge of the screen
        ray_length_x = max_x / math.cos(angle) if math.cos(angle) != 0 else float('inf')
        ray_length_y = max_y / math.sin(angle) if math.sin(angle) != 0 else float('inf')
        ray_length = min(ray_length_x, ray_length_y)

        # Calculate the end point of the ray
        end_x = ego_vehicle.rect.centerx + ray_length * math.cos(angle)
        end_y = ego_vehicle.rect.centery + ray_length * math.sin(angle)
        rays.append(((ego_vehicle.rect.centerx, ego_vehicle.rect.centery), (end_x, end_y)))

    return rays

########################################################################################
def draw_rays(screen: Surface, ego_vehicle: EgoVehicle, vehicle_group: Group):
    # Create a transparent surface for drawing rays
    ray_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)  # Use SRCALPHA for transparency
    
    # Calculate and draw rays for the ego vehicle's field of view
    rays = calculate_rays(screen, ego_vehicle)
    # Check for collisions along each ray
    for ray_start, ray_end in rays:
        hit_point = None  # Initialize the hit point as None
        for vehicle in vehicle_group:
            if vehicle.rect.clipline(ray_start, ray_end):  # Check if the ray intersects a vehicle
                # Get the intersection point
                hit_point = vehicle.rect.clipline(ray_start, ray_end)
                break

        # Draw the ray
        if hit_point:
            # Draw the ray only up to the collision point
            pygame.draw.line(ray_surface, ray_color_hit, ray_start, hit_point[0], 2)  # Green ray for collision
        else:
            # Draw the full ray if no collision
            pygame.draw.line(ray_surface, ray_color_no_hit, ray_start, ray_end, 2)
    # Blit the transparent surface onto the main screen
    screen.blit(ray_surface, (0, 0)) 

########################################################################################
def draw_own(screen: Surface, ego_vehicle: EgoVehicle, ego_group: Group):
    # draw the ego's car
    ego_group.draw(screen)
    # draw the ego vehicle rectangle
    screen.blit(ego_vehicle.image, ego_vehicle.rect)
    # render the label above the rectangle
    font = pygame.font.Font(pygame.font.get_default_font(), 14)
    text = font.render(ego_vehicle.label, True, white)  # white text
    text_rect = text.get_rect(center=(ego_vehicle.rect.centerx, ego_vehicle.rect.top - 10))  # Position above the rectangle
    screen.blit(text, text_rect)

########################################################################################
def draw_vehicle(screen: Surface, vehicle: Vehicle):
    vehicle: Vehicle

    # draw the vehicle rectangle
    screen.blit(source=vehicle.image, dest=vehicle.rect)
    
    # render the label above the rectangle
    font = pygame.font.Font(pygame.font.get_default_font(), 14)
    text = font.render(vehicle.label + " " + str(vehicle.dataConfidence), True, white)  # white text
    text_rect = text.get_rect(center=(vehicle.rect.centerx, vehicle.rect.top - 10))  # Position above the rectangle
    screen.blit(text, text_rect)

    # make the vehicles move
    vehicle.rect.y += vehicle.speed
    
    # remove vehicle once it goes off screen
    if vehicle.rect.top >= screen.get_height():
        vehicle.kill()

########################################################################################
 
def update_vehicle(screen: Surface, vehicle_group: Group):
    object_entry: object_list_for_draw_t
    vehicle: Vehicle
    
    if ObjList_VIEW.MsgCntr > 0:
            for object_entry in ObjList_VIEW.object_list_for_draw:
                if object_entry.object_id != INVALID_OBJECT_ID:  # Ensure object_id is valid
                    for vehicle in vehicle_group:
                        # Check if the vehicle already exists in the group using object_id
                        if vehicle.id == object_entry.object_id:
                            #print("Before: ", vehicle.id, vehicle.rect.x, vehicle.rect.y, vehicle.width, vehicle.height, vehicle.speed, vehicle.dataConfidence)
                            vehicle.kill()  # Remove the vehicle from the group
                            vehicle = Vehicle(
                                id_object=object_entry.object_id,
                                color=(
                                    yellow if object_entry.Class == 0 else  # Unknown
                                    red if object_entry.Class == 1 else  # Car
                                    green if object_entry.Class == 2 else  # Bicycle
                                    gray  # Pedestrian
                                ),
                                x=int(object_entry.LatPos),  # Update lateral position
                                y=int(object_entry.LgtPos),  # Update longitudinal position
                                width=int(object_entry.DataWidth),  # Update width
                                height=int(object_entry.DataLen),  # Update height
                                speed=object_entry.LgtVelo,  # Update speed
                                dataConfidence=object_entry.DataConf,  # Update confidence
                                label = (
                                    'Unknown' if object_entry.Class == 0 else
                                    'Car' if object_entry.Class == 1 else
                                    'Bicycle' if object_entry.Class == 2 else
                                    'Pedestrian'
                                )
                            )
                            #print("After: ", vehicle.id, vehicle.rect.x, vehicle.rect.y, vehicle.width, vehicle.height, vehicle.speed, vehicle.dataConfidence, object_entry.Class)
                            vehicle.update(vehicle.id, vehicle.rect.x, vehicle.rect.y, vehicle.width, vehicle.height, vehicle.speed, vehicle.dataConfidence)  # Update the vehicle's position
                            vehicle_group.add(vehicle)  # Add the updated vehicle back to the group
                            draw_vehicle(screen, vehicle)  # Draw the updated vehicle
                            #return  # Exit after updating the vehicle
    # draw the vehicles
    vehicle_group.draw(screen) 
 
def update_vehicle_ai(screen: Surface, vehicle_group: Group):
    vehicle: Vehicle
    """
    Updates the vehicles in the vehicle group based on the object list for drawing.
    """
    if ObjList_VIEW.MsgCntr > 0:
        # Create a mapping of object IDs to vehicles for quick lookup
        vehicle_map = {vehicle.id: vehicle for vehicle in vehicle_group}

        for object_entry in ObjList_VIEW.object_list_for_draw:
            if object_entry.object_id != INVALID_OBJECT_ID:  # Ensure object_id is valid
                # Check if the vehicle already exists in the group
                if object_entry.object_id in vehicle_map:
                    vehicle = vehicle_map[object_entry.object_id]
                    # Update the existing vehicle's attributes
                    vehicle.rect.x = int(object_entry.LatPos)
                    vehicle.rect.y = int(object_entry.LgtPos)
                    vehicle.width = int(object_entry.DataWidth)
                    vehicle.height = int(object_entry.DataLen)
                    vehicle.speed = object_entry.LgtVelo
                    vehicle.dataConfidence = object_entry.DataConf
                    vehicle.label = (
                        'Unknown' if object_entry.Class == 0 else
                        'Car' if object_entry.Class == 1 else
                        'Bicycle' if object_entry.Class == 2 else
                        'Pedestrian'
                    )
                    vehicle.image.fill(
                        yellow if object_entry.Class == 0 else
                        red if object_entry.Class == 1 else
                        green if object_entry.Class == 2 else
                        gray
                    )
                else:
                    # Create a new vehicle if it doesn't exist
                    vehicle = Vehicle(
                        id_object=object_entry.object_id,
                        color=(
                            yellow if object_entry.Class == 0 else
                            red if object_entry.Class == 1 else
                            green if object_entry.Class == 2 else
                            gray
                        ),
                        x=int(object_entry.LatPos),
                        y=int(object_entry.LgtPos),
                        width=int(object_entry.DataWidth),
                        height=int(object_entry.DataLen),
                        speed=object_entry.LgtVelo,
                        dataConfidence=object_entry.DataConf,
                        label=(
                            'Unknown' if object_entry.Class == 0 else
                            'Car' if object_entry.Class == 1 else
                            'Bicycle' if object_entry.Class == 2 else
                            'Pedestrian'
                        )
                    )
                    vehicle_group.add(vehicle)  # Add the new vehicle to the group

                # Draw the vehicle
                draw_vehicle(screen, vehicle)

    # Draw all vehicles in the group
    vehicle_group.draw(screen)