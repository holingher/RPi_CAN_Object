import pygame
import math
from pygame import Surface
from pygame.sprite import Group
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
def calculate_rays(screen: Surface, player):
    rays = []
    start_angle = -fov_angle*1.5  # Start angle relative to the player's forward direction
    angle_step = fov_angle / (ray_count - 1)  # Angle between each ray

    for i in range(ray_count):
        angle = math.radians(start_angle + i * angle_step)
        # Calculate the maximum ray length based on the screen edges
        if math.cos(angle) > 0:  # Ray pointing right
            max_x = screen.get_width() - player.rect.centerx
        else:  # Ray pointing left
            max_x = -player.rect.centerx

        if math.sin(angle) > 0:  # Ray pointing down
            max_y = screen.get_height() - player.rect.centery
        else:  # Ray pointing up
            max_y = -player.rect.centery

        # Calculate the ray length to the edge of the screen
        ray_length_x = max_x / math.cos(angle) if math.cos(angle) != 0 else float('inf')
        ray_length_y = max_y / math.sin(angle) if math.sin(angle) != 0 else float('inf')
        ray_length = min(ray_length_x, ray_length_y)

        # Calculate the end point of the ray
        end_x = player.rect.centerx + ray_length * math.cos(angle)
        end_y = player.rect.centery + ray_length * math.sin(angle)
        rays.append(((player.rect.centerx, player.rect.centery), (end_x, end_y)))

    return rays
  
def draw_rays(screen: Surface, player, vehicle_group: Group):
    # Create a transparent surface for drawing rays
    ray_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)  # Use SRCALPHA for transparency

    # Calculate and draw rays for the player's field of view
    rays = calculate_rays(screen, player)
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

def draw_vehicle(screen: Surface, vehicle_group: Group):
    # draw the vehicles and their labels
    for vehicle in vehicle_group:
        # draw the vehicle rectangle
        screen.blit(vehicle.image, vehicle.rect)
        
        # render the label above the rectangle
        font = pygame.font.Font(pygame.font.get_default_font(), 14)
        text = font.render(vehicle.label + " " + str(vehicle.speed), True, white)  # white text
        text_rect = text.get_rect(center=(vehicle.rect.centerx, vehicle.rect.top - 10))  # Position above the rectangle
        screen.blit(text, text_rect)

        # make the vehicles move
        vehicle.rect.y += vehicle.speed
        
        # remove vehicle once it goes off screen
        if vehicle.rect.top >= screen.get_height():
            vehicle.kill()
            
            # add to objects
            #objects += 1
            
            # speed up the game after passing 5 vehicles
            #if objects > 0 and objects % 5 == 0:
            #    speed += 1
    
    # draw the vehicles
    vehicle_group.draw(screen)

def draw_own(screen: Surface, player, player_group: Group):
    # draw the player's car
    player_group.draw(screen)
    
    # draw the player rectangle
    screen.blit(player.image, player.rect)
    
    # render the label above the rectangle
    font = pygame.font.Font(pygame.font.get_default_font(), 14)
    text = font.render(player.label, True, white)  # white text
    text_rect = text.get_rect(center=(player.rect.centerx, player.rect.top - 10))  # Position above the rectangle
    screen.blit(text, text_rect)
