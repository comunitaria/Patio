import signal
import requests
import time
from multiprocessing import Process
from energy_monitor import EnergyMonitor
import config


if __name__ == '__main__':
    """
        Starts the EnergyMonitor process, monitoring
        generated and consumed energy inside a community.
        Also, every some seconds, it checks pending messages
        from SaaS.
    """
    community_token = config.community_token
    stop = False

    em = EnergyMonitor(community_token)
    em_p = Process(target=em.run)

    def stop_handler(signum, frame):
        global stop
        stop = True
        em_p.stop = True

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    em_p.start()

    while not stop:
        # Enhancement: Get pending messages from SaaS
        time.sleep(3)
    

    em_p.join()

