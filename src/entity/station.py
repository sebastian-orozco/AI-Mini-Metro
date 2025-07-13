from __future__ import annotations

import pygame
from shortuuid import uuid  # type: ignore

from config import station_capacity, station_passengers_per_row, station_size, station_timer_size
from entity.holder import Holder
from geometry.point import Point
from geometry.shape import Shape


class Station(Holder):
    def __init__(self, shape: Shape, position: Point) -> None:
        super().__init__(
            shape=shape,
            capacity=station_capacity,
            id=f"Station-{uuid()}-{shape.type}",
        )
        self.size = station_size
        self.position = position
        self.passengers_per_row = station_passengers_per_row

        # track time at max capacity
        self.time_at_max_capacity = 0  # in milliseconds

    def __eq__(self, other: Station) -> bool:
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    # check if the station is at max capacity
    def is_full(self) -> bool:
        return len(self.passengers) >= self.capacity

    # update the time at max capacity
    def increment_time_at_max_capacity(self, dt_ms: int) -> None:
        if self.is_full():
            self.time_at_max_capacity += dt_ms
        else:
            self.time_at_max_capacity = 0  # reset if no longer at max capacity

    # reset the timer explicitly (if needed elsewhere)
    def reset_time_at_max_capacity(self) -> None:
        self.time_at_max_capacity = 0

    def get_fill_progress(self, max_capacity_time_limit_ms: int) -> float:
        """
        Calculate the proportion of the max-capacity time limit that has elapsed.
        Returns a value between 0 (no fill) and 1 (completely filled).
        """
        return min(self.time_at_max_capacity / max_capacity_time_limit_ms, 1.0)

    def render_visual_timer(self, screen: pygame.Surface, max_capacity_time_limit_ms: int):
        """
        Render a filling circle around the station to indicate time at max capacity.
        """
        if self.time_at_max_capacity > 0:  # Only draw if time is being tracked
            progress = self.get_fill_progress(max_capacity_time_limit_ms)
            
            # Calculate the dynamic color based on progress
            start_color = 200  # Light gray
            end_color = 0      # Black
            color_value = round(start_color + (end_color - start_color) * progress)
            color = (color_value, color_value, color_value)  # Grayscale color
            
            start_angle = -90  # Start at the top of the circle
            end_angle = start_angle + progress * 360  # Proportional fill

            # Adjusted radius to start farther from the station
            center = (self.position.left, self.position.top)
            radius = self.size + station_timer_size  # Offset added to the station size
            arc_thickness = 10  # Thickness of the arc
            # color = (255, 0, 0)  # Red for warning

            # Draw the arc
            for _ in range(10):
                pygame.draw.arc(
                    screen,
                    color,
                    (center[0] - radius, center[1] - radius, radius * 2, radius * 2),
                    start_angle * (3.14 / 180),  # Convert to radians
                    end_angle * (3.14 / 180),  # Convert to radians
                    arc_thickness  # Arc width
                )
