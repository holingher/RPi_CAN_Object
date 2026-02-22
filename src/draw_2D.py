import math
from pygame import Surface as draw_2D_Surface
from pygame import display as pygame_display
from pygame import event as pygame_event
from pygame import draw as pygame_draw
from pygame import font as pygame_font
from pygame import QUIT, SRCALPHA
from pygame.sprite import Group
from rx import radar_view, ObjectDrawData
from defines import black, white, yellow, gray, red, green
from defines import EgoVehicle, Vehicle
from defines import fov_angle, ray_count, ray_color_hit, ray_color_no_hit
from defines import INVALID_OBJECT_ID
from rx import radar_view, ObjectDrawData, can_sniffer

_cached_fonts = {}
_ray_cache = {}
_ray_surface = None
_cached_ray_angles = None


def _get_font(size):
    if size not in _cached_fonts:
        _cached_fonts[size] = pygame_font.Font(pygame_font.get_default_font(), size)
    return _cached_fonts[size]


def _calculate_ray_angles():
    global _cached_ray_angles
    if _cached_ray_angles is None:
        start_angle = -fov_angle * 1.5
        angle_step = fov_angle / (ray_count - 1)
        _cached_ray_angles = [
            math.radians(start_angle + i * angle_step) for i in range(ray_count)
        ]
    return _cached_ray_angles


########################################################################################
def draw_update():
    pygame_display.update()


########################################################################################
def draw_get_events():
    # Get the list of events
    return pygame_event.get()


########################################################################################
def draw_environment(screen: draw_2D_Surface):
    # draw the background
    screen.fill(black)
    # draw the road
    # pygame.draw.rect(screen, black, road)

    # draw the edge markers
    # pygame.draw.rect(screen, yellow, left_edge_marker)
    # pygame.draw.rect(screen, yellow, right_edge_marker)

    # draw the lane markers
    # lane_marker_move_y += speed * 2
    # if lane_marker_move_y >= marker_height * 2:
    #    lane_marker_move_y = 0
    # for y in range(marker_height * -2, height, marker_height * 2):
    #    pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
    #    pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))


########################################################################################
# Function to calculate rays based on FOV
def calculate_rays(screen: draw_2D_Surface, ego_vehicle: EgoVehicle):
    rays = []
    angles = _calculate_ray_angles()
    centerx = ego_vehicle.rect.centerx
    centery = ego_vehicle.rect.centery
    screen_w = screen.get_width()
    screen_h = screen.get_height()

    for angle in angles:
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        if cos_a > 0:
            max_x = screen_w - centerx
        else:
            max_x = -centerx
        if sin_a > 0:
            max_y = screen_h - centery
        else:
            max_y = -centery
        ray_length_x = max_x / cos_a if cos_a != 0 else float("inf")
        ray_length_y = max_y / sin_a if sin_a != 0 else float("inf")
        ray_length = min(ray_length_x, ray_length_y)
        end_x = centerx + ray_length * cos_a
        end_y = centery + ray_length * sin_a
        rays.append(((centerx, centery), (end_x, end_y)))

    return rays


########################################################################################
def draw_rays(screen: draw_2D_Surface, ego_vehicle: EgoVehicle, vehicle_group: Group):
    # Create a transparent surface for drawing rays
    ray_surface = draw_2D_Surface(
        screen.get_size(), SRCALPHA
    )  # Use SRCALPHA for transparency

    # Calculate and draw rays for the ego vehicle's field of view
    rays = calculate_rays(screen, ego_vehicle)
    # Check for collisions along each ray
    for ray_start, ray_end in rays:
        hit_point = None  # Initialize the hit point as None
        for vehicle in vehicle_group:
            if vehicle.rect.clipline(
                ray_start, ray_end
            ):  # Check if the ray intersects a vehicle
                # Get the intersection point
                hit_point = vehicle.rect.clipline(ray_start, ray_end)
                break

        # Draw the ray
        if hit_point:
            # Draw the ray only up to the collision point
            pygame_draw.line(
                ray_surface, ray_color_hit, ray_start, hit_point[0], 2
            )  # Green ray for collision
        else:
            # Draw the full ray if no collision
            pygame_draw.line(ray_surface, ray_color_no_hit, ray_start, ray_end, 2)
    # Blit the transparent surface onto the main screen
    screen.blit(ray_surface, (0, 0))


########################################################################################
def draw_own(screen: draw_2D_Surface, ego_vehicle: EgoVehicle, ego_group: Group):
    ego_group.draw(screen)
    screen.blit(ego_vehicle.image, ego_vehicle.rect)
    font = _get_font(14)
    text = font.render(ego_vehicle.label, True, white)
    text_rect = text.get_rect(
        center=(ego_vehicle.rect.centerx, ego_vehicle.rect.top - 10)
    )
    screen.blit(text, text_rect)


