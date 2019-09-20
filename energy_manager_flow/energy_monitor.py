import codecs
import json
import time
import requests
import threading
import signal
import sensors_data
from datetime import datetime
import config


datetime_format = "%Y-%m-%d %H:%M:%S+00:00"

class EnergyMonitor(object):
    """
    """

    def __init__(self, community_token):
        self.community_token = community_token
        self.stop = False

    def generation_monitor(self):
        """
            Periodically gets measure from generation smart meter,
            sending to MAM
        """
        while not self.stop:
            now = datetime.utcnow().strftime(datetime_format)
            # Get measure from sensor
            value = sensors_data.get_sensor_value("generation_1")
            data = {"amount": value,  # Amount of generation at this moment
                    "datetime": now,
                    "type": "generated",
                    "token": self.community_token
                    }
            
            response = requests.get("http://localhost:3000",
                                    params={"message": str(data)})
            response = response.json()
            msg_root = response['root']
            data.update({'mam_address': msg_root})

            # Send data to SaaS
            response = requests.post("%s/energy/save" % config.base_backend_url,
                                     json=data)

            if not response.ok:
                print(response.content)

            time.sleep(5)  # Every 5 seconds

    def consuming_monitor(self):
        """
            Gets metrics from common places and from each
            neighbour sensor to measure consuming.
        """
        while not self.stop:
            now = datetime.utcnow().strftime(datetime_format)
            c_type = "consumed"

            # Get measures from building and neighbours sensors
            for sensor in sensors_data.SENSORS["consumption"]:
                value = sensors_data.get_sensor_value(sensor)
                data = {"amount": value,  # Amount being consumed at this moment
                        "datetime": now,
                        "sensor_id": sensor,  # Common places or neighbour id
                        "type": c_type,
                        "token": self.community_token
                        }

                response = requests.get("http://localhost:3000",
                                        params={"message": str(data)})
                response = response.json()
                msg_root = response['root']
                data.update({'mam_address': msg_root})

                # Send data to SaaS
                response = requests.post("%s/energy/save" % config.base_backend_url,
                                         json=data)
                if not response.ok:
                    print(response.content)

            time.sleep(5)  # Every 5 seconds

    def stop_process(self):
        def stop_handler(signum, frame):
            self.stop = True
        return stop_handler

    def run(self):
        signal.signal(signal.SIGINT, self.stop_process())
        signal.signal(signal.SIGTERM, self.stop_process())

        t1 = threading.Thread(target=self.generation_monitor)
        t2 = threading.Thread(target=self.consuming_monitor)
        t1.start()
        t2.start()
        print("Started...")

        t1.join()
        t2.join()
        print("Stopped")

if __name__ == '__main__':
    em = EnergyMonitor('1')
    em.run()

