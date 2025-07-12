import serial
import time
from utils import get_config_value

NO_DATA_TIMEOUT = 30
METRICS_BATCH_SIZE = 10
RPI_NUMBER = get_config_value("device", "rpi_number", 1)


class SerialHandler:
    def __init__(self, port, baud_rate, logger, logger_hw, metrics, metrics_hw):
        self.port = port
        self.baud_rate = baud_rate
        self.logger = logger
        self.logger_hw = logger_hw
        self.metrics = metrics
        self.metrics_hw = metrics_hw
        self.moisture_readings = []
        self.ser = None
        self.last_data_time = time.time()

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=5)
            time.sleep(2)
            self.logger_hw.debug(f"[RPi #{RPI_NUMBER}] - Connected to Arduino")
            self.last_data_time = time.time()
        except serial.SerialException as e:
            self.logger.error(f"[RPi #{RPI_NUMBER}] - Serial port error: {e}")
            raise

    def close(self):
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                self.logger.debug(f"[RPi #{RPI_NUMBER}] - Serial port closed")
            except Exception as e:
                self.logger.error(
                    f"[RPi #{RPI_NUMBER}] - Error closing serial port: {e}"
                )

    def reset_connection(self):
        self.logger.warning(
            f"[RPi #{RPI_NUMBER}] - No data for timeout, resetting serial port."
        )
        self.close()
        time.sleep(2)
        try:
            self.connect()
            self.moisture_readings.clear()
        except Exception as e:
            self.logger.error(f"[RPi #{RPI_NUMBER}] - Error reopening serial port: {e}")

    def read_loop(self):
        while True:
            line = self.ser.readline().decode("utf-8", errors="ignore").strip()
            if line:
                self.last_data_time = time.time()
                self.handle_line(line)

            if time.time() - self.last_data_time > NO_DATA_TIMEOUT:
                self.reset_connection()

    def handle_line(self, line):
        # Temporary calibration data from Arduino
        # const int dryValue = 742;
        # const int wetValue = 505;

        if line == "Start pomiaru wilgotności gleby...":
            return

        try:
            import json

            data = json.loads(line)
            moisture = float(data["wilgotnosc"])
            self.logger.info(f"[RPi #{RPI_NUMBER}] - Moisture raw: {moisture}%")

            self.moisture_readings.append(moisture)

            if len(self.moisture_readings) >= METRICS_BATCH_SIZE:
                avg_moisture = int(
                    sum(self.moisture_readings) / len(self.moisture_readings)
                )
                self.metrics.set("Wilgotność", avg_moisture)
                self.logger.debug(
                    f"[RPi #{RPI_NUMBER}] - Sent metrics: Wilgotność = {avg_moisture}%"
                )
                self.moisture_readings.clear()
        except (json.JSONDecodeError, KeyError, ValueError):
            self.logger.error(f"[RPi #{RPI_NUMBER}] - Invalid JSON or message: {line}")
