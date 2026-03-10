# 1. TaskStatus — enum with: PENDING, RUNNING, SUCCESS, FAILED, RETRYING
#
# enum = fixed set of constant values, useful when a var shld only have certain values
from enum import Enum
class TaskStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    
    
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

import uuid
import datetime

class Task:
    def __init__(self, name: str, payload: dict, priority: int = 0, max_retries: int = 3):
        self.id = str(uuid.uuid4())
        self.name = name
        self.payload = payload
        self.priority = priority
        self.max_retries = max_retries
        self.created_at = datetime.now()

        self.status = TaskStatus.PENDING
        self.retry_count = 0
        self.result = None
             
class TaskResult:
    def __init__(self, task_id, output, success: bool, duration_ms: float, error: str | None = None):
        self.task_id = task_id
        self.output = output
        self.success = success
        self.duration_ms = duration_ms
        self.error = error
        
              

