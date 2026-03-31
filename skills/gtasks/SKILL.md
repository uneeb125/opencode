---
name: gtasks
description: CLI tool for managing Google Tasks
---

# Gtasks Skill

You help users manage Google Tasks using gtasks CLI tool.

## Important Notes

- Requires authentication: run `gtasks login` if not already logged in
- Use `-l, --tasklist` to specify which task list to work with
- Task numbers change after each operation - verify before modifying
- Use `-p, --parent` to add subtasks under an existing task

## Quick Start

```bash
gtasks tasklists view              # List all tasklists
gtasks tasks view -l "My Tasks"     # View tasks (shows tree structure)
gtasks tasks add -l "My Tasks" -t "Buy milk" -d "2026-03-25"
gtasks tasks add -l "My Tasks" -t "Subtask" -p "Buy milk"  # Add subtask
gtasks tasks done -l "My Tasks"     # Interactive: select with arrow keys
gtasks tasks rm -l "My Tasks"       # Interactive: select with arrow keys
```

## Task Lists

```bash
gtasks tasklists view              # List all tasklists
gtasks tasklists add -t "New List" # Create tasklist
gtasks tasklists update            # Rename tasklist
gtasks tasklists rm                # Delete tasklist
```

## Tasks

```bash
gtasks tasks view -l "My Tasks"              # List tasks
gtasks tasks view -l "My Tasks" --completed   # Show only completed
gtasks tasks view -l "My Tasks" -i            # Include completed
gtasks tasks view -l "My Tasks" --format json  # JSON output

gtasks tasks add -l "My Tasks" -t "Task title" -d "2026-03-25" -n "Notes"
# Date format: YYYY-MM-DD (e.g., "2026-03-25", not "March 25")

# Subtasks: use -p flag with parent task title (recommended) or number
gtasks tasks add -l "My Tasks" -t "Subtask" -p "Parent Task"  # By title (safe)
gtasks tasks add -l "My Tasks" -t "Subtask" -p 1              # By number (can shift)

gtasks tasks add -l "My Tasks" -t "Daily" -r daily --repeat-count 5

gtasks tasks done -l "My Tasks"               # Interactive: arrow keys to select, Enter to confirm
gtasks tasks undo -l "My Tasks"               # Mark completed as incomplete (interactive)

gtasks tasks update -l "My Tasks"             # Interactive: select then edit fields
gtasks tasks update -l "My Tasks" -t "New title" -d "2026-03-30"  # Direct update (specify fields)

gtasks tasks rm -l "My Tasks"                 # Interactive: arrow keys to select, Enter to delete
gtasks tasks clear -l "My Tasks"              # Hide completed tasks
```

## Output Formats

```bash
gtasks tasks view --format table  # Default
gtasks tasks view --format json
gtasks tasks view --format csv
```

## Sorting

```bash
gtasks tasks view --sort due       # Sort by due date
gtasks tasks view --sort title     # Sort by title
gtasks tasks view --sort position  # Default order
```

## Troubleshooting

Not logged in:
```bash
gtasks login
```

View current login status:
```bash
gtasks tasklists view  # Will fail if not authenticated
```

For more help: `gtasks [command] --help`