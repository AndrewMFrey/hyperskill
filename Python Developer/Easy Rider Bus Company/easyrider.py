import json
import re
from itertools import combinations


class EasyRider:
    def __init__(self, json_data: str):
        """
        Parses through json_data and validates input data.
        :param json_data: Company data from Easy Rider Bus Company in JSON format
        """
        self.json_data = json.loads(json_data)
        self.error_dict = {
            "bus_id": 0,
            "stop_id": 0,
            "stop_name": 0,
            "next_stop": 0,
            "stop_type": 0,
            "a_time": 0
        }
        self.bus_set = set()
        self.bus_line_dict = {}
        self.bus_start_dict = {}
        self.bus_final_dict = {}
        self.bus_all_stops_dict = {}
        self.prev_stop_time_dict = {}
        self.line_error_status = {}
        self.normal_stops = set()
        self.on_demand_stops = set()

    def validate_input(self):
        for stop in self.json_data:
            self.validate_bus_id(stop)
            self.validate_stop_id(stop)
            self.validate_stop_name(stop)
            self.validate_next_stop(stop)
            self.validate_stop_type(stop)
            self.validate_a_time(stop)
        self.print_errors()

    def validate_bus_id(self, stop):
        if type(stop.get("bus_id")) is int:
            return
        self.error_dict["bus_id"] += 1

    def validate_stop_id(self, stop):
        if type(stop.get("stop_id")) is int:
            return
        self.error_dict["stop_id"] += 1

    def validate_stop_name(self, stop):
        if re.match(r"([A-Z][a-z]+\s)+(Road|Avenue|Boulevard|Street)$", stop.get("stop_name")):
            return
        self.error_dict["stop_name"] += 1

    def validate_next_stop(self, stop):
        if type(stop.get("next_stop")) is int:
            return
        self.error_dict["next_stop"] += 1

    def validate_stop_type(self, stop):
        if re.match(r"^(S|O|F|)$", stop.get("stop_type")):
            return
        self.error_dict["stop_type"] += 1

    def validate_a_time(self, stop):
        if re.match(r"[0-2][0-9]:[0-5][0-9]$", stop.get("a_time")):
            return
        self.error_dict["a_time"] += 1

    def print_errors(self):
        print("Format validation: {} errors".format(sum(self.error_dict.values())))
        print("stop_name: {}".format(self.error_dict.get("stop_name")))
        print("stop_type: {}".format(self.error_dict.get("stop_type")))
        print("a_time: {}".format(self.error_dict.get("a_time")))

    def bus_line_information(self):
        for stop in self.json_data:
            if stop.get("bus_id") in self.bus_line_dict:
                self.bus_line_dict[stop.get("bus_id")] += 1
            else:
                self.bus_line_dict[stop.get("bus_id")] = 1
        self.print_bus_line_information()

    def print_bus_line_information(self):
        print("Line names and number of stops:")
        for bus in self.bus_line_dict:
            print(f"bus_id: {bus}, stops: {self.bus_line_dict.get(bus)}")

    def stop_information(self):
        for stop in self.json_data:
            current_stop = stop.get("bus_id")
            if current_stop not in self.bus_set:
                self.bus_set.add(current_stop)
            if stop.get("stop_type") == "S":
                if current_stop in self.bus_start_dict:
                    print(f"There are multiple start stops for the line: {current_stop}")
                else:
                    self.bus_start_dict[current_stop] = stop.get("stop_name")
            elif stop.get("stop_type") == "F":
                if current_stop in self.bus_final_dict:
                    print(f"There are multiple end stops for the line: {current_stop}")
                else:
                    self.bus_final_dict[current_stop] = stop.get("stop_name")
            if current_stop in self.bus_all_stops_dict:
                self.bus_all_stops_dict[current_stop].add(stop.get("stop_name"))
            else:
                self.bus_all_stops_dict[current_stop] = {stop.get("stop_name")}

        for key in sorted(list(self.bus_set)):
            if key not in self.bus_start_dict and key not in self.bus_final_dict:
                print(f"There is no start or end stop for the line: {key}.")
                return
            elif key not in self.bus_start_dict:
                print(f"There is no start stop for the line: {key}.")
                return
            elif key not in self.bus_final_dict:
                print(f"There is no end stop for the line: {key}.")
                return

        start_set = set()
        for start in sorted(self.bus_start_dict):
            start_set.add(self.bus_start_dict.get(start))
        start_list = sorted(list(start_set))
        print(f"Start stops: {len(start_list)} {start_list}")

        transfer_list = [self.bus_all_stops_dict[key] for key in self.bus_all_stops_dict]
        full_intersection = set()
        for combo in combinations(range(len(transfer_list)), 2):
            intersection = transfer_list[combo[0]].copy()
            for i in combo[1:]:
                intersection &= transfer_list[i]
            full_intersection |= intersection
        transfer_list = sorted(list(full_intersection))
        print(f"Transfer stops: {len(transfer_list)} {transfer_list}")

        final_set = set()
        for final in sorted(self.bus_final_dict):
            final_set.add(self.bus_final_dict.get(final))
        final_list = sorted(list(final_set))
        print(f"Finish stops: {len(final_list)} {final_list}")

    def validate_bus_arrivals(self):
        print("Arrival time test:")
        for stop in self.json_data:
            current_stop = stop.get("bus_id")
            if current_stop not in self.prev_stop_time_dict:
                self.prev_stop_time_dict[current_stop] = ""
                self.line_error_status[current_stop] = False
            if self.line_error_status[current_stop]:
                pass
            else:
                stop_list = [self.prev_stop_time_dict[current_stop], stop.get("a_time")]
                if stop_list == sorted(stop_list):
                    self.prev_stop_time_dict[current_stop] = stop.get("a_time")
                else:
                    print(f"""bus_id line {stop.get("bus_id")}: wrong time on {stop.get("stop_name")}""")
                    self.line_error_status[current_stop] = True
        if True in self.line_error_status.values():
            pass
        else:
            print("OK")

    def validate_on_demand(self):
        print("On demand stops test:")
        for stop in self.json_data:
            if stop.get("stop_type") == "O":
                self.on_demand_stops.add(stop.get("stop_name"))
            else:
                self.normal_stops.add(stop.get("stop_name"))
        intersecting_stops = sorted(list(self.on_demand_stops & self.normal_stops))
        if intersecting_stops:
            print(f"Wrong stop type: {intersecting_stops}")
        else:
            print("OK")


er = EasyRider(input())
er.validate_on_demand()