# Chat Execution Contract

**Status**: Authoritative.

This document defines the rules for translating chat-based proposals into system actions. It establishes the "Human-In-The-Loop" (HITL) requirement for all chat-originated commands.

## 1. Core Principles

1.  **Chat Only Drafts**: The chat interface is permitted to *draft* CLI commands based on user intent.
2.  **Explicit Explanation**: Chat must explain what a drafted command will do before or at the time of drafting.
3.  **No Direct Execution**: The chat environment has **ZERO** authority to execute commands directly on the host system.
4.  **Human Confirmation**: All chat-drafted commands must be confirmed by a human through an explicit "yes/no" step in the CLI bridge.
5.  **CLI Authority**: The CLI wrapper (`bin/run-skill`) remains the final authoritative gatekeeper.

## 2. Forbidden Actions

The following behaviors are strictly prohibited for chat-originated executions:

*   **Silent Execution**: Running any command without notifying the user.
*   **Auto-Correction**: Modifying a command after the human has seen it but before it runs.
*   **Hidden Chaining**: Drafting a command that silently triggers other commands.
*   **Privilege Escalation**: Attempting to use the bridge to run commands outside of the `bin/run-skill` scope.

## 3. The Execution Flow

1.  **User Request**: Human asks Chat to perform a task (e.g., "Summarize the last commit").
2.  **Drafting**: Chat provides a command string (e.g., `python bin/run-skill change-summarizer --commit HEAD`).
3.  **The Bridge**: The human copies this command into the `bin/chat_exec_bridge.py`.
4.  **Confirmation**: The bridge script displays the exact command and asks: `Confirm execution? [y/N]:`.
5.  **Logging**: The approval or rejection is logged.

## 4. Example Usage

**Chat**: "I have drafted the command to summarize your last commit. Please run the following in your terminal:"
`python bin/chat_exec_bridge.py python bin/run-skill change-summarizer --commit HEAD`

**CLI**:
```
[PROPOSED COMMAND]: python bin/run-skill change-summarizer --commit HEAD
Confirm execution? [y/N]: y
[EXECUTION]: Running...
...
```
