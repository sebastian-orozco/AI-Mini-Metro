from geometry.type import ShapeType

agent_play = True

# game
framerate = 60

# screen
screen_width = 1555
screen_height = 875
screen_color = (255, 255, 255)

# station
num_stations = 20
station_size = 30
station_capacity = 3
station_color = (0, 0, 0)
station_shape_type_list = [
    ShapeType.RECT,
    ShapeType.CIRCLE,
    ShapeType.TRIANGLE,
    ShapeType.CROSS,
]
station_passengers_per_row = 4
station_timer_size = station_size

# passenger
passenger_size = 5
passenger_color = (128, 128, 128)
passenger_spawning_start_step = 1
passenger_spawning_interval_step = int(0.75 * framerate) if agent_play else (10 * framerate)
passenger_display_buffer = 3 * passenger_size

# metro
num_metros = 3

metro_size = 30
metro_color = (200, 200, 200)
metro_capacity = 6
metro_speed_per_ms = (1500 / 1000) if agent_play else (150 / 1000) # pixels / ms
metro_passengers_per_row = 3

# path
num_paths = 3
path_width = 10
path_order_shift = 10

# button
button_color = (180, 180, 180)
button_size = 30

# path button
path_button_buffer = 20
path_button_dist_to_bottom = 50
path_button_start_left = 500
path_button_cross_size = 25
path_button_cross_width = 5

# text
score_font_size = 50
score_display_coords = (20, 20)

# parameters control the randomizaiton
seed = 4

time_limit = 1000 if agent_play else 10000