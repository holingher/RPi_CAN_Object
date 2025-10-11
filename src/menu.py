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
previous_screen = ['main']  # Track previous screen: 'main' or 'can'

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
    Navigation pattern:
    - Main screen: LEFT → CAN screen, UP → Radar status
    - CAN screen: RIGHT → Main screen, UP → Radar status  
    - Radar status: DOWN → Previous screen (Main or CAN)
    Returns True if a swipe was detected and handled
    """
    from pygame import KEYDOWN, K_SPACE
    
    for event in events:
        # Handle swipe gestures
        swipe_direction = swipe_detector.handle_event(event)
        
        if swipe_direction == 'left':
            # Swipe left: Main screen → CAN screen
            if not is_can_screen_enabled[0] and not is_radar_status_screen_enabled[0]:
                previous_screen[0] = 'main'  # Remember we came from main
                toggle_can_screen()
                return True
                
        elif swipe_direction == 'right':
            # Swipe right: CAN screen → Main screen
            if is_can_screen_enabled[0] and not is_radar_status_screen_enabled[0]:
                return_to_main_screen()
                return True
                
        elif swipe_direction == 'up':
            # Swipe up: Main or CAN screen → Radar status screen
            if not is_radar_status_screen_enabled[0]:
                # Remember which screen we came from
                if is_can_screen_enabled[0]:
                    previous_screen[0] = 'can'
                else:
                    previous_screen[0] = 'main'
                toggle_radar_status_screen()
                return True
                
        elif swipe_direction == 'down':
            # Swipe down: Radar status → Previous screen (Main or CAN)
            if is_radar_status_screen_enabled[0]:
                is_radar_status_screen_enabled[0] = False
                if previous_screen[0] == 'can':
                    # Return to CAN screen
                    is_can_screen_enabled[0] = True
                else:
                    # Return to main screen (default)
                    is_can_screen_enabled[0] = False
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
        instruction_text = "→ Swipe right to main | ↑ Swipe up for radar status"
    elif is_radar_status_screen:
        prev_screen_name = previous_screen[0].upper()
        instruction_text = f"↓ Swipe down to return to {prev_screen_name} screen"
    else:
        instruction_text = "← Swipe left: CAN monitor | ↑ Swipe up: Radar status"
    
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
    """Draw comprehensive radar status information from FlrFlr1canFr96 dataclass optimized for 800x480"""
    from defines import get_raspberry_pi_temperature
    import pygame
    
    # Clear screen
    screen.fill((0, 0, 0))
    
    # Set up fonts - smaller for 800x480
    title_font = pygame.font.Font(None, 28)
    header_font = pygame.font.Font(None, 24)
    data_font = pygame.font.Font(None, 20)
    small_font = pygame.font.Font(None, 20)
    
    # Colors
    white = (255, 255, 255)
    green = (0, 255, 0)
    red = (255, 0, 0)
    yellow = (255, 255, 0)
    blue = (100, 149, 237)
    orange = (255, 165, 0)
    cyan = (0, 255, 255)
    gray = (128, 128, 128)
    
    # Title - more compact
    title_text = title_font.render("Radar Status (0x45)", True, white)
    screen.blit(title_text, (5, 2))
    
    # Layout for 800x480: 4 columns with tight spacing
    y_start = 35
    col1_x = 5      # E2E & System
    col2_x = 200    # Calibration & Software  
    col3_x = 400    # Position & Motion
    col4_x = 600    # Diagnostics & Faults
    line_height = 13
    
    if radar_signal_status is None:
        # No data available
        no_data_text = header_font.render("No radar status data available", True, red)
        screen.blit(no_data_text, (col1_x, y_start))
        no_data_info = data_font.render("Waiting for CAN ID 0x45 message...", True, yellow)
        screen.blit(no_data_info, (col1_x, y_start + 25))
    else:
        # Column 1: E2E & System Status (compact)
        header1 = header_font.render("E2E & System:", True, blue)
        screen.blit(header1, (col1_x, y_start))
        y1 = y_start + 18
        
        # Compact E2E data
        crc_text = small_font.render(f"CRC: {radar_signal_status.crc:04X}", True, white)
        screen.blit(crc_text, (col1_x, y1))
        y1 += line_height
        
        counter_text = small_font.render(f"Cnt: {radar_signal_status.counter}", True, white)
        screen.blit(counter_text, (col1_x, y1))
        y1 += line_height
        
        # System status with compact format
        sys_fail_color = green if not radar_signal_status.sys_fail_flag else red
        sys_text = small_font.render(f"Sys: {'OK' if not radar_signal_status.sys_fail_flag else 'FAIL'}", True, sys_fail_color)
        screen.blit(sys_text, (col1_x, y1))
        y1 += line_height
        
        rdr_sts_color = green if radar_signal_status.rdr_sts else red
        rdr_text = small_font.render(f"Rdr: {'ON' if radar_signal_status.rdr_sts else 'OFF'}", True, rdr_sts_color)
        screen.blit(rdr_text, (col1_x, y1))
        y1 += line_height
        
        rdr_trans_color = green if radar_signal_status.rdr_trans_act else yellow
        trans_text = small_font.render(f"TX: {'ON' if radar_signal_status.rdr_trans_act else 'OFF'}", True, rdr_trans_color)
        screen.blit(trans_text, (col1_x, y1))
        y1 += line_height
        
        # Temperature with color coding
        temp_color = green if radar_signal_status.internal_temp < 80 else (yellow if radar_signal_status.internal_temp < 90 else red)
        temp_text = small_font.render(f"Temp: {radar_signal_status.internal_temp:.0f}°C", True, temp_color)
        screen.blit(temp_text, (col1_x, y1))
        y1 += line_height
        
        # Timestamp status
        ts_color = green if radar_signal_status.timestamp_status else yellow  
        ts_text = small_font.render(f"TS: {'OK' if radar_signal_status.timestamp_status else 'BAD'}", True, ts_color)
        screen.blit(ts_text, (col1_x, y1))
        y1 += line_height
        
        signal_ub_color = green if not radar_signal_status.signal_status_ub else red
        ub_text = small_font.render(f"UB: {'OK' if not radar_signal_status.signal_status_ub else 'ERR'}", True, signal_ub_color)
        screen.blit(ub_text, (col1_x, y1))
        y1 += line_height
        
        scan_text = small_font.render(f"Scan: {radar_signal_status.scan_id_sts}", True, white)
        screen.blit(scan_text, (col1_x, y1))
        
        # Column 2: Calibration & Software
        header2 = header_font.render("Calibration:", True, blue)
        screen.blit(header2, (col2_x, y_start))
        y2 = y_start + 18
        
        # Compact calibration info
        cal_status_color = green if radar_signal_status.cal_sts == 3 else (yellow if radar_signal_status.cal_sts == 2 else red)
        cal_names = {0: "None", 1: "InProg", 2: "Part", 3: "Done"}
        cal_text = small_font.render(f"Cal: {cal_names.get(radar_signal_status.cal_sts, 'Unk')}", True, cal_status_color)
        screen.blit(cal_text, (col2_x, y2))
        y2 += line_height
        
        cal_result_color = green if radar_signal_status.cal_rlt_sts == 0 else (yellow if radar_signal_status.cal_rlt_sts == 1 else red)
        cal_result_names = {0: "OK", 1: "Warn", 2: "Err", 3: "Crit"}
        result_text = small_font.render(f"Res: {cal_result_names.get(radar_signal_status.cal_rlt_sts, 'Unk')}", True, cal_result_color)
        screen.blit(result_text, (col2_x, y2))
        y2 += line_height
        
        prog_text = small_font.render(f"Prog: {radar_signal_status.cal_prgrss_sts}", True, white)
        screen.blit(prog_text, (col2_x, y2))
        y2 += line_height
        
        wheel_text = small_font.render(f"WhlF: {radar_signal_status.whl_comp_fact:.2f}", True, white)
        screen.blit(wheel_text, (col2_x, y2))
        y2 += line_height + 3
        
        # Software versions
        sw_text = small_font.render(f"SW: {radar_signal_status.sw_vers_major}.{radar_signal_status.sw_vers_minor}", True, cyan)
        screen.blit(sw_text, (col2_x, y2))
        y2 += line_height
        
        if_text = small_font.render(f"IF: {radar_signal_status.if_vers_major}.{radar_signal_status.if_vers_minor}", True, cyan)
        screen.blit(if_text, (col2_x, y2))
        y2 += line_height + 3
        
        # Environment conditions
        blockage_color = green if radar_signal_status.blockage == 0 else (yellow if radar_signal_status.blockage <= 2 else red)
        block_names = {0: "None", 1: "Part", 2: "Sig", 3: "Full"}
        block_text = small_font.render(f"Blk: {block_names.get(radar_signal_status.blockage, 'Unk')}", True, blockage_color)
        screen.blit(block_text, (col2_x, y2))
        y2 += line_height
        
        interference_color = green if radar_signal_status.interference == 0 else (yellow if radar_signal_status.interference <= 2 else red)
        int_names = {0: "None", 1: "Low", 2: "Med", 3: "Hi"}
        int_text = small_font.render(f"Int: {int_names.get(radar_signal_status.interference, 'Unk')}", True, interference_color)
        screen.blit(int_text, (col2_x, y2))
        
        # Column 3: Position & Motion
        header3 = header_font.render("Position & Motion:", True, blue)
        screen.blit(header3, (col3_x, y_start))
        y3 = y_start + 18
        
        # Motion data
        speed_text = small_font.render(f"Spd: {radar_signal_status.ego_spd_est:.2f}m/s", True, white)
        screen.blit(speed_text, (col3_x, y3))
        y3 += line_height
        
        yaw_text = small_font.render(f"Yaw: {radar_signal_status.ego_yaw_rate_est:.3f}r/s", True, white)
        screen.blit(yaw_text, (col3_x, y3))
        y3 += line_height + 3
        
        # Position offsets (compact)
        pos_header = small_font.render("Offsets (m):", True, orange)
        screen.blit(pos_header, (col3_x, y3))
        y3 += line_height
        
        x_text = small_font.render(f"X: {radar_signal_status.x_axis_offs:.2f}", True, white)
        screen.blit(x_text, (col3_x, y3))
        y3 += line_height
        
        y_text = small_font.render(f"Y: {radar_signal_status.y_axis_offs:.2f}", True, white)
        screen.blit(y_text, (col3_x, y3))
        y3 += line_height
        
        z_text = small_font.render(f"Z: {radar_signal_status.z_axis_offs:.2f}", True, white)
        screen.blit(z_text, (col3_x, y3))
        y3 += line_height + 3
        
        # Orientation angles (compact)
        orient_header = small_font.render("Orient (°):", True, orange)
        screen.blit(orient_header, (col3_x, y3))
        y3 += line_height
        
        x_orient_text = small_font.render(f"X: {radar_signal_status.x_orient_ang:.0f}", True, white)
        screen.blit(x_orient_text, (col3_x, y3))
        y3 += line_height
        
        y_orient_text = small_font.render(f"Y: {radar_signal_status.y_orient_ang:.0f}", True, white)
        screen.blit(y_orient_text, (col3_x, y3))
        y3 += line_height
        
        z_orient_text = small_font.render(f"Z: {radar_signal_status.z_orient_ang:.0f}", True, white)
        screen.blit(z_orient_text, (col3_x, y3))
        
        # Column 4: Diagnostics & Faults
        header4 = header_font.render("Diagnostics:", True, blue)
        screen.blit(header4, (col4_x, y_start))
        y4 = y_start + 18
        
        # Fault information
        flt_color = green if radar_signal_status.flt_reason == 0 else red
        flt_text = small_font.render(f"Flt: {radar_signal_status.flt_reason}", True, flt_color)
        screen.blit(flt_text, (col4_x, y4))
        y4 += line_height
        
        comm_color = green if radar_signal_status.comm_flt_reason == 0 else red
        comm_text = small_font.render(f"Comm: {radar_signal_status.comm_flt_reason}", True, comm_color)
        screen.blit(comm_text, (col4_x, y4))
        y4 += line_height
        
        int_sts_text = small_font.render(f"IntSts: {radar_signal_status.rdr_int_sts}", True, white)
        screen.blit(int_sts_text, (col4_x, y4))
        y4 += line_height + 3
        
        # Angle corrections
        corr_header = small_font.render("Corrections (°):", True, orange)
        screen.blit(corr_header, (col4_x, y4))
        y4 += line_height
        
        azi_text = small_font.render(f"Az: {radar_signal_status.azi_ang_cor:.1f}", True, white)
        screen.blit(azi_text, (col4_x, y4))
        y4 += line_height
        
        ele_text = small_font.render(f"El: {radar_signal_status.ele_ang_cor:.1f}", True, white)
        screen.blit(ele_text, (col4_x, y4))
        y4 += line_height + 3
        
        # Timestamp info
        ts_header = small_font.render("Timing:", True, orange)
        screen.blit(ts_header, (col4_x, y4))
        y4 += line_height
        
        timestamp_text = small_font.render(f"TS: {radar_signal_status.timestamp}", True, white)
        screen.blit(timestamp_text, (col4_x, y4))
    
    # Draw Raspberry Pi temperature
    draw_temperature(screen, font_size=14)
    
    # Draw swipe instructions
    draw_swipe_instructions(screen, is_radar_status_screen=True)