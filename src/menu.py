from pygame import draw as menu_draw
from pygame import font as menu_font
from pygame import mouse as menu_mouse
from pygame import event as menu_event
from pygame import MOUSEBUTTONDOWN
from pygame import Surface as menu_Surface
from defines import white, gray, green
from rx import toggle_can_sniffer, can_sniffer

# Checkbox state
is_rays_enabled = [True]  # Use a mutable object to allow modification inside the action function

def toggle_rays():
    is_rays_enabled[0] = not is_rays_enabled[0]  # Toggle the checkbox state

def draw_simple_checkbox(screen: menu_Surface, x, y, size, is_checked, color, action, label=""):
    # Draw the checkbox border
    rect = menu_draw.rect(screen, color, (x, y, size, size), 2)

    for event in menu_event.get():
        if event.type == MOUSEBUTTONDOWN:
            if rect.collidepoint(event.pos):
                mouse = menu_mouse.get_pos()
                if x < mouse[0] < x + size and y < mouse[1] < y + size:
                    action()
                
    # Draw the checkmark if the checkbox is checked
    if is_checked:
        menu_draw.line(screen, color, (x + 4, y + size // 2), (x + size // 3, y + size - 4), 3)
        menu_draw.line(screen, color, (x + size // 3, y + size - 4), (x + size - 4, y + 4), 3)

    # Render the label text next to the checkbox
    font = menu_font.Font(menu_font.get_default_font(), 20)
    text_surface = font.render(label, True, color)
    text_rect = text_surface.get_rect(midleft=(x + size + 10, y + size // 2))
    screen.blit(text_surface, text_rect)
    
def draw_extraInfo(screen: menu_Surface, EgoMotion_data_local, vehicle_group, scanID):
    # display car info
    font = menu_font.Font(menu_font.get_default_font(), 16)
    text = font.render('Speed: ' + str(EgoMotion_data_local.speed), True, white)
    text_rect = text.get_rect()
    text_rect.center = (50, screen.get_height() - 40)
    screen.blit(text, text_rect)
    
    # display the objects count
    font = menu_font.Font(menu_font.get_default_font(), 16)
    text = font.render('Nb of objects: ' + str(len(vehicle_group)) + ' ScanID: ' + str(scanID), True, white)
    text_rect = text.get_rect()
    text_rect.center = (110, screen.get_height() - 20)
    screen.blit(text, text_rect)

def draw_exit_button(screen: menu_Surface, x, y, width, height, color, exit_callback, label="Exit"):
    """Draws an exit button and calls exit_callback when clicked."""
    # Draw the button rectangle
    rect = menu_draw.rect(screen, color, (x, y, width, height), border_radius=6)
    
    # Draw the label text centered in the button
    font = menu_font.Font(menu_font.get_default_font(), 20)
    text_surface = font.render(label, True, (0,0,0))
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

    # Handle click event
    for event in menu_event.get():
        if event.type == MOUSEBUTTONDOWN:
            if rect.collidepoint(event.pos):
                mouse = menu_mouse.get_pos()
                if x < mouse[0] < x + width and y < mouse[1] < y + height:
                    exit_callback()

def draw_sniffer_toggle_button(screen: menu_Surface, x, y, width, height, color, label="Toggle Sniffer"):
    """Draws a CAN sniffer toggle button"""
    # Draw button rectangle
    button_color = green if can_sniffer.enabled else gray
    menu_draw.rect(screen, button_color, (x, y, width, height))
    menu_draw.rect(screen, white, (x, y, width, height), 2)  # White border
    
    # Draw button text
    font = menu_font.Font(menu_font.get_default_font(), 16)
    text = font.render(label, True, white)
    text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text, text_rect)
    
    # Check for mouse click
    mouse_pos = menu_mouse.get_pos()
    mouse_clicked = False
    
    for event in menu_event.get():
        if event.type == MOUSEBUTTONDOWN:
            mouse_clicked = True
    
    if mouse_clicked and x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height:
        toggle_can_sniffer()