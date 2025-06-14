from logdash import create_logdash
import os
from dotenv import load_dotenv

load_dotenv()

def init_loggers():
    logdash = create_logdash({"api_key": os.getenv("LOGDASH_API_KEY")})
    logdash_hw = create_logdash({"api_key": os.getenv("LOGDASH_HW_API_KEY")})
    return logdash.logger, logdash.metrics, logdash_hw.logger, logdash_hw.metrics

