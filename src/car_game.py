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
width = 1024
height = 600
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size, pygame.SRCALPHA)
pygame.display.set_caption('RPi_Object_radar')

# colors
gray = (100, 100, 100)
yellow = (255, 232, 0)
red = (200, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)

# road and marker sizes
road_width = 300
marker_width = 10
marker_height = 50

# lane coordinates
NUMBER_OF_LANES = 3
lane_width = road_width / NUMBER_OF_LANES
left_lane = lane_width + marker_height
center_lane = lane_width * 2 + marker_height
right_lane = lane_width * 3 + marker_height
lanes = [left_lane, center_lane, right_lane]

# road and edge markers
road = (lane_width, 0, road_width, height)
left_edge_marker = (lane_width, 0, marker_width, height)
right_edge_marker = (road_width + lane_width, 0, marker_width, height)

# for animating movement of the lane markers
lane_marker_move_y = 0

# player's starting coordinates
player_x = center_lane
player_y = height - marker_height

# frame settings
clock = pygame.time.Clock()
fps = 120

# game settings
gameover = False
speed = 2
objects = 0

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
    start_angle = fov_angle / 2  # Start angle relative to the player's forward direction
    angle_step = fov_angle / (ray_count - 1)  # Angle between each ray

    for i in range(ray_count):
        angle = math.radians(start_angle + i * angle_step)
        end_x = player.rect.centerx + ray_length * math.cos(angle)
        end_y = player.rect.centery - ray_length * math.sin(angle)
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
            x_position = random.randint(int(lane_width), int(lane_width + road_width - 40))  # Ensure the vehicle stays within the road
            # select a random vertical position above the screen
            y_position = random.randint(-300, -50)  # Random position above the screen
            # select a random vehicle image
            color = [random.randint(0, 255) for _ in range(3)]  # random color
            
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
        text = font.render(vehicle.label, True, (255, 255, 255))  # white text
        text_rect = text.get_rect(center=(vehicle.rect.centerx, vehicle.rect.top - 10))  # Position above the rectangle
        screen.blit(text, text_rect)
    
    # make the vehicles move
    for vehicle in vehicle_group:
        vehicle.rect.y += speed
        
        # remove vehicle once it goes off screen
        if vehicle.rect.top >= height:
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
    distance_factor = max(0.1, 1 - (vehicle.rect.centery / height))  # Closer objects are larger
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
        (width / 2 - road_top_width / 2, 0),  # Top-left
        (width / 2 + road_top_width / 2, 0),  # Top-right
        (width / 2 + road_bottom_width / 2, height),  # Bottom-right
        (width / 2 - road_bottom_width / 2, height),  # Bottom-left
    ]

    # Draw the road
    pygame.draw.polygon(screen, gray, road_points)

    # Draw lane markers with perspective
    for i in range(1, NUMBER_OF_LANES):
        lane_x_top = width / 2 - road_top_width / 2 + i * (road_top_width / NUMBER_OF_LANES)
        lane_x_bottom = width / 2 - road_bottom_width / 2 + i * (road_bottom_width / NUMBER_OF_LANES)
        pygame.draw.line(screen, white, (lane_x_top, 0), (lane_x_bottom, height), 2)

def draw_3d_rays():
    rays = calculate_rays(player)
    for ray_start, ray_end in rays:
        # Scale the ray's endpoint based on its distance
        distance_factor = max(0.1, 1 - (ray_end[1] / height))
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
    
# game loop
running = True
while running:
    
    clock.tick(fps)
    
    for event in pygame.event.get():
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
    # Draw vehicles with 3D scaling
    #for vehicle in vehicle_group:
    #    draw_3d_vehicle(vehicle)
    #    draw_shadow(vehicle)  # Draw shadow for each vehicle
        
    draw_own()
    add_vehicle()
    draw_vehicle()
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