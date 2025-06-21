import threading
import time
from metrics import init_loggers
from utils import setup_signal_handlers, get_config_value
from serial_handler import SerialHandler

SERIAL_PORT = get_config_value("device", "port", "/dev/ttyUSB0")
BAUD_RATE = get_config_value("device", "baudrate", 9600)
RPI_NUMBER = get_config_value("device", "rpi_number", 1)


def send_uptime_metric(metrics_hw, logger_hw):
    start_time = time.time()
    while True:
        uptime_seconds = int(time.time() - start_time)
        uptime_minutes = int(uptime_seconds / 60)
        metrics_hw.set("Uptime [minutes]", uptime_minutes)
        logger_hw.info(f"[RPi #{RPI_NUMBER}] - Sent uptime: {uptime_seconds} s")
        time.sleep(60)


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
