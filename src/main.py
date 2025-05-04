from threading import Event, Thread
import time
from pygame import QUIT
from init_com import init_com, deinit_com
from init_draw import init_draw, deinit_draw
from rx import egomotion_t, process_rx_radar, process_rx_car
from tx import process_tx_radar
from draw_3D import draw_3d_vehicle, draw_3d_road, draw_3d_rays
from draw_2D import draw_get_events, draw_own, draw_environment, draw_rays, draw_update, update_vehicle, update_vehicle_ai
from menu import draw_extraInfo, draw_simple_checkbox, toggle_rays, is_rays_enabled
from simulate import init_process_rx_radar_simulation, object_vehicle_speed_simulation, process_rx_car_simulation, process_rx_radar_simulation
from defines import *

def periodic_task(interval_ms, task, stop_event:Event, *args, **kwargs):
    """
    Runs a task periodically at a fixed interval.

    :param interval_ms: Interval in milliseconds
    :param task: The function to execute periodically
    :param args: Positional arguments for the task
    :param kwargs: Keyword arguments for the task
    """
    next_run_time = time.time()
    while not stop_event.is_set():
        current_time = time.time()
        if current_time >= next_run_time:
            task(*args, **kwargs)  # Execute the task
            next_run_time += interval_ms / 1000.0  # Schedule the next run
        else:
            time_to_sleep = next_run_time - current_time
            time.sleep(time_to_sleep)  # Sleep until the next run time
                      
def main():
    try:
        EgoMotion_data_main:egomotion_t
        # Initialize screen and vehicle groups
        main_screen, main_ego_group, main_vehicle_group, main_ego_vehicle = init_draw() # Initialize the drawing
        # Initialize the CAN communication
        main_can_bus_radar, main_can_bus_car, main_radar_dbc = init_com()  # Initialize the CAN communication
            
        init_process_rx_radar_simulation() # Initialize the object list for simulation
        
        # https://github.com/skpang/PiCAN-Python-examples/blob/master/obdii_logger.py
        # do https://github.com/bkakilli/periodicrun to get 60 ms cycle time
        # Create a stop event for the thread
        stop_event_tx_radar_thread = Event()    
        stop_event_object_vehicle_speed_simulation_thread = Event()   
        # Create a thread for periodic_task_60ms
        # Pass the 
        # cycle_time
        # the function to be executed    
        # the stop event for this thread
        # can_bus_radar            
        tx_radar_thread = Thread(target=periodic_task, args=(60, process_tx_radar, stop_event_tx_radar_thread, main_can_bus_radar))
        object_vehicle_speed_simulation_thread = Thread(target=periodic_task, args=(50, object_vehicle_speed_simulation, stop_event_object_vehicle_speed_simulation_thread))
        # Start the thread
        tx_radar_thread.start()
        object_vehicle_speed_simulation_thread.start()
        
        # loop
        running = True
        while running:
            # Check for quit events
            for event in draw_get_events():
                # Check for quit event
                if event.type == QUIT:
                    # Exit the program
                    running = False

            # simulate object list
            ObjList_VIEW_main  = process_rx_radar_simulation(main_radar_dbc, main_can_bus_radar, main_can_bus_car) 
            EgoMotion_data_main = process_rx_car_simulation(main_can_bus_car) 
            # Process the RX data
            #ObjList_VIEW_main = process_rx_radar(main_radar_dbc, main_can_bus_radar)
            #EgoMotion_data_main = process_rx_car(main_can_bus_car)
			
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
            update_vehicle(main_screen, ObjList_VIEW_main, main_vehicle_group)
            #update_vehicle_ai(main_screen, main_vehicle_group)

            # Draw the checkbox
            #draw_simple_checkbox(screen, 50, screen.get_height() - 100, 20, is_rays_enabled[0], white, toggle_rays, label="Enable Rays")
            
            # Use the menu state
            if is_rays_enabled[0]:
                draw_rays(main_screen, main_ego_vehicle, main_vehicle_group)
            
            draw_extraInfo(main_screen, EgoMotion_data_main, main_vehicle_group, ObjList_VIEW_main.ScanID)
            
            # Update the display
            draw_update()  
            #print(main_vehicle_group)
        # Signal the thread to stop
        stop_event_object_vehicle_speed_simulation_thread.set()
        stop_event_tx_radar_thread.set()
        tx_radar_thread.join()  # Wait for the thread to finish 
        object_vehicle_speed_simulation_thread.join()
        deinit_draw()  
    except KeyboardInterrupt:
        stop_event_object_vehicle_speed_simulation_thread.set()
        stop_event_tx_radar_thread.set()  # Ensure the thread stops on a keyboard interrupt
        tx_radar_thread.join()
        object_vehicle_speed_simulation_thread.join()
        deinit_com()
        deinit_draw()
        
if __name__=="__main__":
    main()
    
