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
    """Draw comprehensive radar status information from FlrFlr1canFr96 dataclass"""
    from defines import get_raspberry_pi_temperature
    import pygame
    
    # Clear screen
    screen.fill((0, 0, 0))
    
    # Set up fonts
    title_font = pygame.font.Font(None, 24)
    header_font = pygame.font.Font(None, 20)
    data_font = pygame.font.Font(None, 18)
    
    # Colors
    white = (255, 255, 255)
    green = (0, 255, 0)
    red = (255, 0, 0)
    yellow = (255, 255, 0)
    blue = (100, 149, 237)
    orange = (255, 165, 0)
    cyan = (0, 255, 255)
    
    # Title
    title_text = title_font.render("Radar Signal Status Monitor (CAN ID: 0x45)", True, white)
    screen.blit(title_text, (10, 5))
    
    y_offset = 30
    col1_x = 10
    col2_x = 320
    col3_x = 630
    
    if radar_signal_status is None:
        # No data available
        no_data_text = header_font.render("No radar status data available", True, red)
        screen.blit(no_data_text, (col1_x, y_offset))
        no_data_info = data_font.render("Waiting for CAN ID 0x45 message...", True, yellow)
        screen.blit(no_data_info, (col1_x, y_offset + 25))
    else:
        # Column 1: E2E Protection & System Status
        # E2E Protection Header
        header = header_font.render("E2E Protection & System:", True, blue)
        screen.blit(header, (col1_x, y_offset))
        y1 = y_offset + 20
        
        # CRC and Counter
        crc_text = data_font.render(f"CRC: 0x{radar_signal_status.crc:04X}", True, white)
        screen.blit(crc_text, (col1_x, y1))
        y1 += 15
        
        counter_text = data_font.render(f"Counter: {radar_signal_status.counter}", True, white)
        screen.blit(counter_text, (col1_x, y1))
        y1 += 15
        
        # Timestamp
        timestamp_color = green if radar_signal_status.timestamp_status else yellow
        timestamp_text = data_font.render(f"Timestamp: {radar_signal_status.timestamp} ms", True, timestamp_color)
        screen.blit(timestamp_text, (col1_x, y1))
        y1 += 15
        
        ts_status_text = data_font.render(f"TS Status: {'Valid' if radar_signal_status.timestamp_status else 'Invalid'}", True, timestamp_color)
        screen.blit(ts_status_text, (col1_x, y1))
        y1 += 20
        
        # System Status
        sys_fail_color = green if not radar_signal_status.sys_fail_flag else red
        sys_fail_text = data_font.render(f"System Fail: {'No' if not radar_signal_status.sys_fail_flag else 'YES'}", True, sys_fail_color)
        screen.blit(sys_fail_text, (col1_x, y1))
        y1 += 15
        
        rdr_sts_color = green if radar_signal_status.rdr_sts else red
        rdr_sts_text = data_font.render(f"Radar Active: {'Yes' if radar_signal_status.rdr_sts else 'No'}", True, rdr_sts_color)
        screen.blit(rdr_sts_text, (col1_x, y1))
        y1 += 15
        
        rdr_trans_color = green if radar_signal_status.rdr_trans_act else yellow
        rdr_trans_text = data_font.render(f"Transmit Active: {'Yes' if radar_signal_status.rdr_trans_act else 'No'}", True, rdr_trans_color)
        screen.blit(rdr_trans_text, (col1_x, y1))
        y1 += 15
        
        # Signal Status UB
        signal_ub_color = green if not radar_signal_status.signal_status_ub else red
        signal_ub_text = data_font.render(f"Signal UB: {'OK' if not radar_signal_status.signal_status_ub else 'ERROR'}", True, signal_ub_color)
        screen.blit(signal_ub_text, (col1_x, y1))
        y1 += 20
        
        # Temperature
        temp_color = green if radar_signal_status.internal_temp < 80 else (yellow if radar_signal_status.internal_temp < 90 else red)
        temp_text = data_font.render(f"Internal Temp: {radar_signal_status.internal_temp:.1f}°C", True, temp_color)
        screen.blit(temp_text, (col1_x, y1))
        y1 += 15
        
        # Scan ID Status
        scan_id_text = data_font.render(f"Scan ID Status: {radar_signal_status.scan_id_sts}", True, white)
        screen.blit(scan_id_text, (col1_x, y1))
        
        # Column 2: Calibration & Versions
        # Calibration Header
        header2 = header_font.render("Calibration & Software:", True, blue)
        screen.blit(header2, (col2_x, y_offset))
        y2 = y_offset + 20
        
        # Calibration Status
        cal_status_color = green if radar_signal_status.cal_sts == 3 else (yellow if radar_signal_status.cal_sts == 2 else red)
        cal_status_names = {0: "Not Calibrated", 1: "In Progress", 2: "Partially Done", 3: "Calibrated"}
        cal_status_text = data_font.render(f"Cal Status: {cal_status_names.get(radar_signal_status.cal_sts, 'Unknown')} ({radar_signal_status.cal_sts})", True, cal_status_color)
        screen.blit(cal_status_text, (col2_x, y2))
        y2 += 15
        
        # Calibration Result Status
        cal_result_names = {0: "OK", 1: "Warning", 2: "Error", 3: "Critical"}
        cal_result_color = green if radar_signal_status.cal_rlt_sts == 0 else (yellow if radar_signal_status.cal_rlt_sts == 1 else red)
        cal_result_text = data_font.render(f"Cal Result: {cal_result_names.get(radar_signal_status.cal_rlt_sts, 'Unknown')} ({radar_signal_status.cal_rlt_sts})", True, cal_result_color)
        screen.blit(cal_result_text, (col2_x, y2))
        y2 += 15
        
        # Calibration Progress
        cal_progress_text = data_font.render(f"Cal Progress: {radar_signal_status.cal_prgrss_sts}", True, white)
        screen.blit(cal_progress_text, (col2_x, y2))
        y2 += 15
        
        # Wheel Compensation Factor
        whl_comp_text = data_font.render(f"Wheel Comp: {radar_signal_status.whl_comp_fact:.3f}", True, white)
        screen.blit(whl_comp_text, (col2_x, y2))
        y2 += 20
        
        # Software Versions
        sw_version_text = data_font.render(f"SW Version: {radar_signal_status.sw_vers_major}.{radar_signal_status.sw_vers_minor}", True, cyan)
        screen.blit(sw_version_text, (col2_x, y2))
        y2 += 15
        
        if_version_text = data_font.render(f"IF Version: {radar_signal_status.if_vers_major}.{radar_signal_status.if_vers_minor}", True, cyan)
        screen.blit(if_version_text, (col2_x, y2))
        y2 += 20
        
        # Blockage and Interference
        blockage_color = green if radar_signal_status.blockage == 0 else (yellow if radar_signal_status.blockage <= 2 else red)
        blockage_names = {0: "None", 1: "Partial", 2: "Significant", 3: "Full"}
        blockage_text = data_font.render(f"Blockage: {blockage_names.get(radar_signal_status.blockage, 'Unknown')} ({radar_signal_status.blockage})", True, blockage_color)
        screen.blit(blockage_text, (col2_x, y2))
        y2 += 15
        
        interference_color = green if radar_signal_status.interference == 0 else (yellow if radar_signal_status.interference <= 2 else red)
        interference_names = {0: "None", 1: "Low", 2: "Medium", 3: "High"}
        interference_text = data_font.render(f"Interference: {interference_names.get(radar_signal_status.interference, 'Unknown')} ({radar_signal_status.interference})", True, interference_color)
        screen.blit(interference_text, (col2_x, y2))
        y2 += 20
        
        # Fault Information
        fault_header = data_font.render("Fault Information:", True, orange)
        screen.blit(fault_header, (col2_x, y2))
        y2 += 15
        
        flt_reason_color = green if radar_signal_status.flt_reason == 0 else red
        flt_reason_text = data_font.render(f"Fault Reason: {radar_signal_status.flt_reason}", True, flt_reason_color)
        screen.blit(flt_reason_text, (col2_x, y2))
        y2 += 15
        
        comm_flt_color = green if radar_signal_status.comm_flt_reason == 0 else red
        comm_flt_text = data_font.render(f"Comm Fault: {radar_signal_status.comm_flt_reason}", True, comm_flt_color)
        screen.blit(comm_flt_text, (col2_x, y2))
        y2 += 15
        
        rdr_int_sts_text = data_font.render(f"Radar Int Status: {radar_signal_status.rdr_int_sts}", True, white)
        screen.blit(rdr_int_sts_text, (col2_x, y2))
        
        # Column 3: Position, Motion & Orientation (if space allows)
        if screen.get_width() > 800:
            # Position and Motion Header
            header3 = header_font.render("Position & Motion:", True, blue)
            screen.blit(header3, (col3_x, y_offset))
            y3 = y_offset + 20
            
            # Ego Speed and Yaw Rate
            ego_speed_text = data_font.render(f"Ego Speed: {radar_signal_status.ego_spd_est:.3f} m/s", True, white)
            screen.blit(ego_speed_text, (col3_x, y3))
            y3 += 15
            
            ego_yaw_text = data_font.render(f"Ego Yaw Rate: {radar_signal_status.ego_yaw_rate_est:.6f} rad/s", True, white)
            screen.blit(ego_yaw_text, (col3_x, y3))
            y3 += 20
            
            # Position Offsets
            offset_header = data_font.render("Position Offsets (m):", True, orange)
            screen.blit(offset_header, (col3_x, y3))
            y3 += 15
            
            x_offs_text = data_font.render(f"X-Axis: {radar_signal_status.x_axis_offs:.3f}", True, white)
            screen.blit(x_offs_text, (col3_x, y3))
            y3 += 15
            
            y_offs_text = data_font.render(f"Y-Axis: {radar_signal_status.y_axis_offs:.3f}", True, white)
            screen.blit(y_offs_text, (col3_x, y3))
            y3 += 15
            
            z_offs_text = data_font.render(f"Z-Axis: {radar_signal_status.z_axis_offs:.3f}", True, white)
            screen.blit(z_offs_text, (col3_x, y3))
            y3 += 20
            
            # Orientation Angles
            orient_header = data_font.render("Orientation Angles (°):", True, orange)
            screen.blit(orient_header, (col3_x, y3))
            y3 += 15
            
            x_orient_text = data_font.render(f"X-Orient: {radar_signal_status.x_orient_ang:.1f}", True, white)
            screen.blit(x_orient_text, (col3_x, y3))
            y3 += 15
            
            y_orient_text = data_font.render(f"Y-Orient: {radar_signal_status.y_orient_ang:.1f}", True, white)
            screen.blit(y_orient_text, (col3_x, y3))
            y3 += 15
            
            z_orient_text = data_font.render(f"Z-Orient: {radar_signal_status.z_orient_ang:.1f}", True, white)
            screen.blit(z_orient_text, (col3_x, y3))
            y3 += 20
            
            # Angle Corrections
            corr_header = data_font.render("Angle Corrections (°):", True, orange)
            screen.blit(corr_header, (col3_x, y3))
            y3 += 15
            
            azi_corr_text = data_font.render(f"Azimuth: {radar_signal_status.azi_ang_cor:.1f}", True, white)
            screen.blit(azi_corr_text, (col3_x, y3))
            y3 += 15
            
            ele_corr_text = data_font.render(f"Elevation: {radar_signal_status.ele_ang_cor:.1f}", True, white)
            screen.blit(ele_corr_text, (col3_x, y3))
        else:
            # For smaller screens, show motion data in column 2 below faults
            y2 += 20
            motion_header = data_font.render("Motion Data:", True, orange)
            screen.blit(motion_header, (col2_x, y2))
            y2 += 15
            
            ego_speed_text = data_font.render(f"Ego Speed: {radar_signal_status.ego_spd_est:.2f} m/s", True, white)
            screen.blit(ego_speed_text, (col2_x, y2))
            y2 += 15
            
            ego_yaw_text = data_font.render(f"Yaw Rate: {radar_signal_status.ego_yaw_rate_est:.4f} rad/s", True, white)
            screen.blit(ego_yaw_text, (col2_x, y2))
    
    # Draw Raspberry Pi temperature
    draw_temperature(screen, font_size=14)
    
    # Draw swipe instructions
    draw_swipe_instructions(screen, is_radar_status_screen=True)