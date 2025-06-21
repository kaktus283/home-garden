import json
import os
import signal
import sys
import time


def get_config_value(section, key, default=None):
    """Retrieves a value from settings.json for the given section and key."""
    settings_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "settings.json"
    )
    try:
        with open(settings_path) as f:
            config = json.load(f)
            return config.get(section, {}).get(key, default)
    except Exception:
        return default


def setup_signal_handlers(logger_hw):
    def handle_exit(signum, frame):
        rpi_number = get_config_value("device", "rpi_number", 1)
        logger_hw.warn(f"[RPi #{rpi_number}] - Program shutting down due to signal")
        logger_hw.error(f"[RPi #{rpi_number}] - Program stopped")
        time.sleep(5)
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)
