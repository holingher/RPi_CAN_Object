from pygame import draw as menu_draw
from pygame import font as menu_font
from pygame import mouse as menu_mouse
from pygame import event as menu_event
from pygame import MOUSEBUTTONDOWN
from pygame import Surface as menu_Surface
from defines import white, gray, green, black
from rx import toggle_can_sniffer, can_sniffer
from swipe_detector import swipe_detector

# Checkbox state
is_rays_enabled = [True]  # Use a mutable object to allow modification inside the action function
# Screen mode state
is_can_screen_enabled = [False]  # Toggle between main screen and CAN data screen

def toggle_rays():
    is_rays_enabled[0] = not is_rays_enabled[0]  # Toggle the checkbox state

def toggle_can_screen():
    """Toggle between main screen and CAN data screen"""
    is_can_screen_enabled[0] = not is_can_screen_enabled[0]
    # Enable CAN sniffer when switching to CAN screen
    if is_can_screen_enabled[0] and not can_sniffer.enabled:
        toggle_can_sniffer()

def handle_swipe_events(events):
    """
    Handle swipe gestures to switch between screens
    Returns True if a swipe was detected and handled
    """
    for event in events:
        swipe_direction = swipe_detector.handle_event(event)
        if swipe_direction == 'left':
            # Swipe left: go to CAN screen
            if not is_can_screen_enabled[0]:
                toggle_can_screen()
                return True
        elif swipe_direction == 'right':
            # Swipe right: go to main screen
            if is_can_screen_enabled[0]:
                toggle_can_screen()
                return True
    return False
        
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

def draw_exit_button(screen: menu_Surface, x, y, width, height, color, exit_callback, events, label="Exit"):
    """Draws an exit button and calls exit_callback when clicked."""
    # Draw the button rectangle
    rect = menu_draw.rect(screen, color, (x, y, width, height), border_radius=6)
    
    # Draw the label text centered in the button
    font = menu_font.Font(menu_font.get_default_font(), 20)
    text_surface = font.render(label, True, (0,0,0))
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

    # Handle click event
    for event in events:
        if event.type == MOUSEBUTTONDOWN:
            if rect.collidepoint(event.pos):
                mouse = menu_mouse.get_pos()
                if x < mouse[0] < x + width and y < mouse[1] < y + height:
                    exit_callback()

def draw_can_screen_toggle_button(screen: menu_Surface, x, y, width, height, color, label="CAN Data"):
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
                    toggle_can_screen()

def draw_swipe_instructions(screen: menu_Surface, is_can_screen=False):
    """Draw swipe instructions at the bottom of the screen"""
    instruction_font = menu_font.Font(menu_font.get_default_font(), 16)
    
    if is_can_screen:
        instruction_text = "← Swipe right to return to main view"
        color = white
    else:
        instruction_text = "Swipe left to view CAN data →"
        color = white
    
    text_surface = instruction_font.render(instruction_text, True, color)
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30))
    screen.blit(text_surface, text_rect)

def draw_can_data_screen(screen: menu_Surface):
    """Draw the CAN data screen showing raw CAN messages"""
    # Fill screen with black background
    screen.fill(black)
    
    # Draw title
    title_font = menu_font.Font(menu_font.get_default_font(), 24)
    title_text = title_font.render("CAN Message Monitor", True, white)
    screen.blit(title_text, (20, 20))
    
    # Draw column headers
    header_font = menu_font.Font(menu_font.get_default_font(), 18)
    header_y = 60
    screen.blit(header_font.render("CAN ID", True, white), (20, header_y))
    screen.blit(header_font.render("DLC", True, white), (120, header_y))
    screen.blit(header_font.render("Timestamp", True, white), (170, header_y))
    screen.blit(header_font.render("Raw Data", True, white), (400, header_y))
    
    # Draw separator line
    menu_draw.line(screen, white, (20, header_y + 25), (screen.get_width() - 20, header_y + 25), 2)
    
    # Draw CAN messages
    data_font = menu_font.Font(menu_font.get_default_font(), 14)
    start_y = header_y + 40
    line_height = 20
    max_messages = min(len(can_sniffer.messages), (screen.get_height() - start_y - 100) // line_height)
    
    for i, message in enumerate(can_sniffer.messages[:max_messages]):
        y_pos = start_y + (i * line_height)
        
        # Parse message string to extract components
        try:
            # Expected format: "ID: 0x123 | Data: AABBCC | Time: 123.456"
            parts = message.split(" | ")
            can_id = parts[0].replace("ID: ", "")
            timestamp = parts[1].replace("Time: ", "")
            data_part = parts[2].replace("Data: ", "")
            
            # Calculate DLC from data length
            dlc = len(data_part) // 2 if data_part != "00" else 0
            
            # Draw the data
            screen.blit(data_font.render(can_id, True, white), (20, y_pos))
            screen.blit(data_font.render(str(dlc), True, white), (120, y_pos))
            screen.blit(data_font.render(timestamp, True, white), (170, y_pos))
            screen.blit(data_font.render(data_part, True, white), (400, y_pos))
            
        except (IndexError, ValueError):
            # If parsing fails, just show the raw message
            screen.blit(data_font.render(message[:80], True, white), (20, y_pos))
    
    # Draw status info
    status_y = screen.get_height() - 60
    status_text = f"Messages captured: {len(can_sniffer.messages)}"
    screen.blit(data_font.render(status_text, True, white), (20, status_y))
    
    # Draw swipe instructions
    draw_swipe_instructions(screen, is_can_screen=True)