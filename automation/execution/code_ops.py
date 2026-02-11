import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class CodeOps:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def infer_changes(self, memory_files: list[str]) -> list[dict]:
        """
        Parses memory files to find code change instructions.
        Returns a list of dicts: {'file': str, 'content': str}

        Format expected in memory file:
        ### FILE: path/to/file.py
        ... content ...
        ### END FILE
        """
        changes = []
        for rel_path in memory_files:
            file_path = self.project_root / rel_path
            if not file_path.exists():
                logger.warning(f"Memory file {rel_path} not found.")
                continue

            try:
                content = file_path.read_text()
                lines = content.splitlines()
                current_file = None
                current_content = []

                for line in lines:
                    if line.startswith("### FILE:"):
                        if current_file:
                            changes.append({'file': current_file, 'content': "\n".join(current_content)})
                        current_file = line.replace("### FILE:", "").strip()
                        current_content = []
                    elif line.startswith("### END FILE"):
                        if current_file:
                            changes.append({'file': current_file, 'content': "\n".join(current_content)})
                            current_file = None
                            current_content = []
                    else:
                        if current_file:
                            current_content.append(line)

                # Capture last block if no end marker
                if current_file:
                    changes.append({'file': current_file, 'content': "\n".join(current_content)})

            except Exception as e:
                logger.error(f"Error parsing memory file {rel_path}: {e}")

        return changes

    def apply_changes(self, changes: list[dict]) -> list[str]:
        """
        Applies changes to the filesystem.
        Returns list of modified file paths.
        """
        modified_files = []
        for change in changes:
            rel_path = change['file']
            content = change['content']
            file_path = self.project_root / rel_path

            try:
                # Ensure directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)

                file_path.write_text(content)
                modified_files.append(rel_path)
                logger.info(f"Applied changes to {rel_path}")
            except Exception as e:
                logger.error(f"Failed to write {rel_path}: {e}")

        return modified_files

    def generate_test_if_missing(self, file_path: str):
        """
        Generates a test stub if one is missing for the given file.
        """
        if not file_path.endswith(".py"):
            return

        path = self.project_root / file_path
        if not path.exists():
            return

        # Determine test path
        # Strategy: Look for 'tests' directory in parent or create one
        parent = path.parent
        tests_dir = parent / "tests"
        if not tests_dir.exists():
            try:
                tests_dir.mkdir(exist_ok=True)
                # Create __init__.py
                (tests_dir / "__init__.py").touch()
            except Exception as e:
                logger.warning(f"Could not create tests directory {tests_dir}: {e}")
                return

        test_file_name = f"test_{path.name}"
        test_file_path = tests_dir / test_file_name

        if not test_file_path.exists():
            logger.info(f"Generating test stub for {file_path} at {test_file_path}")
            try:
                content = f"""
import pytest
# from {'.'.join(path.parts[-2:]).replace('.py', '')} import ...

def test_{path.stem}_stub():
    assert True
"""
                test_file_path.write_text(content)
            except Exception as e:
                logger.error(f"Failed to generate test stub: {e}")

    def generate_diffs(self) -> str:
        """
        Runs git diff to capture changes.
        """
        try:
            result = subprocess.run(
                ["git", "diff"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            return result.stdout
        except Exception as e:
            logger.error(f"Failed to generate diffs: {e}")
            return ""

    def reset_changes(self):
        """
        Resets changes (useful for cleanup or failure rollback).
        """
        try:
            subprocess.run(["git", "reset", "--hard"], cwd=str(self.project_root))
            subprocess.run(["git", "clean", "-fd"], cwd=str(self.project_root))
        except Exception as e:
            logger.error(f"Failed to reset changes: {e}")
