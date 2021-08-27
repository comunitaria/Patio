import time
import requests

import config

from time import sleep
from ina219 import INA219

ina1, ina2 = None, None
if not config.MOCK_SENSORS:
    ina1 = INA219(shunt_ohms=0.1, max_expected_amps = 0.6, address=0x40)
    ina2 = INA219(shunt_ohms=0.1, max_expected_amps = 0.6, address=0x41)

    ina1.configure(voltage_range=ina1.RANGE_16V, gain=ina1.GAIN_AUTO, bus_adc=ina1.ADC_128SAMP, shunt_adc=ina1.ADC_128SAMP)
    ina2.configure(voltage_range=ina2.RANGE_16V, gain=ina2.GAIN_AUTO, bus_adc=ina2.ADC_128SAMP, shunt_adc=ina2.ADC_128SAMP)




def get_sensor_value(sensor_id):
    if config.MOCK_SENSORS:
        return "0.5W"
    elif config.IOTA_WATT_URL:
        latest_value = "0"
        endpoint = ("/query?select=[time.iso,%s]&begin=M&end=s&"
                    "group=h&format=json&header=yes" % sensor_id)
        iota_url = config.IOTA_WATT_URL + endpoint
        response = requests.get(iota_url, auth=config.IOTA_WATT_AUTH)
        logs = response.json().get('data')
        if logs:
            date, latest_value = logs[-1]
        
        return str(latest_value)

    else:
        # Use the ID from SENSORS to get the real value
        try:
            if sensor_id == "0x40":
                return str(ina1.power())
            if sensor_id == "0x41":
                return str(ina2.power())
        except KeyboardInterrupt:
            print ("\nCtrl-C pressed.  Program exiting...")

