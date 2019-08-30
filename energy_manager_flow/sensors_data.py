import time

MODE = "testing"

# This dict is fixed. But eventually could be updateable remotely
SENSORS = {"generation": {"generation_1": "ID"},
           "consumption": {"common_place_1": "",
                            "neighbour_1": ""
                            },
           }


def get_sensor_value(sensor_id):
    if MODE == "testing":
        return "0.5W"
    else:
        pass
        # Use the ID from SENSORS to get the real value

