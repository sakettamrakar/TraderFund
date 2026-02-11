import os
import json
import logging
import time
import requests
from typing import Dict, Any, Optional

from automation.jules.config import (
    JULES_API_URL,
    JULES_API_KEY,
    JULES_POLL_INTERVAL,
    JULES_TIMEOUT,
    JULES_FORBIDDEN_PATHS
)

logger = logging.getLogger(__name__)

class JulesAdapter:
    """
    Adapter for submitting jobs to the Jules execution backend.
    """

    def __init__(self):
        self.api_url = JULES_API_URL
        self.api_key = JULES_API_KEY

        if not self.api_key:
            logger.warning("JULES_API_KEY is not set. Jules execution may fail.")

    def create_job(self, task: Dict[str, Any], instructions: str) -> Dict[str, Any]:
        """
        Creates the job payload.
        """
        return {
            "task_id": task.get("task_id"),
            "repo_path": str(os.getcwd()), # Assuming local execution context or mapped volume
            "files": task.get("changed_memory_files", []),
            "instructions": instructions,
            "forbidden_paths": JULES_FORBIDDEN_PATHS,
            "mode": "batch",
        }

    def submit_job(self, payload: Dict[str, Any]) -> str:
        """
        Submits the job to Jules API. Returns job_id.
        """
        logger.info(f"Submitting Jules job for task {payload['task_id']}...")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            # Check for MOCK mode for testing
            if self.api_key == "MOCK":
                logger.info("MOCK mode: Returning fake job ID")
                return f"jules_job_{int(time.time())}"

            response = requests.post(
                f"{self.api_url}/jobs",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            job_id = data.get("job_id")
            logger.info(f"Jules job submitted successfully. Job ID: {job_id}")
            return job_id

        except Exception as e:
            logger.error(f"Failed to submit Jules job: {e}")
            raise RuntimeError(f"Jules submission failed: {e}")

    def poll_job(self, job_id: str) -> str:
        """
        Polls job status until COMPLETE or FAILED.
        Returns final status.
        """
        logger.info(f"Polling Jules job {job_id}...")
        start_time = time.time()

        while (time.time() - start_time) < JULES_TIMEOUT:
            if self.api_key == "MOCK":
                time.sleep(1)
                return "COMPLETE"

            try:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = requests.get(
                    f"{self.api_url}/jobs/{job_id}",
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                status = data.get("status")

                if status in ["COMPLETE", "FAILED"]:
                    return status

                logger.debug(f"Job {job_id} status: {status}")
                time.sleep(JULES_POLL_INTERVAL)

            except Exception as e:
                logger.error(f"Error polling job {job_id}: {e}")
                # Don't crash on transient poll errors, just retry
                time.sleep(JULES_POLL_INTERVAL)

        raise TimeoutError(f"Jules job {job_id} timed out after {JULES_TIMEOUT}s")

    def get_results(self, job_id: str) -> Dict[str, Any]:
        """
        Fetches job results (diff, logs, tests).
        """
        if self.api_key == "MOCK":
            return {
                "diff": "",
                "logs": "Mock execution successful.",
                "tests": "All tests passed (mock)."
            }

        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.get(
                f"{self.api_url}/jobs/{job_id}/results",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get results for job {job_id}: {e}")
            raise RuntimeError(f"Could not fetch Jules results: {e}")
