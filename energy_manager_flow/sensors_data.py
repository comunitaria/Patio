import time

import config

# This dict is fixed. But in the future it'll be get from SaaS API to get data
# for the specific community
SENSORS = {"generation": {"generation_1": ""},
           "consumption": {"common_place_1": "",  # value should be the addr of the sensor
                           "neighbour_1": ""
                           },
           }


def get_sensor_value(sensor_id):
    if config.MOCK_SENSORS:
        return "0.5W"
    else:
        pass
        # Use the ID from SENSORS to get the real value

