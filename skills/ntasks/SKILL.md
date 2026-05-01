---
name: ntasks
description: CLI tool for managing Nextcloud tasks via CalDAV
---

# Ntasks Skill

You help users manage tasks using ntasks, a CLI tool for Nextcloud Tasks via CalDAV.

## Important Notes

- Requires configuration: run `ntasks config` if not already configured
- Use `-c, --calendar` to specify which calendar/tasklist to work with
- Tasks are identified by UID or partial title match for complete/delete operations

## Quick Start

```bash
ntasks calendars                     # List available calendars
ntasks list                          # List all tasks
ntasks list -c "Tasks"               # List tasks in specific calendar
ntasks add "Buy milk" -d "2026-03-25" -c "Tasks"
ntasks complete "Buy milk"           # Mark task as complete
ntasks delete "Buy milk" -f          # Delete task (force, no confirm)
ntasks sync                          # Sync with Nextcloud server
```

## Calendars

```bash
ntasks calendars                     # List all calendars
```

## Tasks

```bash
ntasks list                          # List pending tasks
ntasks list -a                       # Include completed tasks
ntasks list -c "Tasks"               # Filter by calendar

ntasks add "Task title" -d "2026-03-25" -n "Notes" -c "Tasks"
# Date format: YYYY-MM-DD or YYYY-MM-DD HH:MM

# With description
ntasks add "Task title" --description "Detailed notes" -c "Tasks"

# With priority (1-9, 9=highest)
tasks add "Urgent task" -p 9 -c "Tasks"

# With tags/categories
ntasks add "Work task" -t "work,important" -c "Tasks"

# Subtasks: use -P flag with parent task UID
ntasks add "Subtask" -P "parent-uid-here" -c "Tasks"

ntasks complete "task title"         # Mark as complete by partial title
ntasks delete "task title" -f        # Delete by partial title (force)
```

## Output

```bash
ntasks list                          # Default: pending tasks only
ntasks list -a                       # Show completed too
ntasks list -c "Tasks"               # Filter by calendar
```

## Troubleshooting

Not configured:
```bash
ntasks config
```

Sync issues:
```bash
ntasks sync
```

For more help: `ntasks [command] --help`
