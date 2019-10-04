import time

import config

from time import sleep
from ina219 import INA219

ina1, ina2 = None, None
if not config.MOCK_SENSORS:
    ina1 = INA219(shunt_ohms=0.1, max_expected_amps = 0.6, address=0x40)
    ina2 = INA219(shunt_ohms=0.1, max_expected_amps = 0.6, address=0x41)

    ina1.configure(voltage_range=ina1.RANGE_16V, gain=ina1.GAIN_AUTO, bus_adc=ina1.ADC_128SAMP, shunt_adc=ina1.ADC_128SAMP)
    ina2.configure(voltage_range=ina2.RANGE_16V, gain=ina2.GAIN_AUTO, bus_adc=ina2.ADC_128SAMP, shunt_adc=ina2.ADC_128SAMP)

# This dict is fixed. But in the future it'll be get from SaaS API to get data
# for the specific community
# In the case of 'neighbour_X', X is the UserCommunity ID from backend
SENSORS = {"generation": {"generation_1": ""},
           "consumption": {"common_place_1": "0x40",  # value should be the addr of the sensor
                           # 4 is the id of demo usercommunity for Community 1
                           "neighbour_4": "0x41"
                           },
           }


def get_sensor_value(sensor_id):
    if config.MOCK_SENSORS:
        return "0.5W"
    else:
        # Use the ID from SENSORS to get the real value
        try:
            if sensor_id == "0x40":
                return str(ina1.power())
            if sensor_id == "0x41":
                return str(ina2.power())
        except KeyboardInterrupt:
            print ("\nCtrl-C pressed.  Program exiting...")

