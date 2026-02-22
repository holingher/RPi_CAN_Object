import time
import threading
from pygame import QUIT, KEYDOWN
from init_com import init_com, deinit_com
from init_draw import init_draw, deinit_draw
from rx import (
    radar_view,
    ego_motion_data,
    process_CAN0_rx,
    process_CAN1_rx,
    radar_signal_status,
)
from tx import periodic_CAN0_tx_TimeSync_125ms_wrapper, process_CAN0_tx_60ms_wrapper
from draw_3D import draw_3d_vehicle, draw_3d_road, draw_3d_rays
from draw_2D import (
    draw_get_events,
    draw_own,
    draw_environment,
    draw_rays,
    draw_update,
    update_vehicle,
)
from menu import (
    draw_extraInfo,
    draw_exit_button,
    toggle_rays,
    is_rays_enabled,
    is_can_screen_enabled,
    draw_can_data_screen,
    handle_swipe_events,
    draw_swipe_instructions,
    is_radar_status_screen_enabled,
    draw_radar_status_screen,
)
from simulate import init_process_sim_radar, process_sim_car, process_sim_radar
from defines import *


class VisualizationThread(threading.Thread):
    """Separate thread for handling visualization and rendering"""

    def __init__(self):
        super().__init__(daemon=True)
        self.screen = None
        self.ego_group = None
        self.vehicle_group = None
        self.ego_vehicle = None
        self.running = True
        self.ego_motion_data = ego_motion_data
        self.frame_rate = fps  # Use fps from defines.py
        self.initialization_complete = threading.Event()

    def update_ego_motion_data(self, new_data):
        """Thread-safe method to update ego motion data"""
        self.ego_motion_data = new_data

    def stop(self):
        """Stop the visualization thread"""
        self.running = False

    def run(self):
        """Main visualization loop running in separate thread"""
        clock = None
        try:
            # Initialize pygame and screen in this thread to avoid GL context issues
            self.screen, self.ego_group, self.vehicle_group, self.ego_vehicle = (
                init_draw()
            )
            import pygame

            clock = pygame.time.Clock()
            self.initialization_complete.set()  # Signal that initialization is complete
        except Exception as e:
            print(f"Failed to initialize visualization: {e}")
            self.running = False
            self.initialization_complete.set()
            return

        print("Visualization thread started")

        while self.running:
            try:
                # Get all events for this frame
                events = draw_get_events()

                # Handle swipe gestures first
                handle_swipe_events(events)

                # Check for quit events
                for event in events:
                    if event.type == QUIT:
                        self.running = False
                        break
                    elif (
                        event.type == KEYDOWN
                        and hasattr(event, "key")
                        and event.key == 27
                    ):  # ESC
                        self.running = False
                        break

                if not self.running:
                    break

                # Check which screen to display
                if is_can_screen_enabled[0]:
                    # Draw CAN data screen
                    draw_can_data_screen(self.screen)

                    # Draw exit button only on CAN screen
                    draw_exit_button(
                        self.screen,
                        self.screen.get_width() - 110,
                        10,
                        100,
                        40,
                        gray,
                        self._exit_callback,
                        events,
                    )
                elif is_radar_status_screen_enabled[0]:
                    # Draw radar status screen
                    draw_radar_status_screen(self.screen, radar_signal_status, events)

                    # Draw exit button only on radar status screen
                    draw_exit_button(
                        self.screen,
                        self.screen.get_width() - 110,
                        10,
                        100,
                        40,
                        gray,
                        self._exit_callback,
                        events,
                    )
                else:
                    # Fill the screen with a color
                    draw_environment(self.screen)

                    # Draw own vehicle
                    draw_own(self.screen, self.ego_vehicle, self.ego_group)
                    # Update data for all vehicles
                    update_vehicle(self.screen, self.vehicle_group)
                    # Use the menu state
                    if is_rays_enabled[0]:
                        draw_rays(self.screen, self.ego_vehicle, self.vehicle_group)

                    # Draw the exit button (top-right corner, 100x40 size)
                    draw_exit_button(
                        self.screen,
                        self.screen.get_width() - 110,
                        10,
                        100,
                        40,
                        gray,
                        self._exit_callback,
                        events,
                    )

                    # Draw vehicle and radar info
                    draw_extraInfo(
                        self.screen,
                        self.ego_motion_data,
                        self.vehicle_group,
                        radar_view.scan_id,
                    )

                    # Draw swipe instructions
                    draw_swipe_instructions(
                        self.screen, is_can_screen=False, is_radar_status_screen=False
                    )

                # Update the display
                draw_update()

                # Control frame rate
                if clock:
                    clock.tick(self.frame_rate)
                else:
                    time.sleep(1.0 / self.frame_rate)

            except Exception as e:
                print(f"Visualization thread error: {e}")
                # Continue running even if there's an error
                time.sleep(0.1)

        print("Visualization thread stopped")

        # Clean up pygame resources in this thread
        try:
            deinit_draw()
        except Exception as e:
            print(f"Error during pygame cleanup: {e}")

    def _exit_callback(self):
        """Internal exit callback for visualization thread"""
        self.running = False


