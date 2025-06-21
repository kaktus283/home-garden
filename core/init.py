import threading
import time
import json
import os
from metrics import init_loggers
from utils import setup_signal_handlers
from serial_handler import SerialHandler


def get_config():
    """Loads configuration from the settings.json file in the project's root directory."""
    settings_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "settings.json"
    )
    with open(settings_path) as f:
        return json.load(f)


def send_uptime_metric(metrics_hw, logger_hw):
    start_time = time.time()
    while True:
        uptime_seconds = int(time.time() - start_time)
        uptime_minutes = int(uptime_seconds / 60)
        metrics_hw.set("Uptime [minutes]", uptime_minutes)
        logger_hw.info(f"[RPi #{RPI_NUMBER}] - Sent uptime: {uptime_seconds} s")
        time.sleep(60)


config = get_config()
SERIAL_PORT = config["device"]["port"]
BAUD_RATE = config["device"]["baudrate"]
RPI_NUMBER = config["device"]["rpi_number"]


def main():
    logger, metrics, logger_hw, metrics_hw = init_loggers()
    logger_hw.debug(f"[RPi #{RPI_NUMBER}] - Power ON")

    setup_signal_handlers(logger_hw)

    serial_handler = SerialHandler(
        SERIAL_PORT, BAUD_RATE, logger, logger_hw, metrics, metrics_hw
    )
    try:
        serial_handler.connect()
        threading.Thread(
            target=send_uptime_metric, args=(metrics_hw, logger_hw), daemon=True
        ).start()
        serial_handler.read_loop()
    except Exception as e:
        logger.error(f"[RPi #{RPI_NUMBER}] - Unexpected error: {e}")
    finally:
        logger.debug(f"[RPi #{RPI_NUMBER}] - END")


if __name__ == "__main__":
    main()
