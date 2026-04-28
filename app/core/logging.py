import logging
from pythonjsonlogger import jsonlogger
import sys

class SensitiveDataFilter(logging.Filter):
    SENSITIVE_KEYS = {"api_key", "token", "password"}
    def filter(self, record):
        if hasattr(record, 'msg') and isinstance(record.msg, dict):
            for key in self.SENSITIVE_KEYS:
                if key in record.msg:
                    record.msg[key] = "***MASKED***"
        return True

def setup_logging():
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(correlation_id)s'
    )
    handler.setFormatter(formatter)
    handler.addFilter(SensitiveDataFilter())
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

# Call setup_logging() at app startup
