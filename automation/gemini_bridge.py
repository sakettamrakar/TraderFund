import subprocess
import time

GEMINI_PATH = r"C:\Users\Sakethfjm\AppData\Roaming\npm\gemini.cmd"
MAX_RETRIES = 2
TIMEOUT_SECONDS = 120


def ask(prompt: str) -> str:
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
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
