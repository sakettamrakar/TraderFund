import subprocess
import tempfile
import time
import logging
import re
import os
import shutil
from pathlib import Path
from typing import Tuple, Dict, Any, List

from automation.executors.base import BaseExecutor

logger = logging.getLogger(__name__)

GEMINI_PATH = os.environ.get("GEMINI_CLI_PATH") or shutil.which("gemini") or "gemini"
MAX_RETRIES = 2
TIMEOUT_SECONDS = 180
MAX_INLINE_PROMPT_LEN = 6000

def ask(prompt: str) -> str:
    if os.environ.get("MOCK_GEMINI"):
        logger.info("MOCK_GEMINI active: returning mock response.")
        return "MOCK_RESPONSE: " + prompt[:50] + "..."

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if len(prompt) <= MAX_INLINE_PROMPT_LEN:
                result = subprocess.run(
                    [GEMINI_PATH, "-p", prompt],
                    capture_output=True,
                    text=True,
                    shell=True,
                    timeout=TIMEOUT_SECONDS,
                    encoding="utf-8",
                    errors="replace",
                    stdin=subprocess.DEVNULL,
                )
            else:
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".txt", delete=False,
                    encoding="utf-8", dir=tempfile.gettempdir()
                ) as tf:
                    tf.write(prompt)
                    prompt_file = tf.name

                try:
                    with open(prompt_file, "r", encoding="utf-8") as pf:
                        result = subprocess.run(
                            [GEMINI_PATH, "-p", "-"],
                            capture_output=True,
                            text=True,
                            shell=True,
                            timeout=TIMEOUT_SECONDS,
                            encoding="utf-8",
                            errors="replace",
                            stdin=pf,
                        )
                finally:
                    Path(prompt_file).unlink(missing_ok=True)

        except subprocess.TimeoutExpired:
            last_error = f"Gemini CLI timed out after {TIMEOUT_SECONDS}s (attempt {attempt}/{MAX_RETRIES})"
            if attempt < MAX_RETRIES:
                time.sleep(2)
                continue
            raise RuntimeError(last_error)

        if result.returncode != 0:
            stderr = result.stderr.strip() if result.stderr else "(no stderr)"
            last_error = f"Gemini CLI exit code {result.returncode}: {stderr}"
            if attempt < MAX_RETRIES:
                time.sleep(2)
                continue
            raise RuntimeError(last_error)

        output = result.stdout.strip()
        if not output:
            last_error = f"Gemini CLI returned empty output (attempt {attempt}/{MAX_RETRIES})"
            if attempt < MAX_RETRIES:
                time.sleep(2)
                continue
            raise RuntimeError(last_error)

        return output

    raise RuntimeError(last_error or "Gemini CLI failed after all retries")


class GeminiExecutor(BaseExecutor):
    def execute(self, task: Dict[str, Any], run_dir: Path) -> Tuple[str, str]:
        """
        Executes the task using Gemini CLI (Fallback).
        """
        logger.info("Executing task via Gemini Fallback...")

        # 1. Construct Prompt
        # Read changed memory files to give context
        changed_files = task.get("changed_memory_files", [])
        context = ""
        for f in changed_files:
            path = self.project_root / f
            if path.exists():
                context += f"\n### FILE: {f}\n{path.read_text()}\n"

        prompt = (
            f"You are a coding agent. Your task is to execute the following plan:\n"
            f"{task}\n\n"
            f"Context:\n{context}\n\n"
            f"Output format:\n"
            f"Provide the full content of the modified files using the following format:\n"
            f"### FILE: path/to/file.py\n"
            f"... content ...\n"
            f"### END FILE\n"
        )

        # 2. Ask Gemini
        try:
            response = ask(prompt)
        except Exception as e:
            logger.error(f"Gemini execution failed: {e}")
            return "", f"Gemini execution failed: {e}"

        # 3. Apply Changes
        self._apply_response(response)

        # 4. Generate Diff
        # We use a subprocess to get the diff from git
        diff = ""
        try:
            diff_proc = subprocess.run(
                ["git", "diff"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            diff = diff_proc.stdout
        except Exception as e:
            logger.error(f"Failed to generate diff: {e}")

        return diff, f"Gemini Response:\n{response}"

    def _apply_response(self, response: str):
        """
        Parses ### FILE: blocks and writes files.
        """
        lines = response.splitlines()
        current_file = None
        current_content = []

        for line in lines:
            if line.startswith("### FILE:"):
                if current_file:
                    self._write_file(current_file, "\n".join(current_content))
                current_file = line.replace("### FILE:", "").strip()
                current_content = []
            elif line.startswith("### END FILE"):
                if current_file:
                    self._write_file(current_file, "\n".join(current_content))
                    current_file = None
                    current_content = []
            else:
                if current_file:
                    current_content.append(line)

        # Capture last block
        if current_file:
            self._write_file(current_file, "\n".join(current_content))

    def _write_file(self, rel_path: str, content: str):
        try:
            file_path = self.project_root / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            logger.info(f"Gemini: Updated {rel_path}")
        except Exception as e:
            logger.error(f"Gemini: Failed to write {rel_path}: {e}")
