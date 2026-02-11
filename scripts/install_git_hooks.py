"""
Installs git hooks from automation/hooks/ to .git/hooks/
And ensures core.hooksPath is correctly set.
"""
import sys
import shutil
import stat
import os
import subprocess
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent
    hooks_src = root / "automation" / "hooks" / "pre-commit"

    # We assume .git is in root
    hooks_dst_dir = root / ".git" / "hooks"

    if not hooks_dst_dir.exists():
        print(f"Error: .git/hooks directory not found at {hooks_dst_dir}")
        print("Are you in a git repository?")
        sys.exit(1)

    if not hooks_src.exists():
        print(f"Error: Source hook not found at {hooks_src}")
        sys.exit(1)

    hooks_dst = hooks_dst_dir / "pre-commit"

    print(f"Installing pre-commit hook to {hooks_dst}...")
    shutil.copy(hooks_src, hooks_dst)

    # Make executable
    st = os.stat(hooks_dst)
    os.chmod(hooks_dst, st.st_mode | stat.S_IEXEC)

    # Configure git to use local hooks explicitly
    # This overrides any global/system setting that might disable hooks (e.g. /dev/null)
    print("Configuring git core.hooksPath to .git/hooks...")
    subprocess.run(["git", "config", "core.hooksPath", ".git/hooks"], cwd=str(root))

    print("✅ Git hooks installed and enabled successfully.")

if __name__ == "__main__":
    main()
