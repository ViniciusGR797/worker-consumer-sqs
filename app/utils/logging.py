import logging
import json
from datetime import datetime, timezone

logger = logging.getLogger("worker-consumer-sqs")
logger.setLevel(logging.INFO)


def log_message(trace_id, action, status, details=None):
    log_entry = {
        "trace_id": str(trace_id),
        "action": action,
        "status": status,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    logger.info(json.dumps(log_entry))
