import logging
import json
import time
import requests
import threading
import signal
import sensors_data
from datetime import datetime
import config

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s : %(levelname)s :%(message)s',
                    filename="energy_monitoring.log")

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
            sending to chosen DLT
        """
        while not self.stop:
            time.sleep(config.WAITING_TIME)  # Every 5 seconds
            
            date = datetime.utcnow().strftime(datetime_format)
            # Get measure from sensors
            sensors = config.SENSORS["generation"]
            for sensor in sensors:
                value_date, value = sensors_data.get_sensor_value(
                    sensors[sensor])

                if value_date is not None:
                    date = datetime.strptime(value_date, '%Y-%m-%dT%H:%M:%S')
                    date = date.strftime(datetime_format)
                
                if value is None:
                    # Connection issues, continue and retry later
                    continue

                if float(value.replace(config.power_unit, '').strip()) <= 0.001:
                    continue

                data = {"amount": value,  # Amount of generation at this moment
                        "datetime": date,
                        "type": "generated",
                        "sensor_id": sensor,
                        "community_unique_id": config.community_unique_id
                        }
                
                saved_log_id = self.save_to_DLT(data)

                data.update({'dlt_address': saved_log_id,
                            'token': self.community_token})

                # Send data to SaaS
                response = requests.post("%s/energy/save" %
                                         config.base_backend_url,
                                         json=data)

                if not response.ok:
                    logging.error(response.content)

    def consuming_monitor(self):
        """
            Gets metrics from common places and from each
            neighbour sensor to measure consuming.
        """
        while not self.stop:
            time.sleep(config.WAITING_TIME)  # Every 5 seconds
            
            date = datetime.utcnow().strftime(datetime_format)
            c_type = "consumed"

            # Get measures from building and neighbours sensors
            sensors = config.SENSORS["consumption"]
            for sensor in sensors:
                value_date, value = sensors_data.get_sensor_value(
                    sensors[sensor])
                
                if value_date is not None:
                    date = datetime.strptime(value_date, '%Y-%m-%dT%H:%M:%S')
                    date = date.strftime(datetime_format)
                
                if value is None:
                    # Connection issues, continue and try later
                    logging.info("Null value, retrying later")
                    continue

                if float(value.replace(config.power_unit, '').strip()) <= 0.001:
                    logging.info("Value lower than 0.001, ignoring")
                    continue

                data = {"amount": value,
                        "datetime": date,
                        "sensor_id": sensor,  # Common places or neighbour id
                        "type": c_type,
                        "community_unique_id": config.community_unique_id
                        }

                saved_log_id = self.save_to_DLT(data)

                data.update({'dlt_address': saved_log_id,
                             'token': self.community_token})

                # Send data to SaaS
                response = requests.post("%s/energy/save" %
                                         config.base_backend_url,
                                         json=data)
                logging.info(response.json())
                if not response.ok:
                    logging.error(response.content)

    def stop_process(self):
        def stop_handler(signum, frame):
            self.stop = True
        return stop_handler

    def save_to_DLT(self, data):
        saved_log_id = ""
        if config.IOTA:
            response = requests.get("http://localhost:3000",
                                    params={"message": json.dumps(data)})
            response = response.json()
            saved_log_id = response['root']
        else:  # Zenroom
            response = requests.post(
                "http://localhost:3300/api/patio_save_energy",
                json={"data": {"dataToStore": data}
                      }
                                     )
            response = response.json()
            saved_log_id = response['log_tag']

        return saved_log_id

    def run(self):
        signal.signal(signal.SIGINT, self.stop_process())
        signal.signal(signal.SIGTERM, self.stop_process())

        t1 = threading.Thread(target=self.generation_monitor)
        t2 = threading.Thread(target=self.consuming_monitor)
        t1.start()
        t2.start()
        logging.info("Started monitoring...")

        t1.join()
        t2.join()
        logging.info("Stopped monitoring")


if __name__ == '__main__':
    em = EnergyMonitor('1')
    em.run()
