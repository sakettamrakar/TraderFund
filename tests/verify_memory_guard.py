import sys
from pathlib import Path

# Add automation dir to path
root = Path(__file__).resolve().parent.parent
automation_dir = root / "automation"
sys.path.insert(0, str(automation_dir))

from diff_applier import apply
from automation_config import SecurityViolation

def main():
    print("Testing Runtime Guard...")

    malicious_diff = """diff --git a/docs/memory/test.md b/docs/memory/test.md
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/docs/memory/test.md
@@ -0,0 +1 @@
+This is a violation.
"""

    try:
        apply(malicious_diff)
        print("❌ FAIL: Protected path modification was NOT blocked.")
        sys.exit(1)
    except SecurityViolation as e:
        print(f"✅ PASS: Caught expected SecurityViolation: {e}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ FAIL: Caught unexpected exception: {type(e).__name__}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
