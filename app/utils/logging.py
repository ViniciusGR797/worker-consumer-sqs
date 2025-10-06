import logging
import json
from datetime import datetime, timezone

logger = logging.getLogger("worker-consumer-sqs")
logger.setLevel(logging.INFO)


def log_message(trace_id, action, status, details=None):
    log_entry = {
        "trace_id": str(trace_id),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "status": status
    }
    if details is not None:
        log_entry["details"] = details
    logger.info(json.dumps(log_entry))
