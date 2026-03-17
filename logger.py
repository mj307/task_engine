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

