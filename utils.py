import signal
import sys
import time

def setup_signal_handlers(logger_hw):
    def handle_exit(signum, frame):
        logger_hw.warn("[RPi #1] - Program shutting down due to signal")
        logger_hw.error("[RPi #1] - Program stopped")
        time.sleep(5)
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)
