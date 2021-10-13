import signal
import requests
import time
from multiprocessing import Process
from energy_monitor import EnergyMonitor
import config
import sentry_sdk

sentry_sdk.init(
    "https://8a30ed4b48814d5c9406dcf308eb22e4@o106308.ingest.sentry.io/6005756",

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

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

