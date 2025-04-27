#packages
import pygame
import sys
import math

#global constants
SCREEN_HEIGHT = 600#480
SCREEN_WIDTH = SCREEN_HEIGHT * 2
MAP_SIZE = 8
TILE_SIZE = int((SCREEN_WIDTH / 2) / MAP_SIZE)
FOV = math.pi / 2
HALF_FOV = FOV / 2
CASTED_RAYS = 80
STEP_ANGLE = FOV / CASTED_RAYS
MAX_DEPTH = int(MAP_SIZE * TILE_SIZE)
SCALE = (SCREEN_WIDTH / 2) / CASTED_RAYS
#global variables
#game window
win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

#draw car
car = pygame.Rect(50, 60, 50, 80)
#carImage_png = pygame.image.load("car-top-view.png").convert_alpha()
# New width and height will be (50, 30).
IMAGE_SMALL = pygame.transform.scale(car, (50, 50))

player_x = (SCREEN_WIDTH / 2) / 2
player_y = SCREEN_HEIGHT - 80
player_angle = math.pi

#map

MAP = (
    '########'
    '#      #'
    '#      #'
    '#      #'
    '#      #'
    '#      #'
    '#      #'
    '########'
)

#init pygame
pygame.init()


pygame.display.set_caption('RPi_Object_radar')
#init timer
clock = pygame.time.Clock()

def draw_map():
    #iterate over map
    for i in range(MAP_SIZE):
        for j in range(MAP_SIZE):
            #calculate square index
            square = i * MAP_SIZE + j
            print('i: ', i)
            print('j: ', j)
            print('square: ', square)
            #draw map
            pygame.draw.rect(
                surface=win, 
                color=(191, 191, 191) if MAP[square] == '#' else (65, 65, 65),
                rect=(j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE - 1, TILE_SIZE - 1)
            )

    #draw car in 2D
    #IMAGE_SMALL - car representation from png
    #coordinates in 2D: x: player_X position - offset of half of image
    #                   y: player_y position - hardcoded for now to 419
    win.blit(IMAGE_SMALL, ( int(player_x)-IMAGE_SMALL.get_width()/2, int(player_y))) # paint to screen

#ray-casting algorithm
def ray_casting():
    #left angle of FOV
    start_angle = player_angle - HALF_FOV
    
    #iterate over casted rays
    for ray in range(CASTED_RAYS):
        for depth in range(MAX_DEPTH):
            #get ray target coordinates
            target_x = player_x - math.sin(start_angle) * depth
            target_y = player_y +  math.cos(start_angle) * depth

            #convert target x, y coordinates to map col, row
            col = int(target_x / TILE_SIZE)
            row = int(target_y / TILE_SIZE)  

            #calculate map square index
            square = row * MAP_SIZE + col
            
            #print(square)

            if MAP[square] == '#':
               # pygame.draw.rect(
               #     surface=win, 
              #      color=(195, 137, 38), 
              #      rect=(col * TILE_SIZE, row * TILE_SIZE,  TILE_SIZE - 1, TILE_SIZE - 1)
              #      )
                
                #draw casted ray
                pygame.draw.line(
                    surface=win, 
                    color=(233, 166, 49), 
                    start_pos=(player_x, player_y), 
                    end_pos=(target_x, target_y)
                    )

                #wall shading
                #color = 255 / (1 + depth * depth * 0.0001)

                #fix fish eye effect
                depth *= math.cos(player_angle - start_angle) 

                #calculate wall_height
                #wall_height = 21000 / (depth)

                #fix stuck at the wall
                #if wall_height > SCREEN_HEIGHT:
                #    wall_height = SCREEN_HEIGHT

                #draw 3D projection
                #pygame.draw.rect(
               #     surface=win, 
               #     color=(color, color, color), 
                #    rect=(SCREEN_HEIGHT + ray * SCALE, (SCREEN_HEIGHT / 2) - wall_height / 2, SCALE, wall_height)
               #     )
                
                break

        #increment angle by step
        start_angle += STEP_ANGLE

#movement direction
forward = True

#game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)

    #update 2D background
    pygame.draw.rect(win, (0, 0, 0), (0, 0, SCREEN_HEIGHT, SCREEN_HEIGHT))

    #update 3D background
    #pygame.draw.rect(win, (100, 100, 100), (480, SCREEN_HEIGHT / 2, SCREEN_HEIGHT, SCREEN_HEIGHT))
   # pygame.draw.rect(win, (200, 200, 200), (480, -SCREEN_HEIGHT / 2, SCREEN_HEIGHT, SCREEN_HEIGHT))

    draw_map()
    ray_casting()

    #update display
    pygame.display.flip()