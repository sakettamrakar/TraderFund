import sys
import os
import datetime
import getpass

# Add project root to path
sys.path.append(os.getcwd())
from src.utils.logging import setup_logging

SKILLS_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".agent", "skills")

logger = setup_logging("RunSkillCLI", log_dir="logs")

def main():
    if len(sys.argv) < 2:
        print("Usage: python bin/run-skill <skill-name> --user <user_id> [inputs]")
        print("Error: Missing skill name.")
        sys.exit(1)

    skill_name = sys.argv[1]
    
    # Simple manual arg parsing
    if "--user" in sys.argv:
        user_idx = sys.argv.index("--user")
        if user_idx + 1 < len(sys.argv):
            user_id = sys.argv[user_idx + 1]
            # Remove from args passed to skill
            skill_args = sys.argv[2:user_idx] + sys.argv[user_idx+2:]
        else:
            logger.error("Error: --user flag provided but no username specified.")
            sys.exit(1)
    else:
        # Enforce attribution in Phase 4
        logger.error("Error: Operator Attribution Required (Phase 4). Please provide --user <your_id>")
        sys.exit(1)

    skill_dir = os.path.join(SKILLS_ROOT, skill_name)
    
    # 1. Log Execution
    # Pass user_id in 'extra' so JSONFormatter picks it up as 'user' field
    logger.info(f"Invoking Skill: {skill_name} | Inputs: {skill_args}", extra={"user": user_id})

    # 2. Validate Skill Existence
    if not os.path.isdir(skill_dir):
        logger.error(f"Error: Skill '{skill_name}' not found in {SKILLS_ROOT}")
        sys.exit(1)

    # 3. Invoke Skill (Placeholder for actual delegation)
    print(f"--- Invoking Skill: {skill_name} ---") # Keep STDOUT for interactive feedback
    
    skill_file = os.path.join(skill_dir, "SKILL.md")
    if os.path.exists(skill_file):
        print(f"Skill loaded from: {skill_dir}")
        print(f"Instructions available in: {skill_file}")
        # Here we would delegate to the skill's logic if it existed as code.
        print("(Skill logic is declarative. Please follow instructions in SKILL.md)")
        
        # Check for executable script
        script_dir = os.path.join(skill_dir, "scripts")
        if os.path.exists(script_dir):
             logger.info(f"Checking for executable scripts in {script_dir}")
             # Future: Auto-execute based on convention
    else:
        logger.error(f"Error: SKILL.md not found for {skill_name}")
        sys.exit(1)

if __name__ == "__main__":
    main()
