from multiprocessing import Process, Event, freeze_support
import time
from pygame import QUIT
from init_com import init_com, deinit_com
from init_draw import init_draw, deinit_draw
from rx import ObjList_VIEW, VIEW_t, egomotion_t, object_list_for_draw_t, process_rx_radar, process_rx_car
from tx import process_tx_radar
from draw_3D import draw_3d_vehicle, draw_3d_road, draw_3d_rays
from draw_2D import draw_get_events, draw_own, draw_environment, draw_rays, draw_update, update_vehicle, update_vehicle_ai
from menu import draw_extraInfo, draw_simple_checkbox, toggle_rays, is_rays_enabled
from simulate import init_process_sim_radar, process_sim_car, process_sim_radar
from defines import *
      
def periodic_task(interval_ms, task, stop_event: Event, *args, **kwargs):
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
    try:
        EgoMotion_data_main: egomotion_t
        '''
        # Initialize the shared object list using a manager
        manager = Manager()
        ObjList_VIEW = manager.list()
        '''
  
        # Initialize screen and vehicle groups
        main_screen, main_ego_group, main_vehicle_group, main_ego_vehicle = init_draw()
        # Initialize the CAN communication
        main_can_bus_radar, main_can_bus_car, main_radar_dbc = init_com()
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
        while running:
            # Check for quit events
            for event in draw_get_events():
                # Check for quit event
                if event.type == QUIT:
                    # Exit the program
                    running = False

            # simulate object list
            process_sim_radar(main_radar_dbc, main_can_bus_radar, main_can_bus_car) 
            EgoMotion_data_main = process_sim_car(main_can_bus_car) 
            # Process the RX data
            #process_rx_radar(main_radar_dbc, main_can_bus_radar)
            #process_rx_car(main_can_bus_car)
			
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
            #update_vehicle_ai(main_screen, main_vehicle_group)

            # Draw the checkbox
            #draw_simple_checkbox(screen, 50, screen.get_height() - 100, 20, is_rays_enabled[0], white, toggle_rays, label="Enable Rays")
            
            # Use the menu state
            if is_rays_enabled[0]:
                draw_rays(main_screen, main_ego_vehicle, main_vehicle_group)
            
            draw_extraInfo(main_screen, EgoMotion_data_main, main_vehicle_group, ObjList_VIEW.ScanID)
            
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
    
