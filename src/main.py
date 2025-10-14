import time
import threading
from pygame import QUIT, KEYDOWN
from init_com import init_com, deinit_com
from init_draw import init_draw, deinit_draw
from rx import radar_view, ego_motion_data, process_CAN0_rx, process_CAN1_rx, radar_signal_status
from tx import periodic_CAN0_tx_TimeSync_125ms_wrapper, process_CAN0_tx_60ms_wrapper
from draw_3D import draw_3d_vehicle, draw_3d_road, draw_3d_rays
from draw_2D import draw_get_events, draw_own, draw_environment, draw_rays, draw_update, update_vehicle
from menu import draw_extraInfo, draw_exit_button, toggle_rays, is_rays_enabled, is_can_screen_enabled, draw_can_data_screen, handle_swipe_events, draw_swipe_instructions, is_radar_status_screen_enabled, draw_radar_status_screen
from simulate import init_process_sim_radar, process_sim_car, process_sim_radar
from defines import *

def main():
    """Optimized main function with improved data type handling"""
    try:
        EgoMotion_data_main = ego_motion_data
        
        # Initialize screen and vehicle groups
        main_screen, main_ego_group, main_vehicle_group, main_ego_vehicle = init_draw()
        # Initialize the CAN communication
        main_can_bus_CAN0, main_can_bus_CAN1, main_radar_dbc = init_com()
        
        # Set display flags based on platform
        if not is_raspberrypi():
            init_process_sim_radar()
            
        # Create stop events for threads
        stop_event_periodic_CAN0_tx_60ms = threading.Event()
        stop_event_periodic_CAN0_tx_TimeSync_125ms = threading.Event()

        # Start TX thread with wrapper function using existing CAN bus
        periodic_CAN0_tx_60ms_thread = threading.Thread(target=process_CAN0_tx_60ms_wrapper, args=(60, stop_event_periodic_CAN0_tx_60ms, main_can_bus_CAN0))
        periodic_CAN0_tx_60ms_thread.daemon = True
        periodic_CAN0_tx_60ms_thread.start()
        print("TX thread started - sending CAN messages every 60ms")

        # Start 125ms periodic thread
        periodic_CAN0_tx_TimeSync_125ms_thread = threading.Thread(target=periodic_CAN0_tx_TimeSync_125ms_wrapper, args=(125, stop_event_periodic_CAN0_tx_TimeSync_125ms, main_can_bus_CAN1))
        periodic_CAN0_tx_TimeSync_125ms_thread.daemon = True
        periodic_CAN0_tx_TimeSync_125ms_thread.start()
        print("125ms periodic thread started")
        
        # loop
        running = True
        def exit_callback():
            nonlocal running
            running = False

        while running:
            # Get all events for this frame
            events = draw_get_events()
            
            # Handle swipe gestures first
            handle_swipe_events(events)
            
            # Check for quit events
            for event in events:
                # Check for quit event
                if event.type == QUIT:
                    # Exit the program
                    running = False
                # Allow closing with ESC key in fullscreen
                elif event.type == KEYDOWN and hasattr(event, 'key') and event.key == 27:  # 27 is pygame.K_ESCAPE
                    running = False

            # Set display flags based on platform
            if is_raspberrypi():
                ##### CAN1 - Car #####
                # Process the RX data
                #process_CAN1_rx(main_can_bus_CAN1)
                # Process the TX data
                # not required as no data to send
                #process_CAN1_tx(main_can_bus_CAN1)

                ##### CAN0 - Radar #####
                # TX is now handled by separate process - removed from main loop
                # Process the RX data
                process_CAN0_rx(main_radar_dbc, main_can_bus_CAN1)
            else:
                # simulate object list
                process_sim_radar(main_radar_dbc, main_can_bus_CAN0, main_can_bus_CAN1) 
                EgoMotion_data_main = process_sim_car(main_can_bus_CAN1)

            # Check which screen to display
            if is_can_screen_enabled[0]:
                # Draw CAN data screen
                draw_can_data_screen(main_screen)
                
                # Draw exit button only on CAN screen
                draw_exit_button(main_screen, main_screen.get_width() - 110, 10, 100, 40, gray, exit_callback, events)
            elif is_radar_status_screen_enabled[0]:
                # Draw radar status screen
                draw_radar_status_screen(main_screen, radar_signal_status, events)
                
                # Draw exit button only on radar status screen
                draw_exit_button(main_screen, main_screen.get_width() - 110, 10, 100, 40, gray, exit_callback, events)
            else:
                # Fill the screen with a color
                draw_environment(main_screen)
                
                #draw_3d_road(main_screen, road_width)
                #draw_3d_rays(main_screen, main_ego_vehicle)
                # Draw vehicles with 3D scaling
                #for vehicle in main_vehicle_group:
                    #draw_3d_vehicle(main_screen, vehicle)
                    #draw_shadow(main_screen, vehicle)  # Draw shadow for each vehicle

                # Draw own vehicle
                draw_own(main_screen, main_ego_vehicle, main_ego_group)
                # Update data for all vehicles
                update_vehicle(main_screen, main_vehicle_group)
                # Use the menu state
                if is_rays_enabled[0]:
                    draw_rays(main_screen, main_ego_vehicle, main_vehicle_group)
                        
                # Draw the exit button (top-right corner, 100x40 size)
                draw_exit_button(main_screen, main_screen.get_width() - 110, 10, 100, 40, gray, exit_callback, events)

                # Draw vehicle and radar info
                draw_extraInfo(main_screen, EgoMotion_data_main, main_vehicle_group, radar_view.scan_id)
                
                # Draw swipe instructions
                draw_swipe_instructions(main_screen, is_can_screen=False, is_radar_status_screen=False)

            # Update the display
            draw_update()  
            #print(main_vehicle_group)
        
        # Clean shutdown
        stop_event_periodic_CAN0_tx_60ms.set()
        stop_event_periodic_CAN0_tx_TimeSync_125ms.set()
        periodic_CAN0_tx_60ms_thread.join()
        periodic_CAN0_tx_TimeSync_125ms_thread.join()
        deinit_draw()
    except KeyboardInterrupt:
        # Clean shutdown on interrupt
        stop_event_periodic_CAN0_tx_60ms.set()
        stop_event_periodic_CAN0_tx_TimeSync_125ms.set()
        periodic_CAN0_tx_60ms_thread.join()
        periodic_CAN0_tx_TimeSync_125ms_thread.join()
        deinit_com()
        deinit_draw()

if __name__ == "__main__":
    main()

