import sys
import os
import subprocess
import datetime
import getpass

def log_bridge_event(command, decision):
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    user = getpass.getuser()
    log_entry = f"[{timestamp}] User: {user} | Decision: {decision} | Command: {command}\n"
    
    # Writing to a simple bridge log file
    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "epistemic", "ledger", "bridge_log.txt")
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Warning: Could not write to bridge log: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python bin/chat_exec_bridge.py <command_string>")
        sys.exit(1)

    # Reconstruct the command from arguments
    proposed_command = " ".join(sys.argv[1:])

    print("\n" + "="*50)
    print("PROPOSED COMMAND FROM CHAT BRIDGE:")
    print("="*50)
    print(f"\n   {proposed_command}\n")
    print("="*50)
    
    confirm = input("Confirm execution? [y/N]: ").strip().lower()

    if confirm == 'y':
        print("\n[EXECUTION]: Confirmed. Running command...\n")
        log_bridge_event(proposed_command, "APPROVED")
        try:
            # We run the command. Note: In this system, bridge commands should target run-skill.py
            # but we allow the full string as drafted by chat for flexibility, 
            # while run-skill.py handles the actual safety logic.
            subprocess.run(proposed_command, shell=True, check=True)
            print("\n[SUCCESS]: Execution complete.")
        except subprocess.CalledProcessError as e:
            print(f"\n[FAILURE]: Command failed with exit code {e.returncode}")
        except Exception as e:
            print(f"\n[ERROR]: Unexpected error: {e}")
    else:
        print("\n[ABORTED]: Execution rejected by user.")
        log_bridge_event(proposed_command, "REJECTED")

if __name__ == "__main__":
    main()
