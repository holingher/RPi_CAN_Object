from draw_2D import calculate_rays
import pygame
from pygame import Surface
from defines import *

def draw_3d_vehicle(screen: Surface, vehicle):
    # Calculate the scale factor based on the vehicle's vertical position
    distance_factor = max(0.1, 1 - (vehicle.rect.centery / screen.get_height()))  # Closer objects are larger
    scaled_width = int(vehicle.width * distance_factor)
    scaled_height = int(vehicle.height * distance_factor)

    # Scale the vehicle's image
    scaled_image = pygame.transform.scale(vehicle.image, (scaled_width, scaled_height))

    # Adjust the position to keep the vehicle centered
    scaled_rect = scaled_image.get_rect(center=vehicle.rect.center)

    # Draw the scaled vehicle
    screen.blit(scaled_image, scaled_rect)

def draw_3d_road(screen: Surface, road_width):
    road_top_width = road_width * 0.5  # Narrower at the top
    road_bottom_width = road_width  # Wider at the bottom

    # Define the road's trapezoid points
    road_points = [
        (screen.get_width() / 2 - road_top_width / 2, 0),  # Top-left
        (screen.get_width() / 2 + road_top_width / 2, 0),  # Top-right
        (screen.get_width() / 2 + road_bottom_width / 2, screen.get_height()),  # Bottom-right
        (screen.get_width() / 2 - road_bottom_width / 2, screen.get_height()),  # Bottom-left
    ]

    # Draw the road
    pygame.draw.polygon(screen, gray, road_points)

    # Draw lane markers with perspective
    #for i in range(1, NUMBER_OF_LANES):
    lane_x_top = screen.get_width() / 2 - road_top_width / 2 + (road_top_width)
    lane_x_bottom = screen.get_width() / 2 - road_bottom_width / 2 + (road_bottom_width)
    pygame.draw.line(screen, white, (lane_x_top, 0), (lane_x_bottom, screen.get_height()), 2)

def draw_3d_rays(screen: Surface, player):
    rays = calculate_rays(player)
    for ray_start, ray_end in rays:
        # Scale the ray's endpoint based on its distance
        distance_factor = max(0.1, 1 - (ray_end[1] / screen.get_height()))
        scaled_end_x = ray_start[0] + (ray_end[0] - ray_start[0]) * distance_factor
        scaled_end_y = ray_start[1] + (ray_end[1] - ray_start[1]) * distance_factor

        # Draw the ray
        pygame.draw.line(screen, ray_color_no_hit, ray_start, (scaled_end_x, scaled_end_y), 2)
        

def draw_shadow(screen: Surface, vehicle):
    shadow_color = (50, 50, 50, 128)  # Semi-transparent gray
    shadow_width = vehicle.width
    shadow_height = 10  # Flat shadow
    shadow_rect = pygame.Rect(
        vehicle.rect.centerx - shadow_width // 2,
        vehicle.rect.bottom,
        shadow_width,
        shadow_height,
    )
    pygame.draw.ellipse(screen, shadow_color, shadow_rect)

      