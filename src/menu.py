from pygame import draw as menu_draw
from pygame import font as menu_font
from pygame import mouse as menu_mouse
from pygame import event as menu_event
from pygame import MOUSEBUTTONDOWN
from pygame import Surface as menu_Surface
from defines import white, gray, green, black, get_raspberry_pi_temperature
from rx import toggle_can_sniffer, can_sniffer, radar_signal_status
from swipe_detector import swipe_detector

def draw_temperature(screen: menu_Surface, font_size=16):
    """Draw raspberry pi temperature at consistent location (left bottom corner)"""
    temp = get_raspberry_pi_temperature()
    if temp is not None:
        # Choose color based on temperature (green < 60°C, yellow 60-70°C, red > 70°C)
        if temp < 60:
            temp_color = green
        elif temp < 70:
            temp_color = (255, 255, 0)  # yellow
        else:
            temp_color = (255, 0, 0)  # red
        
        font = menu_font.Font(menu_font.get_default_font(), font_size)
        temp_text = font.render(f'CPU: {temp:.1f}°C', True, temp_color)
        # Position at left bottom corner with some margin
        temp_rect = temp_text.get_rect()
        temp_rect.bottomleft = (10, screen.get_height() - 10)
        screen.blit(temp_text, temp_rect)

# Checkbox state
is_rays_enabled = [True]  # Use a mutable object to allow modification inside the action function
# Screen mode state
is_can_screen_enabled = [False]  # Toggle between main screen and CAN data screen
is_radar_status_screen_enabled = [False]  # Toggle for radar status screen

# CAN screen pause functionality
is_can_screen_paused = [False]  # Toggle between paused and live mode
paused_messages = []  # Store messages when paused

# Timestamp optimization variables
base_timestamp = None
last_timestamp_display = ""

def toggle_rays():
    is_rays_enabled[0] = not is_rays_enabled[0]  # Toggle the checkbox state

def toggle_can_screen():
    """Toggle between main screen and CAN data screen"""
    is_can_screen_enabled[0] = not is_can_screen_enabled[0]
    # Enable CAN sniffer when switching to CAN screen
    if is_can_screen_enabled[0] and not can_sniffer.enabled:
        toggle_can_sniffer()

def toggle_radar_status_screen():
    """Toggle radar status screen"""
    is_radar_status_screen_enabled[0] = not is_radar_status_screen_enabled[0]
    # If enabling radar status, disable CAN screen
    if is_radar_status_screen_enabled[0]:
        is_can_screen_enabled[0] = False
    
def return_to_main_screen():
    """Return to main screen from any other screen"""
    is_can_screen_enabled[0] = False
    is_radar_status_screen_enabled[0] = False

def toggle_can_screen_pause():
    """Toggle pause state of CAN screen"""
    global paused_messages
    is_can_screen_paused[0] = not is_can_screen_paused[0]
    
    if is_can_screen_paused[0]:
        # When pausing, capture current messages
        paused_messages = can_sniffer.messages.copy() if hasattr(can_sniffer, 'messages') else []
    else:
        # When unpausing, clear paused messages to show live data
        paused_messages = []

def handle_swipe_events(events):
    """
    Handle swipe gestures to switch between screens and keyboard events for pause
    Returns True if a swipe was detected and handled
    """
    from pygame import KEYDOWN, K_SPACE
    
    for event in events:
        # Handle swipe gestures
        swipe_direction = swipe_detector.handle_event(event)
        if swipe_direction == 'left':
            # Swipe left: go to CAN screen (if not already there)
            if not is_can_screen_enabled[0] and not is_radar_status_screen_enabled[0]:
                toggle_can_screen()
                return True
        elif swipe_direction == 'right':
            # Swipe right: return to main screen
            if is_can_screen_enabled[0] or is_radar_status_screen_enabled[0]:
                return_to_main_screen()
                return True
        elif swipe_direction == 'up':
            # Swipe up: go to radar status screen
            if not is_radar_status_screen_enabled[0]:
                toggle_radar_status_screen()
                return True
        elif swipe_direction == 'down':
            # Swipe down: return to main screen from radar status
            if is_radar_status_screen_enabled[0]:
                return_to_main_screen()
                return True
        
        # Handle keyboard events for pause functionality
        elif event.type == KEYDOWN:
            if event.key == K_SPACE and is_can_screen_enabled[0]:
                # Spacebar: toggle pause when on CAN screen
                toggle_can_screen_pause()
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
    text_rect.center = (50, screen.get_height() - 60)
    screen.blit(text, text_rect)
    
    # display the objects count
    font = menu_font.Font(menu_font.get_default_font(), 16)
    text = font.render('Nb of objects: ' + str(len(vehicle_group)) + ' ScanID: ' + str(scanID), True, white)
    text_rect = text.get_rect()
    text_rect.center = (110, screen.get_height() - 40)
    screen.blit(text, text_rect)
    
    # display raspberry pi temperature at consistent location
    draw_temperature(screen, font_size=16)

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

