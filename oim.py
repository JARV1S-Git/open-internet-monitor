import logging
from time import gmtime
from src.oim_monitor import OIM_Monitor
import asyncio

if __name__ == "__main__":
    debug_level = logging.DEBUG
    logging.basicConfig(level=debug_level, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.Formatter.converter = gmtime
    test_monitor: OIM_Monitor = OIM_Monitor("microsoft.com")
    #logging.debug(asyncio.run(test_monitor.run_test()))
    test_monitor.database.save_ping_result("google.com", 1.1, True)