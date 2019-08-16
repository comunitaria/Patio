import codecs
import json
import time
import requests
import threading
import signal
from datetime import datetime


class EnergyMonitor(object):
    """
    """

    def __init__(self, community_id):
        self.community_id = community_id
        self.stop = False

    def generation_monitor(self):
        """
            Periodically gets measure from generation smart meter,
            sending to MAM
        """
        while not self.stop:
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            # TODO: Get measure from sensor (format?)
            data = {"amount": 0.5,  # Amount of generation at this moment
                    "datetime": now,
                    "type": "generated",
                    "community_id": self.community_id
                    }
            
            response = requests.get("http://localhost:3000",
                                    params={"message": str(data)})
            response = response.json()
            msg_root = response['root']
            data.update({'mam_address': msg_root})

            # TODO send amount and root to SaaS
            # response = requests.post("https://back.comunitaria.com/...", json=data)

            time.sleep(5)  # Every 5 seconds

    def consuming_monitor(self):
        """
            Gets metrics from common places and from each
            neighbour sensor to measure consuming.
        """
        while not self.stop:
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            c_type = "consumed"

            # TODO: Get measures from building sensors

            # for sensor in sensors:
            data = {"amount": 0.5,  # Amount being consumed at this moment
                    "datetime": now,
                    "sensor_id": "sensor.id",  # Common places or neighbour id
                    "type": c_type,
                    "community_id": self.community_id
                    }

            response = requests.get("http://localhost:3000",
                                    params={"message": str(data)})
            response = response.json()
            msg_root = response['root']
            data.update({'mam_address': msg_root})

            # TODO send amount and root to SaaS
            # response = requests.post("https://back.comunitaria.com/...", json=data)

            time.sleep(5)  # Every 5 seconds

    def stop_process(self):
        def stop_handler(signum, frame):
            self.stop = True
        return stop_handler

    def run(self):
        signal.signal(signal.SIGINT, self.stop_process())
        signal.signal(signal.SIGTERM, self.stop_process())

        t1 = threading.Thread(target=self.generation_monitor)
        t2 = threading.Thread(target=self.autoconsuming_monitor)
        t1.start()
        t2.start()
        print("Started...")

        t1.join()
        t2.join()
        print("Stopped")

if __name__ == '__main__':
    em = EnergyMonitor('1')
    em.run()

