import sys
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from automation.workers.manager import WorkerManager
from automation.workers.router import AccountRouter

def main():
    parser = argparse.ArgumentParser(description="Check Antigravity Workers")
    parser.add_argument("--no-headless", action="store_true", help="Run in visible mode (not headless)")
    args = parser.parse_args()

    headless = not args.no_headless
    print(f"Running worker check (Headless: {headless})...")

    router = AccountRouter()
    manager = WorkerManager()

    # Get all profiles to check them all
    profiles = router.get_all_profiles()

    all_ready = True

    for profile_path in profiles:
        print(f"Checking profile: {profile_path}")
        try:
            worker = manager.launch_worker(profile_path, headless=headless)

            # Verify URL
            # Wait a moment for page load if needed, but file:// is fast
            worker.page.wait_for_load_state("load")
            current_url = worker.page.url
            expected_start = "file://"

            if current_url.startswith(expected_start):
                print(f"  ✅ Worker Launched. URL: {current_url}")
            else:
                print(f"  ❌ Worker URL mismatch. Got: {current_url}")
                all_ready = False

            worker.close()

        except Exception as e:
            print(f"  ❌ Worker Failed: {e}")
            all_ready = False

    if all_ready:
        print("\nAll workers READY.")
    else:
        print("\nSome workers failed health check.")
        sys.exit(1)

if __name__ == "__main__":
    main()
