import signal
import requests
import time
from multiprocessing import Process
from energy_monitor import EnergyMonitor
from lightning_manager import LightningManager

if __name__ == '__main__':
    """
        Starts the EnergyMonitor process, monitoring
        generated and consumed energy inside a community.
        Also, every some seconds, it checks pending messages
        from SaaS (to open/close channels, start/stop something, ..),
        and pending invoices to be payed through the Lightning Manager.
    """
    community_id = "1"
    stop = False

    em = EnergyMonitor(community_id)
    em_p = Process(target=em.run)

    lm = LightningManager(community_id)

    def stop_handler(signum, frame):
        global stop
        stop = True
        em_p.stop = True

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    em_p.start()

    while not stop:
        # TODO: Get pending messages from SaaS
        #       Interact with LM to open channels
        # TODO: Get pending invoicing from SaaS
        #       Interact with LM to make payments
        #       Send to SaaS the payment confirmation

        time.sleep(5)

    

    em_p.join()