def main():
    """Optimized main function with improved data type handling and threaded visualization"""
    try:
        EgoMotion_data_main = ego_motion_data

        # Initialize the CAN communication
        main_can_bus_CAN0, main_can_bus_CAN1, main_radar_dbc = init_com()

        # Set display flags based on platform
        if not is_raspberrypi():
            init_process_sim_radar()

        # Create and start visualization thread
        viz_thread = VisualizationThread()
        viz_thread.start()
        print("Starting visualization thread...")

        # Wait for visualization thread to complete initialization
        if not viz_thread.initialization_complete.wait(timeout=10.0):
            print("Visualization thread failed to initialize within timeout")
            return

        if not viz_thread.running:
            print("Visualization thread failed to start")
            return

        print("Visualization thread initialized successfully")

        # Create stop events for threads
        stop_event_periodic_CAN0_tx_60ms = threading.Event()
        stop_event_periodic_CAN0_tx_TimeSync_125ms = threading.Event()

        # Start TX thread with wrapper function using existing CAN bus
        periodic_CAN0_tx_60ms_thread = threading.Thread(
            target=process_CAN0_tx_60ms_wrapper,
            args=(60, stop_event_periodic_CAN0_tx_60ms, main_can_bus_CAN0),
        )
        periodic_CAN0_tx_60ms_thread.daemon = True
        periodic_CAN0_tx_60ms_thread.start()
        print("TX thread started - sending CAN messages every 60ms")

        # Start 125ms periodic thread
        periodic_CAN0_tx_TimeSync_125ms_thread = threading.Thread(
            target=periodic_CAN0_tx_TimeSync_125ms_wrapper,
            args=(125, stop_event_periodic_CAN0_tx_TimeSync_125ms, main_can_bus_CAN1),
        )
        periodic_CAN0_tx_TimeSync_125ms_thread.daemon = True
        periodic_CAN0_tx_TimeSync_125ms_thread.start()
        print("125ms periodic thread started")

        # Main CAN processing loop
        running = True

        while running and viz_thread.is_alive():
            # Check if visualization thread requested exit
            if not viz_thread.running:
                running = False
                break

            # Set display flags based on platform
            if is_raspberrypi():
                ##### CAN1 - Car #####
                # Process the RX data
                EgoMotion_data_main = process_CAN1_rx(main_can_bus_CAN1)
                # Process the TX data
                # not required as no data to send
                # process_CAN1_tx(main_can_bus_CAN1)

                ##### CAN0 - Radar #####
                # TX is now handled by separate process - removed from main loop
                # Process the RX data
                process_CAN0_rx(main_radar_dbc, main_can_bus_CAN0)

                # Update visualization thread with new ego motion data
                viz_thread.update_ego_motion_data(EgoMotion_data_main)
            else:
                # simulate object list
                process_sim_radar(main_radar_dbc, main_can_bus_CAN0, main_can_bus_CAN1)
                EgoMotion_data_main = process_sim_car(main_can_bus_CAN1)

                # Update visualization thread with new ego motion data
                viz_thread.update_ego_motion_data(EgoMotion_data_main)

            time.sleep(0.0005)

        # Clean shutdown
        print("Shutting down...")
        viz_thread.stop()
        stop_event_periodic_CAN0_tx_60ms.set()
        stop_event_periodic_CAN0_tx_TimeSync_125ms.set()
        periodic_CAN0_tx_60ms_thread.join()
        periodic_CAN0_tx_TimeSync_125ms_thread.join()

        # Wait for visualization thread to finish
        if viz_thread.is_alive():
            viz_thread.join(timeout=1.0)
    except KeyboardInterrupt:
        print("Interrupted by user")
        # Clean shutdown on interrupt
        try:
            viz_thread.stop()
            if viz_thread.is_alive():
                viz_thread.join(timeout=1.0)
        except:
            pass
        stop_event_periodic_CAN0_tx_60ms.set()
        stop_event_periodic_CAN0_tx_TimeSync_125ms.set()
        periodic_CAN0_tx_60ms_thread.join()
        periodic_CAN0_tx_TimeSync_125ms_thread.join()
        deinit_com()


if __name__ == "__main__":
    main()
