import json
import logging
import time
import requests
from pathlib import Path
from automation.jules.adapter import JulesAdapter
from automation.jules.config import JULES_POLL_INTERVAL

logger = logging.getLogger(__name__)

class TaskMonitor:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.run_dir = Path("automation/runs") / run_id
        self.adapter = JulesAdapter()

    def wait(self, task_id: str, timeout: int = 1800) -> str:
        """
        Polls Jules task status until COMPLETED, FAILED, or TIMEOUT.
        Writes status to jules_status.json.
        """
        logger.info(f"Monitor: Waiting for task {task_id} (timeout={timeout}s)...")
        start_time = time.time()
        status = "UNKNOWN"
        exit_reason = "In progress"

        try:
            while True:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    status = "TIMEOUT"
                    exit_reason = "Exceeded timeout threshold"
                    break

                if self.adapter.api_key == "MOCK":
                    time.sleep(1)
                    status = "COMPLETED"
                    exit_reason = "Mock execution successful"
                    break

                try:
                    # Direct check using adapter's config
                    headers = {"X-Goog-Api-Key": self.adapter.api_key}
                    # task_id is the session name (e.g. sessions/123)
                    url = f"{self.adapter.api_url}/{task_id}"

                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    data = response.json()

                    # Check for outputs
                    outputs = data.get("outputs", [])
                    if outputs:
                        status = "COMPLETED"
                        exit_reason = "Outputs produced"
                        break

                    # Check for explicit failure if API supports it
                    # (Assuming API returns error status or similar if failed)
                    # For now, just wait for outputs.

                except Exception as e:
                    logger.warning(f"Error polling task {task_id}: {e}")

                time.sleep(JULES_POLL_INTERVAL)

        except KeyboardInterrupt:
            status = "FAILED"
            exit_reason = "User interrupted"
            logger.info("Monitor interrupted by user.")
        except Exception as e:
            status = "FAILED"
            exit_reason = str(e)
            logger.error(f"Monitor failed: {e}")

        end_time = time.time()
        duration = end_time - start_time

        status_record = {
            "task_id": task_id,
            "status": status,
            "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
            "end_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time)),
            "duration_seconds": round(duration, 2),
            "exit_reason": exit_reason
        }

        self.run_dir.mkdir(parents=True, exist_ok=True)
        with open(self.run_dir / "jules_status.json", "w") as f:
            json.dump(status_record, f, indent=2)

        logger.info(f"Monitor: Task {task_id} finished with status {status}")
        return status
