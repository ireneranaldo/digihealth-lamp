#!/usr/bin/env python3
"""
DigiHealth Lamp - Main Entry Point
Smart lamp with environmental monitoring and InfluxDB integration.
"""

import sys
import time
import threading
from .config import config
from .logger import setup_logging, logger

# Core modules
from .sensors import SensorManager
from .processors import ProcessorManager
from .communicator import CommunicatorManager

# Optional modules
try:
    from .actuators import ActuatorManager
    actuators_available = True
except ImportError:
    actuators_available = False
    logger.warning("Actuators module not available")

try:
    from .web import WebManager
    web_available = True
except ImportError:
    web_available = False
    logger.warning("Web module not available")

def main():
    """Main application entry point."""
    setup_logging()
    logger.info("Starting DigiHealth Lamp")

    # Initialize core managers
    sensor_manager = SensorManager()
    processor_manager = ProcessorManager()
    communicator_manager = CommunicatorManager()

    # Initialize optional managers
    actuator_manager = ActuatorManager() if actuators_available else None
    web_manager = WebManager() if web_available and config.web.enabled else None

    # Start threads
    threads = []

    # Sensor collection thread
    def sensor_loop():
        while True:
            data = sensor_manager.collect_all()
            processed_data = processor_manager.process(data)
            communicator_manager.send(processed_data)

            if actuator_manager:
                actuator_manager.update(processed_data)

            time.sleep(30)  # Collect every 30 seconds

    threads.append(threading.Thread(target=sensor_loop, daemon=True))

    # Web server thread (if enabled)
    if web_manager:
        threads.append(threading.Thread(target=web_manager.run, daemon=True))

    # Start all threads
    for thread in threads:
        thread.start()

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down DigiHealth Lamp")
        sys.exit(0)

if __name__ == "__main__":
    main()