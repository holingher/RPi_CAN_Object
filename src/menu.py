import pygame
from rx import egomotion_t
from defines import *

# Checkbox state
is_rays_enabled = [True]  # Use a mutable object to allow modification inside the action function

def toggle_rays():
    is_rays_enabled[0] = not is_rays_enabled[0]  # Toggle the checkbox state

def draw_simple_checkbox(screen, x, y, size, is_checked, color, action, label=""):
    # Draw the checkbox border
    rect = pygame.draw.rect(screen, color, (x, y, size, size), 2)

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
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
    
def draw_extraInfo(screen: pygame.Surface, EgoMotion_data: egomotion_t, vehicle_group, scanID):
    # display car info
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render('Speed: ' + str(EgoMotion_data.Speed), True, white)
    text_rect = text.get_rect()
    text_rect.center = (50, screen.get_height() - 40)
    screen.blit(text, text_rect)
    
    # display the objects count
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render('Nb of objects: ' + str(len(vehicle_group)) + ' ScanID: ' + str(scanID), True, white)
    text_rect = text.get_rect()
    text_rect.center = (110, screen.get_height() - 20)
    screen.blit(text, text_rect)
    