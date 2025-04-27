import math
import pygame
from pygame.locals import *
import random
from enum import Enum

# Define an enum for vehicle types
class VehicleType(Enum):
    VEHICLE = "Vehicle"
    BICYCLE = "Bicycle"
    PEDESTRIAN = "Pedestrian"
    MOTORCYCLE = "Motorcycle"
    TRUCK = "Truck"
pygame.init()

# create the window
surface_width = 1024
surface_height = 600
screen_size = (surface_width, surface_height)
screen = pygame.display.set_mode(screen_size, pygame.SRCALPHA)
pygame.display.set_caption('RPi_Object_radar')

# colors
gray = (100, 100, 100)
yellow = (255, 232, 0)
red = (200, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
black = (0, 0, 0)

# road and marker sizes
road_width = 510
marker_width = 10
marker_height = 50

# lane coordinates
lane_width = road_width
#left_lane = lane_width
#right_lane = road_width

# road and edge markers
road = (road_width, 0, road_width, screen.get_height())
#left_edge_marker = (lane_width, 0, marker_width, screen.get_height())
#right_edge_marker = (road_width, 0, marker_width, screen.get_height())

# for animating movement of the lane markers
lane_marker_move_y = 0

# player's starting coordinates
player_x = round(surface_width / 2 / 10) * 10#road_width + marker_height 
player_y = screen.get_height() - marker_height

# frame settings
clock = pygame.time.Clock()
fps = 120

# game settings
gameover = False
speed = 2
objects = 0
running = True

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, color, x, y, label=''):
        pygame.sprite.Sprite.__init__(self)
        
        # define the size of the rectangle
        self.width = 20
        self.height = 40
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(color)
        
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        
        # set the label for the vehicle
        self.label = label
        
class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        color = (0, 0, 255)  # blue color for the player's car
        super().__init__(color, x, y, label="Own")
        
# sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

# create the player's car
player = PlayerVehicle(player_x, player_y)
player_group.add(player)
    
# load the crash image
crash_color = (255, 0, 0)  # red for crash indication
crash_rect = pygame.Rect(0, 0, 40, 40)  # Placeholder rectangle for crash

# Define ray tracing parameters
ray_count = 100  # Number of rays in the field of view
ray_length = 600  # Length of each ray
ray_color_hit = (0, 255, 0, 64)  # Green color for the rays that hit a vehicle
ray_color_no_hit = (255, 0, 0, 64)  # Red color for the rays
fov_angle = 90  # Field of view angle in degrees

# Function to calculate rays based on FOV
def calculate_rays(player):
    rays = []
    start_angle = -fov_angle*1.5  # Start angle relative to the player's forward direction
    angle_step = fov_angle / (ray_count - 1)  # Angle between each ray

    for i in range(ray_count):
        angle = math.radians(start_angle + i * angle_step)
        # Calculate the maximum ray length based on the screen edges
        if math.cos(angle) > 0:  # Ray pointing right
            max_x = surface_width - player.rect.centerx
        else:  # Ray pointing left
            max_x = -player.rect.centerx

        if math.sin(angle) > 0:  # Ray pointing down
            max_y = surface_height - player.rect.centery
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
  
def draw_rays():
    # Create a transparent surface for drawing rays
    ray_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)  # Use SRCALPHA for transparency

    # Calculate and draw rays for the player's field of view
    rays = calculate_rays(player)
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
            
def add_vehicle():
    # add a vehicle
    if len(vehicle_group) < 30:
        # ensure there's enough gap between vehicles
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height:
                add_vehicle = False
                
        if add_vehicle:
            # select a random horizontal position within the road boundaries
            x_position = random.randint(int(lane_width/3), int(lane_width + road_width - 10))  # Ensure the vehicle stays within the road
            # select a random vertical position above the screen
            y_position = random.randint(-300, -50)
            # select a random vehicle color
            color = [random.randint(0, 255) for _ in range(3)]
            
            # select a random label from the VehicleType enum
            label = random.choice(list(VehicleType)).value
            
            vehicle = Vehicle(color, x_position, y_position, label=label)
            vehicle_group.add(vehicle)

