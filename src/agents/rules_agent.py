from agents.agent import Agent
import random
import math


class RulesBasedAgent(Agent):
    def generate_paths(self):
        # init planned paths
        self.planned_paths = [[] for _ in range(self.num_paths)]

        # rules:
        # 1. connect stations to nearby stations
        # 2. lines should have different station types
        # 3. all stations must be connected to a line

        # Step 1: collect stats
        total_stations = self.mediator.num_stations
        total_lines = self.mediator.num_metros
        total_types = {station.id.split('.')[1] for station in self.all_stations}  # {'RECT', 'CIRCLE', 'TRIANGLE'}
        station_map = {station_type: [] for station_type in total_types}

        # map stations by type
        for station in self.all_stations:
            station_type = station.id.split('.')[1]
            station_map[station_type].append(station)

        stations_per_line = total_stations // total_lines
        unassigned_stations = set(self.all_stations)  
        lines = []

        # Step 2: create paths for each line
        for _ in range(total_lines):
            line_path = []
            line_types = set()

            # 2.1: pick random unassigned station
            if not unassigned_stations:
                break  
            current_station = random.choice(list(unassigned_stations))
            line_path.append(current_station)
            line_types.add(current_station.id.split('.')[1])
            unassigned_stations.remove(current_station)

            # 2.2: connect to nearest station 
            while len(line_path) < stations_per_line and unassigned_stations:
                closest_station = self.find_closest(current_station, unassigned_stations)
                line_path.append(closest_station)
                line_types.add(closest_station.id.split('.')[1])
                current_station = closest_station
                unassigned_stations.remove(closest_station)

            # 2.3: ensure all types are represented in the line
            missing_types = total_types - line_types
            for type in missing_types:
                if station_map[type]:
                    closest_station = self.find_closest(current_station, station_map[type])
                    line_path.append(closest_station)
                    if closest_station in unassigned_stations:
                        unassigned_stations.remove(closest_station)

            lines.append(line_path)

        # Step 3: handle leftover unassigned stations
        for station in unassigned_stations:
            # connect remaining unassigned stations to the nearest assigned station
            assigned_stations = [s for line in lines for s in line]
            closest_assigned = self.find_closest(station, assigned_stations)
            if closest_assigned:
                for line in lines:
                    if closest_assigned in line:
                        line.append(station)
                        break

        # Step 4: assign paths to planned_paths
        self.planned_paths = [self.order_stations(line) for line in lines]