import os
import json
import logging
import time
import re
import subprocess
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
    Adapter for submitting jobs (sessions) to the Google Jules API.
    """

    def __init__(self):
        self.api_url = JULES_API_URL.rstrip('/')
        self.api_key = JULES_API_KEY

        if not self.api_key:
            logger.warning("JULES_API_KEY is not set. Jules execution may fail.")

        self.source_name = self._detect_source_name()

    def _detect_source_name(self) -> str:
        """
        Detects the Jules source name from local git config.
        Format: sources/github/{owner}/{repo}
        """
        try:
            # Fallback to configured env var if present
            if os.environ.get("JULES_SOURCE_NAME"):
                return os.environ.get("JULES_SOURCE_NAME")

            # Try to get remote origin URL
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True, text=True, check=True
            )
            url = result.stdout.strip()
            # Parse owner/repo from URL (supports https and ssh)
            # https://github.com/owner/repo.git
            # git@github.com:owner/repo.git
            match = re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?", url)
            if match:
                owner, repo = match.groups()
                return f"sources/github/{owner}/{repo}"
            
            logger.warning("Could not detect GitHub repo from git config. Using default placeholder.")
            return "sources/github/sakettamrakar/TraderFund" # Fallback based on known context

        except Exception as e:
            logger.warning(f"Failed to detect git remote: {e}")
            return "sources/github/sakettamrakar/TraderFund"

    def create_job(self, task: Dict[str, Any], instructions: str) -> Dict[str, Any]:
        """
        Creates the payload for creating a Jules session.
        """
        task_id = task.get("task_id", "unknown-task")
        title = f"Task {task_id}: {task.get('purpose', 'Automated Task')}"
        
        # Construct prompt from instructions plus explicit changes context if available
        prompt = instructions
        files = task.get("changed_memory_files", [])
        if files:
            prompt += "\n\nRelevant files:\n" + "\n".join(files)

        return {
            "title": title,
            "prompt": prompt,
            "sourceContext": {
                "source": self.source_name,
                "githubRepoContext": {
                    "startingBranch": "main"  # Or current branch? Ideally detect current branch.
                }
            },
            "automationMode": "AUTO_CREATE_PR",
            # internal tracking
            "task_id": task_id 
        }

    def submit_job(self, payload: Dict[str, Any]) -> str:
        """
        Submits the job (creates a session) to Jules API. Returns session ID.
        """
        task_id = payload.pop("task_id", "unknown")
        logger.info(f"Submitting Jules session for task {task_id} on {self.source_name}...")

        headers = {
            "X-Goog-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            # Mock mode check
            if self.api_key == "MOCK":
                logger.info("MOCK mode: Returning fake session ID")
                return f"sessions/mock-{int(time.time())}"

            # Detect current branch to avoid working on stale 'main'
            try:
                branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True).stdout.strip()
                if branch:
                    payload["sourceContext"]["githubRepoContext"]["startingBranch"] = branch
            except:
                pass

            response = requests.post(
                f"{self.api_url}/sessions",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            session_name = data.get("name") # e.g. sessions/123456
            
            # The API returns 'name' as the unique ID resource string
            # We return just the ID part or the full resource name depending on what poll expects
            # Let's keep the full resource name as the ID
            job_id = session_name
            
            logger.info(f"Jules session created successfully. Session: {job_id}")
            return job_id

        except Exception as e:
            logger.error(f"Failed to create Jules session: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise RuntimeError(f"Jules submission failed: {e}")

    def poll_job(self, job_id: str) -> str:
        """
        Polls session status until outputs (PR) are generated or timeout.
        Returns "COMPLETE" or "FAILED".
        """
        logger.info(f"Polling Jules session {job_id}...")
        start_time = time.time()

        while (time.time() - start_time) < JULES_TIMEOUT:
            if self.api_key == "MOCK":
                time.sleep(1)
                return "COMPLETE"

            try:
                headers = {"X-Goog-Api-Key": self.api_key}
                response = requests.get(
                    f"{self.api_url}/{job_id}", # job_id is "sessions/..."
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                
                # Check for outputs (PRs)
                outputs = data.get("outputs", [])
                if outputs:
                    # If any output exists (like a PR), we consider it done for now
                    logger.info(f"Jules session produced outputs: {len(outputs)}")
                    return "COMPLETE"
                
                # Check for explicit errors if API provides them (not detailed in snippet but good practice)
                # If no outputs yet, continue polling
                time.sleep(JULES_POLL_INTERVAL)

            except Exception as e:
                logger.error(f"Error polling session {job_id}: {e}")
                time.sleep(JULES_POLL_INTERVAL)

        raise TimeoutError(f"Jules session {job_id} timed out after {JULES_TIMEOUT}s (no outputs produced)")

    def get_results(self, job_id: str) -> Dict[str, Any]:
        """
        Fetches session results.
        Returns schema with 'diff', 'logs', 'tests' (adapted from session output).
        """
        if self.api_key == "MOCK":
            return {
                "diff": "",
                "logs": "Mock execution successful.",
                "tests": "All tests passed (mock)."
            }

        headers = {"X-Goog-Api-Key": self.api_key}
        try:
            response = requests.get(
                f"{self.api_url}/{job_id}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            outputs = data.get("outputs", [])
            pr_links = []
            description = "Jules execution completed."
            
            for out in outputs:
                if "pullRequest" in out:
                    pr = out["pullRequest"]
                    pr_links.append(f"{pr.get('title')} - {pr.get('url')}")
            
            logs = f"Session: {data.get('name')}\nPrompt: {data.get('prompt')}\n"
            if pr_links:
                logs += "\nGenerated Pull Requests:\n" + "\n".join(pr_links)
            else:
                logs += "\nNo Pull Requests generated yet."

            return {
                "diff": "", # Jules creates PRs, so diff is on GitHub
                "logs": logs,
                "tests": "N/A (See Pull Request checks)"
            }
        except Exception as e:
            logger.error(f"Failed to get results for session {job_id}: {e}")
            raise RuntimeError(f"Could not fetch Jules results: {e}")
