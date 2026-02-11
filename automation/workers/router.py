import json
from pathlib import Path
from typing import List

# Determine Project Root
WORKER_DIR = Path(__file__).resolve().parent
AUTOMATION_DIR = WORKER_DIR.parent
PROFILES_DIR = AUTOMATION_DIR / "profiles"
STATE_FILE = WORKER_DIR / "router_state.json"

class AccountRouter:
    def __init__(self):
        self.accounts = ["account_1", "account_2", "account_3"]
        self.state_file = STATE_FILE
        self._load_state()

    def _load_state(self):
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                    self.current_index = data.get("current_index", 0)
            except Exception:
                self.current_index = 0
        else:
            self.current_index = 0

    def _save_state(self):
        try:
            with open(self.state_file, "w") as f:
                json.dump({"current_index": self.current_index}, f)
        except Exception as e:
            print(f"Warning: Failed to save router state: {e}")

    def get_next_profile_path(self) -> str:
        """
        Returns the path to the next profile directory in the rotation.
        Updates the rotation state.
        """
        account_name = self.accounts[self.current_index]
        profile_path = PROFILES_DIR / account_name

        # Update index for next time (round-robin)
        self.current_index = (self.current_index + 1) % len(self.accounts)
        self._save_state()

        return str(profile_path)

    def get_all_profiles(self) -> List[str]:
        """Returns all profile paths."""
        return [str(PROFILES_DIR / account) for account in self.accounts]