def optimize_timestamp_display(timestamp, is_first_message):
    """
    Optimize timestamp display to save space by showing only changing parts.
    For first message, show full timestamp and set as base.
    For subsequent messages, show relative time or just the changing decimal part.
    """
    global base_timestamp, last_timestamp_display
    
    try:
        current_time = float(timestamp)
        
        if is_first_message or base_timestamp is None:
            # First message or reset - show full timestamp and set as base
            base_timestamp = int(current_time)  # Store integer part as base
            last_timestamp_display = f"{current_time:.3f}"
            return f"T:{current_time:.3f}"
        else:
            # Subsequent messages - show relative or optimized format
            time_diff = current_time - base_timestamp
            
            if time_diff < 1000:  # Within reasonable range
                # Show as offset from base time (e.g., "+1.234")
                return f"+{time_diff:.3f}"
            else:
                # Time jumped significantly, reset base
                base_timestamp = int(current_time)
                return f"T:{current_time:.3f}"
                
    except (ValueError, TypeError):
        # If parsing fails, return original timestamp
        return timestamp

def draw_swipe_instructions(screen: menu_Surface, is_can_screen=False, is_radar_status_screen=False):
    """Draw swipe instructions at the bottom of the screen"""
    instruction_font = menu_font.Font(menu_font.get_default_font(), 14)
    
    if is_can_screen:
        instruction_text = "← Swipe right to return to main | ↑ Swipe up for radar status"
    elif is_radar_status_screen:
        instruction_text = "↓ Swipe down to return to main | ← Swipe left for CAN data"
    else:
        instruction_text = "← Swipe left: CAN data | ↑ Swipe up: Radar status"
    
    text_surface = instruction_font.render(instruction_text, True, white)
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 30))
    screen.blit(text_surface, text_rect)