########################################################################################
def draw_vehicle(screen: draw_2D_Surface, veh: Vehicle):
    screen.blit(source=veh.image, dest=veh.rect)
    font = _get_font(14)
    text = font.render(veh.label + " " + str(veh.dataConfidence), True, white)
    text_rect = text.get_rect(center=(veh.rect.centerx, veh.rect.top - 10))
    screen.blit(text, text_rect)
    if veh.rect.top >= screen.get_height():
        veh.kill()


########################################################################################


def update_vehicle(screen: draw_2D_Surface, vehicle_group: Group):
    if radar_view.msg_counter > 0:
        vehicle_map = {v.id: v for v in vehicle_group}
        for object_entry in radar_view.object_list_for_draw:
            if object_entry.object_id != INVALID_OBJECT_ID:
                obj_id = object_entry.object_id
                if obj_id in vehicle_map:
                    veh = vehicle_map[obj_id]
                    veh.kill()
                veh = Vehicle(
                    id_object=obj_id,
                    color=(
                        yellow
                        if object_entry.class_type == 0
                        else red
                        if object_entry.class_type == 1
                        else green
                        if object_entry.class_type == 2
                        else gray
                    ),
                    x=int(object_entry.lat_pos),
                    y=int(object_entry.lgt_pos),
                    width=int(object_entry.data_width),
                    height=int(object_entry.data_len),
                    speed=object_entry.lgt_velocity,
                    dataConfidence=object_entry.data_conf,
                    label=(
                        "Unknown"
                        if object_entry.class_type == 0
                        else "Car"
                        if object_entry.class_type == 1
                        else "Bicycle"
                        if object_entry.class_type == 2
                        else "Pedestrian"
                    ),
                )
                veh.rect.y += veh.speed
                veh.update(
                    veh.id,
                    veh.rect.x,
                    veh.rect.y,
                    veh.width,
                    veh.height,
                    veh.speed,
                    veh.dataConfidence,
                )
                vehicle_group.add(veh)
                draw_vehicle(screen, veh)
    vehicle_group.draw(screen)


def update_vehicle_ai(
    screen: draw_2D_Surface, ObjList_VIEW_local, vehicle_group: Group
):
    vehicle: Vehicle
    """
    Updates the vehicles in the vehicle group based on the object list for drawing.
    """
    if ObjList_VIEW_local.MsgCntr > 0:
        # Create a mapping of object IDs to vehicles for quick lookup
        vehicle_map = {vehicle.id: vehicle for vehicle in vehicle_group}

        for object_entry in ObjList_VIEW_local.object_list_for_draw:
            if object_entry.object_id != INVALID_OBJECT_ID:  # Ensure object_id is valid
                # Check if the vehicle already exists in the group
                if object_entry.object_id in vehicle_map:
                    vehicle = vehicle_map[object_entry.object_id]
                    # Update the existing vehicle's attributes
                    vehicle.rect.x = int(object_entry.lat_pos)
                    vehicle.rect.y = int(object_entry.lgt_pos)
                    vehicle.width = int(object_entry.data_width)
                    vehicle.height = int(object_entry.data_len)
                    vehicle.speed = object_entry.lgt_velocity
                    vehicle.dataConfidence = object_entry.data_conf
                    vehicle.label = (
                        "Unknown"
                        if object_entry.class_type == 0
                        else "Car"
                        if object_entry.class_type == 1
                        else "Bicycle"
                        if object_entry.class_type == 2
                        else "Pedestrian"
                    )
                    vehicle.image.fill(
                        yellow
                        if object_entry.class_type == 0
                        else red
                        if object_entry.class_type == 1
                        else green
                        if object_entry.class_type == 2
                        else gray
                    )
                else:
                    # Create a new vehicle if it doesn't exist
                    vehicle = Vehicle(
                        id_object=object_entry.object_id,
                        color=(
                            yellow
                            if object_entry.class_type == 0
                            else red
                            if object_entry.class_type == 1
                            else green
                            if object_entry.class_type == 2
                            else gray
                        ),
                        x=int(object_entry.lat_pos),
                        y=int(object_entry.lgt_pos),
                        width=int(object_entry.data_width),
                        height=int(object_entry.data_len),
                        speed=object_entry.lgt_velocity,
                        dataConfidence=object_entry.data_conf,
                        label=(
                            "Unknown"
                            if object_entry.class_type == 0
                            else "Car"
                            if object_entry.class_type == 1
                            else "Bicycle"
                            if object_entry.class_type == 2
                            else "Pedestrian"
                        ),
                    )
                    vehicle_group.add(vehicle)  # Add the new vehicle to the group

                # Draw the vehicle
                draw_vehicle(screen, vehicle)

    # Draw all vehicles in the group
    vehicle_group.draw(screen)
