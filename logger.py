# 7. ALL logging setup must live here. No other module should call
#    logging.basicConfig() or create handlers directly.
#
# 8. Provide:
#    - get_logger(name) — returns a named logger
#    - log_task_event(logger, task, event_type, extra=None)
#      logs structured JSON-like message: timestamp, task_id, task_name,
#      event_type, status, extra info
#    - A StructuredFormatter class (logging.Formatter subclass) that formats
#      all log records as JSON strings
import logging, datetime
import json

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # include extra fields if present
        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)

        return json.dumps(log_record)

def get_logger(name: str):
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = StructuredFormatter()
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger

def log_task_event(logger, task, event_type, extra=None):
    log_data = {
        "task_id": task.id,
        "task_name": task.name,
        "event_type": event_type,
        "status": str(task.status),
    }

    if extra:
        log_data.update(extra)

    logger.info(
        f"task_event",
        extra={"extra_data": log_data}
    )