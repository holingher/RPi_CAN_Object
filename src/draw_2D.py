import pygame
import math
from pygame import Surface
from pygame.sprite import Group
from rx import object_list_for_draw_t
from defines import *

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

def draw_vehicle(screen: Surface, vehicle_group: Group):
    vehicle: Vehicle
    # draw the vehicles and their labels
    for vehicle in vehicle_group:
        # draw the vehicle rectangle
        screen.blit(vehicle.image, vehicle.rect)
        
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
    
    # draw the vehicles
    vehicle_group.draw(screen)
    
def add_or_update_vehicle(object_entry: object_list_for_draw_t, vehicle_group: Group):
    vehicle: Vehicle = None
    # Check if the vehicle already exists in the group using object_id
    for vehicle in vehicle_group:
        if object_entry and vehicle.object_id == object_entry.object_id:
            # Update vehicle properties
            vehicle.rect.x = object_entry.LatPos  # Update lateral position
            vehicle.rect.y = object_entry.LgtPos  # Update longitudinal position
            vehicle.width = object_entry.DataWidth  # Update width
            vehicle.height = object_entry.DataLen  # Update width
            vehicle.speed = object_entry.LgtVelo  # Update speed
            vehicle.dataConfidence = object_entry.DataConf  # Update confidence
            return  # Exit after updating the vehicle

    # If no matching vehicle exists, add a new one
    if object_entry:
        '''
        if random_data == True:
            color = [random.randint(0, 255) for _ in range(3)]  # Random color
            vehicle = Vehicle(
                object_id=random.randint(0, 29),
                color=color,
                x_position=random.randint(int(road_width/3), int(road_width + road_width - 10)),
                y_position=random.randint(-300, -50),
                width=random.randint(20, 50),
                label=random.choice(list(VehicleType)).value
            )
        else:
        '''
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
            object_id=object_entry.object_id,
            color=color,
            x_position=object_entry.LatPos,
            y_position=object_entry.LgtPos,
            width=object_entry.DataWidth,
            speed=object_entry.LgtVelo,
            dataConfidence=object_entry.DataConf,
            label=label
        )
        vehicle_group.add(vehicle)
