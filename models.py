# 1. TaskStatus — enum with: PENDING, RUNNING, SUCCESS, FAILED, RETRYING
#
# enum = fixed set of constant values, useful when a var shld only have certain values  
# 2. Task — class with:
#    - id (auto-generated uuid)
#    - name (str)
#    - payload (dict)
#    - priority (int, default 0 — higher = more important)
#    - max_retries (int, default 3)
#    - created_at (datetime, auto set)
#    - status (TaskStatus, starts PENDING)
#    - retry_count (int, starts 0)
#    - result (any, starts None)
#
# 3. TaskResult — class with:
#    - task_id
#    - output (any)
#    - success (bool)
#    - duration_ms (float)
#    - error (str or None)

from datetime import datetime
from enum import Enum
import uuid


class TaskStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class Task:
    def __init__(self, name, payload, priority=0, max_retries=2):
        self.id = str(uuid.uuid4())
        self.name = name
        self.payload = payload
        self.priority = priority

        self.status = TaskStatus.PENDING
        self.retry_count = 0
        self.max_retries = max_retries

        self.created_at = datetime.now()
             
class TaskResult:
    def __init__(self, task_id, output, success, duration_ms, error=None):
        self.task_id = task_id
        self.output = output
        self.success = success
        self.duration_ms = duration_ms
        self.error = error
        
        
        
              

