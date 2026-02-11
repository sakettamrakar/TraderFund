import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from playwright.sync_api import sync_playwright, BrowserContext, Page, Playwright

# Determine Project Root
WORKER_DIR = Path(__file__).resolve().parent
AUTOMATION_DIR = WORKER_DIR.parent
PROJECT_ROOT = AUTOMATION_DIR.parent

@dataclass
class WorkerInstance:
    worker_id: str
    profile_path: str
    playwright: Playwright
    context: BrowserContext
    page: Page

    def close(self):
        """Cleanly closes the worker and playwright instance."""
        try:
            self.context.close()
        except Exception as e:
            print(f"Error closing context: {e}")
        finally:
            self.playwright.stop()

class WorkerManager:
    def launch_worker(self, profile_path: str, headless: bool = True) -> WorkerInstance:
        """
        Launches a persistent browser context for the given profile.

        Args:
            profile_path: Path to the user data directory (profile).
            headless: Whether to run in headless mode.

        Returns:
            WorkerInstance: Handle to the running worker.
        """
        p = sync_playwright().start()

        # Ensure profile path is absolute
        abs_profile_path = Path(profile_path).resolve()

        if not abs_profile_path.exists():
             # Playwright will create it, but good to know if we expected it
             pass

        # Launch persistent context
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(abs_profile_path),
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"],
                viewport={"width": 1280, "height": 720}
            )
        except Exception as e:
            p.stop()
            raise RuntimeError(f"Failed to launch worker for profile {profile_path}: {e}")

        # Get or create page
        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()

        # "Mount" local repo by navigating to it
        # Using file protocol to view directory
        repo_url = f"file://{PROJECT_ROOT}"
        try:
            page.goto(repo_url)
        except Exception as e:
            print(f"Warning: Failed to navigate to repo URL {repo_url}: {e}")

        worker_id = f"worker_{abs_profile_path.name}"

        return WorkerInstance(
            worker_id=worker_id,
            profile_path=str(abs_profile_path),
            playwright=p,
            context=context,
            page=page
        )
