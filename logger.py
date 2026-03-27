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
import logging


def get_logger(name):
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


def log_task_event(logger, task, event, extra=None):
    logger.info(f"{event} - Task {task.id} | {extra or ''}")