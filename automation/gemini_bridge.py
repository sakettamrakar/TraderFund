import subprocess
import tempfile
import time
from pathlib import Path

GEMINI_PATH = r"C:\Users\Sakethfjm\AppData\Roaming\npm\gemini.cmd"
MAX_RETRIES = 2
TIMEOUT_SECONDS = 180
# Windows command line limit is ~8191 chars; use file-based input above this
MAX_INLINE_PROMPT_LEN = 6000


def ask(prompt: str) -> str:
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if len(prompt) <= MAX_INLINE_PROMPT_LEN:
                # Short prompt: pass directly via -p flag
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
                # Long prompt: write to temp file, pipe via stdin
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
