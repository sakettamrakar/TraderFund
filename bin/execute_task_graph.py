import sys
import re
import os
import collections

# Paths
DOCS_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "epistemic", "roadmap")
TASK_GRAPH_FILE = os.path.join(DOCS_ROOT, "task_graph.md")
SKILL_MAP_FILE = os.path.join(DOCS_ROOT, "task_to_skill_map.md")
EXEC_PLAN_FILE = os.path.join(DOCS_ROOT, "execution_plan.md")

class Task:
    def __init__(self, tid, name):
        self.tid = tid
        self.name = name
        self.dependencies = []
        self.freeze_impact = "Unknown"
        self.status = "Pending" # Default
        self.mode = "Unknown"
        self.skill = "N/A"
        
    def __repr__(self):
        return f"<Task {self.tid}: {self.name}>"

def parse_task_graph():
    if not os.path.exists(TASK_GRAPH_FILE):
        print(f"Error: Task Graph not found at {TASK_GRAPH_FILE}")
        sys.exit(1)
        
    with open(TASK_GRAPH_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    tasks = {}
    current_task = None
    
    # Regex patterns
    task_header_re = re.compile(r'^#### Task (P\d+\.\d+\.\d+): (.*)')
    dep_re = re.compile(r'\*   \*\*Dependencies\*\*: (.*)')
    freeze_re = re.compile(r'\*   \*\*Freeze Impact\*\*: (.*)')
    
    for line in content.splitlines():
        # New Task Header
        match = task_header_re.match(line)
        if match:
            tid = match.group(1)
            name = match.group(2)
            current_task = Task(tid, name)
            tasks[tid] = current_task
            continue
            
        if current_task:
            # Parse Dependencies
            dep_match = dep_re.match(line)
            if dep_match:
                deps_str = dep_match.group(1).strip()
                if deps_str.lower() != "none." and deps_str.lower() != "none":
                    # Extract Px.y.z IDs
                    deps = re.findall(r'(P\d+\.\d+\.\d+)', deps_str)
                    current_task.dependencies = deps
            
            # Parse Freeze Impact
            freeze_match = freeze_re.match(line)
            if freeze_match:
                current_task.freeze_impact = freeze_match.group(1).strip()

    return tasks

def parse_skill_map(tasks):
    if not os.path.exists(SKILL_MAP_FILE):
        return # Optional, but good for context
        
    with open(SKILL_MAP_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Table parsing is simple line-by-line
    # | **P1.1.1** | Create Chat Usage Contract | **A** | N/A | ...
    
    for line in content.splitlines():
        if not line.startswith('|'): continue
        
        parts = [p.strip() for p in line.split('|')]
        # Filter empty strings from split
        parts = [p for p in parts if p]
        
        if len(parts) < 3: continue
        
        # Extract ID (remove bolding)
        tid = parts[0].replace('*', '').strip()
        
        if tid in tasks:
            mode = parts[2].replace('*', '').strip()
            # If explicit skill is listed
            skill = parts[3].strip() if len(parts) > 3 else "N/A"
            
            tasks[tid].mode = mode
            tasks[tid].skill = skill

def parse_execution_plan(tasks):
    approved_tasks = set()
    if os.path.exists(EXEC_PLAN_FILE):
        with open(EXEC_PLAN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        # Stupid simple check for now: Look for task IDs in a "Approved" context?
        # Or just look for IDs generally present in the file implies they are in the plan.
        # Let's assume strict listing: "- [ ] Px.y.z"
        
        for line in content.splitlines():
            ids = re.findall(r'(P\d+\.\d+\.\d+)', line)
            for tid in ids:
                approved_tasks.add(tid)
                
    return approved_tasks

def topological_sort_grouping(tasks):
    # Determine levels
    # Since we aren't executing, strict order isn't required, but grouping by dependency satisfaction is useful.
    # Group into: Satisfied (Roots), Blocked
    pass

def main():
    print("--- GRAPH-GOVERNED EXECUTION HARNESS [DRY-RUN ONLY] ---\n")
    
    # 1. Parse Graph
    tasks = parse_task_graph()
    print(f"Loaded {len(tasks)} tasks from Task Graph.")
    
    # 2. Map Skills
    parse_skill_map(tasks)
    
    # 3. Check Plan
    approved_ids = parse_execution_plan(tasks)
    if approved_ids:
        print(f"Loaded Execution Plan: {len(approved_ids)} tasks referenced found.")
    else:
        print("No active Execution Plan found (or file missing).")

    print("\n[TASK ANALYSIS]\n")
    
    # Sort by ID for display
    sorted_ids = sorted(tasks.keys())
    
    stats = {
        "Total": len(tasks),
        "Executable (All Conditions Met)": 0,
        "Frozen": 0,
        "Blocked Dependency": 0,
        "Mode A (Human)": 0,
        "Mode B (Assisted)": 0,
        "Mode C (CLI)": 0
    }

    # "Executed" tasks are tricky sans persistent state file for tasks themselves. 
    # For now, we assume P1 is executed based on the graph definition, but let's just readout static properties.
    
    for tid in sorted_ids:
        t = tasks[tid]
        
        # Check Dependency Satisfaction within this ephemeral run
        # (Naive: Dependencies are 'Satisfied' if they exist in the graph. Real execution requires query of state.)
        # Here we just list them.
        
        deps_met = True
        missing_deps = []
        for d in t.dependencies:
            if d not in tasks: # Should technically check if D is marked 'Executed' in input
                deps_met = False # But we don't track execution state in files yet.
                missing_deps.append(d)
        
        # Determine Status Label
        status_label = "READY"
        if "Requires Unfreeze" in t.freeze_impact or "Req" in t.freeze_impact:
            status_label = "FROZEN"
            stats["Frozen"] += 1
        elif not deps_met:
            status_label = "BLOCKED"
            stats["Blocked Dependency"] += 1
        else:
            # If unfreeze not required, strict dependency check passed
            # Check execution plan
            if tid in approved_ids:
                 status_label = "APPROVED"
                 stats["Executable (All Conditions Met)"] += 1
            elif "Executed" in t.freeze_impact or t.freeze_impact == "None":
                 status_label = "DONE" # Heuristic: P1 tasks marked "Executed" in graph text
            else:
                 status_label = "PENDING PLAN"

        # Heuristic for P1 executed
        if tid.startswith("P1"):
            status_label = "EXECUTED" # Override for known state

        # Collect Stats
        if t.mode == "A": stats["Mode A (Human)"] += 1
        if t.mode == "B": stats["Mode B (Assisted)"] += 1
        if t.mode == "C": stats["Mode C (CLI)"] += 1

        print(f"[{status_label: <10}] {tid} : {t.name}")
        print(f"               Mode: {t.mode} | Skill: {t.skill}")
        print(f"               Freeze: {t.freeze_impact}")
        if t.dependencies:
            print(f"               Deps: {', '.join(t.dependencies)}")
        print("")

    print("---------------------------------------------------")
    print("SUMMARY")
    print(f"Total Tasks: {stats['Total']}")
    print(f"Frozen: {stats['Frozen']}")
    print(f"Executable (Approved): {stats['Executable (All Conditions Met)']}")
    print(f"Human-Only (A): {stats['Mode A (Human)']}")
    print(f"Skill-Assisted (B): {stats['Mode B (Assisted)']}")
    print("---------------------------------------------------")
    print("NOTE: This harness is an OBSERVER. use 'bin/run-skill' for actual execution.")

if __name__ == "__main__":
    main()