def draw_vehicle():
    global speed, objects
    # draw the vehicles and their labels
    for vehicle in vehicle_group:
        # draw the vehicle rectangle
        screen.blit(vehicle.image, vehicle.rect)
        
        # render the label above the rectangle
        font = pygame.font.Font(pygame.font.get_default_font(), 14)
        text = font.render(vehicle.label, True, white)  # white text
        text_rect = text.get_rect(center=(vehicle.rect.centerx, vehicle.rect.top - 10))  # Position above the rectangle
        screen.blit(text, text_rect)
    
    # make the vehicles move
    for vehicle in vehicle_group:
        vehicle.rect.y += speed
        
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
    
def draw_3d_vehicle(vehicle):
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

def draw_3d_road():
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

def draw_3d_rays():
    rays = calculate_rays(player)
    for ray_start, ray_end in rays:
        # Scale the ray's endpoint based on its distance
        distance_factor = max(0.1, 1 - (ray_end[1] / screen.get_height()))
        scaled_end_x = ray_start[0] + (ray_end[0] - ray_start[0]) * distance_factor
        scaled_end_y = ray_start[1] + (ray_end[1] - ray_start[1]) * distance_factor

        # Draw the ray
        pygame.draw.line(screen, ray_color_no_hit, ray_start, (scaled_end_x, scaled_end_y), 2)
        
def draw_own():
    # draw the player's car
    player_group.draw(screen)
    
    # draw the player rectangle
    screen.blit(player.image, player.rect)
    
    # render the label above the rectangle
    font = pygame.font.Font(pygame.font.get_default_font(), 14)
    text = font.render(player.label, True, white)  # white text
    text_rect = text.get_rect(center=(player.rect.centerx, player.rect.top - 10))  # Position above the rectangle
    screen.blit(text, text_rect)
    
def draw_environment():
    global lane_marker_move_y 
    # draw the grass
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

def draw_shadow(vehicle):
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
# Checkbox state
is_rays_enabled = [True]  # Use a mutable object to allow modification inside the action function

def toggle_rays():
    is_rays_enabled[0] = not is_rays_enabled[0]  # Toggle the checkbox state

def draw_simple_checkbox(x, y, size, is_checked, color, action, label=""):
    # Draw the checkbox border
    rect = pygame.draw.rect(screen, color, (x, y, size, size), 2)

    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            if rect.collidepoint(event.pos):
                mouse = pygame.mouse.get_pos()
                if x < mouse[0] < x + size and y < mouse[1] < y + size:
                    action()
                
    # Draw the checkmark if the checkbox is checked
    if is_checked:
        pygame.draw.line(screen, color, (x + 4, y + size // 2), (x + size // 3, y + size - 4), 3)
        pygame.draw.line(screen, color, (x + size // 3, y + size - 4), (x + size - 4, y + 4), 3)

    # Render the label text next to the checkbox
    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    text_surface = font.render(label, True, color)
    text_rect = text_surface.get_rect(midleft=(x + size + 10, y + size // 2))
    screen.blit(text_surface, text_rect)
    
# game loop
running = True
while running:
    
    clock.tick(fps)
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            running = False
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
    draw_environment()
    
    #draw_3d_road()
    #draw_3d_rays()
    # Draw vehicles with 3D scaling
    #for vehicle in vehicle_group:
    #    draw_3d_vehicle(vehicle)
    #    draw_shadow(vehicle)  # Draw shadow for each vehicle
        
    draw_own()
    add_vehicle()
    draw_vehicle()
    # Draw the checkbox
    #draw_simple_checkbox(50, screen.get_height() - 100, 20, is_rays_enabled[0], white, toggle_rays, label="Enable Rays")
    # Use the menu state
    if is_rays_enabled[0]:
        draw_rays()
    
    # display the objects count
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render('Nb of objects: ' + str(len(vehicle_group)), True, white)
    text_rect = text.get_rect()
    text_rect.center = (100, screen.get_height() - 50)
    screen.blit(text, text_rect)
    
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