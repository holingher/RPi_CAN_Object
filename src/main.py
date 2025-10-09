from multiprocessing import Process, Event, freeze_support
from typing import Any, Callable
import time
from pygame import QUIT, KEYDOWN
from init_com import init_com, deinit_com
from init_draw import init_draw, deinit_draw
from rx import radar_view, ego_motion_data, process_radar_rx, process_car_rx
from tx import process_tx_radar
from draw_3D import draw_3d_vehicle, draw_3d_road, draw_3d_rays
from draw_2D import draw_get_events, draw_own, draw_environment, draw_rays, draw_update, update_vehicle, update_vehicle_ai
from menu import draw_extraInfo, draw_exit_button, toggle_rays, is_rays_enabled
from simulate import init_process_sim_radar, process_sim_car, process_sim_radar
from defines import *
      
def periodic_task(interval_ms: float, task: Callable, stop_event, *args, **kwargs):
    next_run_time = time.time()
    while not stop_event.is_set():
        current_time = time.time()
        if current_time >= next_run_time:
            task(*args, **kwargs)
            next_run_time += interval_ms / 1000.0
        else:
            time_to_sleep = next_run_time - current_time
            time.sleep(time_to_sleep)

def main():
    """Optimized main function with improved data type handling"""
    try:
        EgoMotion_data_main = ego_motion_data
        
        # Initialize screen and vehicle groups
        main_screen, main_ego_group, main_vehicle_group, main_ego_vehicle = init_draw()
        # Initialize the CAN communication
        main_can_bus_radar, main_can_bus_car, main_radar_dbc = init_com()
        
        # Set display flags based on platform
        if not is_raspberrypi():
            init_process_sim_radar()
            
        '''
        # Create stop events for the processes
        stop_event_tx_radar = Event()
        stop_event_rx_radar = Event()
        stop_event_sim_radar = Event()

        # Start periodic tasks as processes
        tx_radar_process = Process(target=periodic_task, args=(60, process_tx_radar, stop_event_tx_radar, main_can_bus_radar))
        rx_radar_process = Process(target=periodic_task, args=(50, process_rx_radar, stop_event_rx_radar, main_radar_dbc, main_can_bus_radar))
        sim_radar_process = Process(target=periodic_task, args=(50, process_sim_radar, stop_event_sim_radar))

        tx_radar_process.start()
        rx_radar_process.start()
        sim_radar_process.start()
       '''
        # loop
        running = True
        def exit_callback():
            nonlocal running
            running = False
        while running:
            # Check for quit events
            for event in draw_get_events():
                # Check for quit event
                if event.type == QUIT:
                    # Exit the program
                    running = False
                # Allow closing with ESC key in fullscreen
                elif event.type == KEYDOWN and hasattr(event, 'key') and event.key == 27:  # 27 is pygame.K_ESCAPE
                    running = False

            # Set display flags based on platform
            if is_raspberrypi():
                # Process the RX data (uncomment when needed)
                process_radar_rx(main_radar_dbc, main_can_bus_radar)
                process_car_rx(main_can_bus_car)
            else:
                # simulate object list
                process_sim_radar(main_radar_dbc, main_can_bus_radar, main_can_bus_car) 
                EgoMotion_data_main = process_sim_car(main_can_bus_car)

            # Fill the screen with a color
            draw_environment(main_screen)
            
            #draw_3d_road(screen, road_width)
            #draw_3d_rays(screen, ego_vehicle)
            # Draw vehicles with 3D scaling
            #for vehicle in vehicle_group:
            #    draw_3d_vehicle(screen, vehicle)
            #    draw_shadow(screen, vehicle)  # Draw shadow for each vehicle
            
            # Draw own vehicle
            draw_own(main_screen, main_ego_vehicle, main_ego_group)
            # Update data for all vehicles
            update_vehicle(main_screen, main_vehicle_group)
            # Draw the exit button (top-right corner, 100x40 size)
            from menu import draw_exit_button
            draw_exit_button(main_screen, main_screen.get_width() - 110, 10, 100, 40, gray, exit_callback, label="Exit")

            # Draw the rays toggle button (top-left corner, 100x40 size)
            #draw_exit_button(main_screen, 10, 10, 100, 40, white, toggle_rays, label="Toggle Rays")
            
            # Use the menu state
            if is_rays_enabled[0]:
                draw_rays(main_screen, main_ego_vehicle, main_vehicle_group)

            draw_extraInfo(main_screen, EgoMotion_data_main, main_vehicle_group, radar_view.scan_id)

            # Update the display
            draw_update()  
            #print(main_vehicle_group)
        '''
        # Signal the processes to stop
        stop_event_sim_radar.set()
        stop_event_tx_radar.set()
        stop_event_rx_radar.set()
        tx_radar_process.join()
        rx_radar_process.join()
        stop_event_sim_radar.join()
        '''
        deinit_draw()
    except KeyboardInterrupt:
        '''
        stop_event_sim_radar.set()
        stop_event_tx_radar.set()
        stop_event_rx_radar.set()
        tx_radar_process.join()
        rx_radar_process.join()
        stop_event_sim_radar.join()
        '''
        deinit_com()
        deinit_draw()

if __name__ == "__main__":
    main()