def draw_can_data_screen(screen: menu_Surface):
    """Draw the CAN data screen showing raw CAN messages"""
    # Fill screen with black background
    screen.fill(black)
    
    # Draw title with pause indication
    title_font = menu_font.Font(menu_font.get_default_font(), 24)
    if is_can_screen_paused[0]:
        title_text = title_font.render("CAN Message Monitor - PAUSED", True, (255, 255, 0))  # Yellow when paused
    else:
        title_text = title_font.render("CAN Message Monitor - LIVE", True, (0, 255, 0))  # Green when live
    screen.blit(title_text, (20, 20))
    
    # Draw column headers
    header_font = menu_font.Font(menu_font.get_default_font(), 18)
    header_y = 60
    screen.blit(header_font.render("Time", True, white), (20, header_y))
    screen.blit(header_font.render("CAN ID", True, white), (120, header_y))
    screen.blit(header_font.render("DLC", True, white), (220, header_y))
    screen.blit(header_font.render("Raw Data", True, white), (280, header_y))
    
    # Draw separator line
    menu_draw.line(screen, white, (20, header_y + 25), (screen.get_width() - 20, header_y + 25), 2)
    
    # Draw CAN messages
    data_font = menu_font.Font(menu_font.get_default_font(), 14)
    start_y = header_y + 40
    line_height = 20
    
    # Use paused messages if in pause mode, otherwise use live messages
    messages_to_display = paused_messages if is_can_screen_paused[0] else can_sniffer.messages
    max_messages = min(len(messages_to_display), (screen.get_height() - start_y - 100) // line_height)
    
    global base_timestamp, last_timestamp_display
    
    for i, message in enumerate(messages_to_display[:max_messages]):
        y_pos = start_y + (i * line_height)
        
        # Parse message string to extract components
        try:
            # Expected format: "ID: 0x123 | Time: 123.456 | Data: AABBCC"
            parts = message.split(" | ")
            timestamp = parts[0].replace("Time: ", "")
            can_id = parts[1].replace("ID: ", "")
            can_dlc = parts[2].replace("DLC: ", "")
            data_part = parts[3].replace("Data: ", "")
            
            # Calculate DLC from data length
            dlc = len(data_part) // 2 if data_part != "00" else 0
            
            # Optimize timestamp display - show only changing parts
            timestamp_display = optimize_timestamp_display(timestamp, i == 0)
            
            # Draw the data with optimized timestamp first
            screen.blit(data_font.render(timestamp_display, True, white), (20, y_pos))
            screen.blit(data_font.render(can_id, True, white), (120, y_pos))
            screen.blit(data_font.render(str(dlc), True, white), (220, y_pos))
            screen.blit(data_font.render(data_part, True, white), (280, y_pos))
            
        except (IndexError, ValueError):
            # If parsing fails, just show the raw message
            screen.blit(data_font.render(message[:80], True, white), (20, y_pos))
    
    # Draw status info with pause indication
    status_y = screen.get_height() - 80
    
    # Show pause status
    if is_can_screen_paused[0]:
        pause_status = "PAUSED - Press SPACE to resume"
        pause_color = (255, 255, 0)  # Yellow for paused state
        screen.blit(data_font.render(pause_status, True, pause_color), (20, status_y))
        status_text = f"Showing {len(paused_messages)} paused messages"
    else:
        status_text = f"Live: {len(can_sniffer.messages)} messages - Press SPACE to pause"
    
    screen.blit(data_font.render(status_text, True, white), (20, status_y + 20))
    
    # Draw raspberry pi temperature at consistent location (same as main screen)
    draw_temperature(screen, font_size=14)
    
    # Draw swipe instructions
    draw_swipe_instructions(screen, is_can_screen=True)

def draw_radar_status_screen(screen, radar_signal_status, events):
    """Draw radar status information from FlrFlr1canFr96 dataclass"""
    from defines import get_raspberry_pi_temperature
    import pygame
    
    # Clear screen
    screen.fill((0, 0, 0))
    
    # Set up fonts
    title_font = pygame.font.Font(None, 28)
    header_font = pygame.font.Font(None, 20)
    data_font = pygame.font.Font(None, 16)
    
    # Colors
    white = (255, 255, 255)
    green = (0, 255, 0)
    red = (255, 0, 0)
    yellow = (255, 255, 0)
    blue = (100, 149, 237)
    
    # Title
    title_text = title_font.render("Radar Status Monitor", True, white)
    screen.blit(title_text, (10, 10))
    
    y_offset = 45
    
    if radar_signal_status is None:
        # No data available
        no_data_text = header_font.render("No radar status data available", True, red)
        screen.blit(no_data_text, (10, y_offset))
        no_data_info = data_font.render("Waiting for CAN ID 0x45 message...", True, yellow)
        screen.blit(no_data_info, (10, y_offset + 25))
    else:
        # System Status Section
        status_header = header_font.render("System Status:", True, blue)
        screen.blit(status_header, (10, y_offset))
        y_offset += 25
        
        # Temperature
        temp_color = green if radar_signal_status.internal_temp < 80 else (yellow if radar_signal_status.internal_temp < 90 else red)
        temp_text = data_font.render(f"Temperature: {radar_signal_status.internal_temp}°C", True, temp_color)
        screen.blit(temp_text, (20, y_offset))
        y_offset += 18
        
        # Radar Status
        rdr_sts_color = green if radar_signal_status.rdr_sts else red
        rdr_sts_text = data_font.render(f"Radar Active: {'Yes' if radar_signal_status.rdr_sts else 'No'}", True, rdr_sts_color)
        screen.blit(rdr_sts_text, (20, y_offset))
        y_offset += 18
        
        # Calibration Status
        y_offset += 10
        calib_header = header_font.render("Calibration Status:", True, blue)
        screen.blit(calib_header, (10, y_offset))
        y_offset += 25
        
        # Calibration states
        cal_status_color = green if radar_signal_status.cal_sts == 3 else (yellow if radar_signal_status.cal_sts == 2 else red)
        cal_status_names = {0: "Not Calibrated", 1: "In Progress", 2: "Partially Done", 3: "Calibrated"}
        cal_status_text = data_font.render(f"Status: {cal_status_names.get(radar_signal_status.cal_sts, 'Unknown')}", True, cal_status_color)
        screen.blit(cal_status_text, (20, y_offset))
        y_offset += 18
        
        # Calibration progress
        cal_progress_text = data_font.render(f"Progress: {radar_signal_status.cal_prgrss_sts}", True, white)
        screen.blit(cal_progress_text, (20, y_offset))
        y_offset += 18
        
        # Software Information
        y_offset += 10
        sw_header = header_font.render("Software Information:", True, blue)
        screen.blit(sw_header, (10, y_offset))
        y_offset += 25
        
        sw_version_text = data_font.render(f"SW Version: {radar_signal_status.sw_vers_major}.{radar_signal_status.sw_vers_minor}", True, white)
        screen.blit(sw_version_text, (20, y_offset))
        y_offset += 18
        
        if_version_text = data_font.render(f"IF Version: {radar_signal_status.if_vers_major}.{radar_signal_status.if_vers_minor}", True, white)
        screen.blit(if_version_text, (20, y_offset))
        y_offset += 18
        
        # Diagnostic Information
        y_offset += 10
        diag_header = header_font.render("Diagnostics:", True, blue)
        screen.blit(diag_header, (10, y_offset))
        y_offset += 25
        
        # System Status
        sys_fail_color = green if not radar_signal_status.sys_fail_flag else red
        sys_fail_text = data_font.render(f"System Status: {'OK' if not radar_signal_status.sys_fail_flag else 'FAIL'}", True, sys_fail_color)
        screen.blit(sys_fail_text, (20, y_offset))
        y_offset += 18
        
        # CRC Status
        crc_text = data_font.render(f"CRC: {radar_signal_status.crc}", True, white)
        screen.blit(crc_text, (20, y_offset))
        y_offset += 18
        
        # Blockage and Interference
        blockage_color = green if radar_signal_status.blockage == 0 else (yellow if radar_signal_status.blockage == 1 else red)
        blockage_names = {0: "None", 1: "Partial", 2: "Full", 3: "Unknown"}
        blockage_text = data_font.render(f"Blockage: {blockage_names.get(radar_signal_status.blockage, 'Unknown')}", True, blockage_color)
        screen.blit(blockage_text, (20, y_offset))
        y_offset += 18
        
        interference_color = green if radar_signal_status.interference == 0 else red
        interference_names = {0: "None", 1: "Low", 2: "High", 3: "Critical"}
        interference_text = data_font.render(f"Interference: {interference_names.get(radar_signal_status.interference, 'Unknown')}", True, interference_color)
        screen.blit(interference_text, (20, y_offset))
        y_offset += 18
        
        # Communication Status
        y_offset += 10
        comm_header = header_font.render("Communication:", True, blue)
        screen.blit(comm_header, (10, y_offset))
        y_offset += 25
        
        msg_counter_text = data_font.render(f"Message Counter: {radar_signal_status.counter}", True, white)
        screen.blit(msg_counter_text, (20, y_offset))
        y_offset += 18
        
        timestamp_text = data_font.render(f"Timestamp: {radar_signal_status.timestamp}", True, white)
        screen.blit(timestamp_text, (20, y_offset))
        y_offset += 18
        
        # Ego Speed Estimation
        ego_speed_text = data_font.render(f"Ego Speed Est: {radar_signal_status.ego_spd_est:.2f} m/s", True, white)
        screen.blit(ego_speed_text, (20, y_offset))
    
    # Draw Raspberry Pi temperature
    draw_temperature(screen, font_size=14)
    
    # Draw swipe instructions
    draw_swipe_instructions(screen, is_radar_status_screen=True)