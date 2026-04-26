---
name: autoscheduler
description: AI-powered automatic scheduling system that learns from historical data, tracks personal resources (mental/physical/willpower), and generates optimized daily schedules while respecting fixed calendar events and task deadlines.
---

# AutoScheduler Skill

## Overview

An intelligent scheduling system that:
- **Learns** from your Simple Tracker CSV logs
- **Syncs** with `ntasks` (tasks) and `ncal` (calendar events)
- **Models** your personal resource state (mental bandwidth, physical energy, willpower)
- **Tracks** expected vs actual behavior with deviation analysis
- **Plans** your day considering ADHD, medication timing, energy curves, and task requirements
- **Commits** approved plans to a dedicated `Generated` calendar

## Commands

| Command | Description |
|---------|-------------|
| `/autoscheduler init` | Initialize database and configuration |
| `/autoscheduler import-log <path>` | Import Simple Tracker CSV export |
| `/autoscheduler sync` | Sync tasks from ntasks and events from ncal |
| `/autoscheduler analyze` | Run statistical analysis on historical data |
| `/autoscheduler plan [date]` | Generate AI schedule draft (default: today) |
| `/autoscheduler commit [date]` | Push approved plan to ncal Generated calendar |
| `/autoscheduler stats [activity]` | Show historical stats for activities |
| `/autoscheduler suggest-break` | Quick recommendation based on today's state |
| `/autoscheduler reconcile [date]` | Compare planned vs actual to improve predictions |

## Quick Start

```bash
# 1. Initialize
/autoscheduler init

# 2. Import your historical data
/autoscheduler import-log ~/Downloads/simple_tracker_export.csv

# 3. Sync current tasks and calendar
/autoscheduler sync

# 4. Analyze patterns
/autoscheduler analyze

# 5. Generate a plan
/autoscheduler plan

# 6. Review the output, then commit
/autoscheduler commit
```

## How It Works

### 1. Data Ingestion
Reads Simple Tracker CSV exports with columns:
- `activity name`, `time started`, `time ended`, `comment`, `categories`, `tags`, `duration`

Comments support resource annotations:
- `cost: m40 p0 w30` (mental/physical/willpower cost)
- `gain: m20 p10 w0` (resource recovery)
- `note: felt drowsy after` (contextual notes)
- `med: adderall` (medication tracking)
- `phase: peak` (medication phase)

### 2. Database Architecture: Expected vs Actual

The database is designed as a repository for modeling expected vs actual behavior:

**Planned Events** (`planned_events`): What was scheduled
- Populated from ncal calendar sync
- Tracks title, planned start/end, expected duration
- Source = 'ncal' for calendar events

**Actual Events** (`actual_events`): What actually happened
- Populated from Simple Tracker CSV imports
- Tracks real duration, resource costs, states
- Links to planned events via mappings

**Event Mappings** (`event_mappings`): Links planned to actual
- Tracks deviation in minutes
- Match confidence score
- Deviation reason (if known)

**Unplanned Events** (`unplanned_events`): Tracker items with no corresponding plan
- Used for ADHD pattern analysis
- Tracks "what interrupted the plan"

**Resource Snapshots** (`resource_snapshots`): State over time
- Mental/physical/willpower levels
- ADHD medication tracking (taken, type, phase, effectiveness)
- Time of day context

### 3. Learning
Builds statistical baselines:
- Activity duration distributions (mean, stddev)
- Time-of-day efficiency curves
- Resource depletion/recovery rates
- Post-food energy patterns
- ADHD medication window optimization
- Planned vs actual deviation trends

### 4. Planning
The LLM orchestrator:
- Reads your current resource state
- Fetches pending tasks from ntasks
- Fetches fixed events from ncal
- Uses historical stats as priors
- Applies ADHD-aware scheduling (medication peaks, crash windows)
- Generates a structured schedule with reasoning

### 5. Commitment
Approved plans are written to the `Generated` ncal calendar. They sync directly to Nextcloud CalDAV.

## ADHD & Medication Awareness

The scheduler accounts for short-acting stimulant medication:
- **Onset window** (~30-60 min post-dose): Light tasks, setup, routine
- **Peak window** (~1-3 hours): Deep work, complex tasks
- **Maintenance** (~3-5 hours): Standard productive work
- **Offset/Crash** (~5-6 hours): Admin, chores, recovery
- **Evening**: Low-demand tasks, wind-down

Configure your medication timing in the init wizard.

## Database

SQLite database at `~/.config/opencode/skills/autoscheduler/data/data.db`

Tables:
- `planned_events`: Scheduled calendar events (the "plan")
- `actual_events`: Imported tracker data (what actually happened)
- `event_mappings`: Links between planned and actual with deviation tracking
- `unplanned_events`: Tracker items with no corresponding plan
- `time_patterns`: Learned statistical patterns per activity
- `daily_summaries`: Aggregate stats per day (planned vs actual ratios)
- `resource_snapshots`: Historical resource state with medication tracking
- `tasks`: Pending ntasks items
- `calendar_events`: Raw synced ncal events
- `daily_plans`: Generated schedule drafts
- `plan_items`: Individual time blocks in a plan

## Configuration

Config stored in `~/.config/opencode/skills/autoscheduler/data/config.json`:
- Default daily resources (mental/physical/willpower maxima)
- Medication schedule (if applicable)
- Calendar preferences
- Task list priorities

## Important Notes

- **Always review** generated plans before committing
- Plans are written to `Generated` calendar, never overwrite fixed events
- `ncal sync` runs automatically after committing to push to Nextcloud
- **All scheduled events must be in the future** — the system checks current date/time before creating any event
- **Events must fall within the task's date boundaries** — between start date and due date if set, with enough time to complete before the deadline
- **Earliest-available-first** — tasks are scheduled in the earliest open slot to leave room for unexpected changes later
- The more data you log, the better the predictions become
- Resource costs in comments are optional; the system learns defaults over time
- Database models expected vs actual behavior for insight extraction

## Tool Reference

### ntasks CLI Format

**List tasks** (show all calendars):
```bash
ntasks list
# Output: Calendar: Tasks
#         - [ ] Task Title | start: 2026-04-22 09:00 | due: 2026-04-25 20:00 | priority: 5 | status: todo
```

**List tasks in a specific calendar**:
```bash
ntasks list -c Tasks
```

**Add a task**:
```bash
ntasks add "Task Title" --due "2026-04-21" --priority 5 -c Tasks
```

### ncal CLI Format

**List events** (today):
```bash
ncal list
# Output: 2026-04-26
#         - 04:00 AM - 04:30 AM | Routine | Exercise | location: - | tags: -
```

**List events by calendar**:
```bash
ncal list --calendar Generated
```

**Create event**:
```bash
ncal add -s "2026-04-21T09:00:00" -e "2026-04-21T10:00:00" -c "Generated" "Task Title" -d "Description"
```

**Available calendars**:
```bash
ncal calendars
```

## Troubleshooting

No tasks showing?
```bash
ntasks list
```

No calendar events?
```bash
ncal list
ncal sync
```

Database corrupted?
```bash
rm ~/.config/opencode/skills/autoscheduler/data/data.db
/autoscheduler init
```

## Requirements

- `ncal` configured with Nextcloud CalDAV
- `ntasks` configured with Nextcloud CalDAV
- Python 3.12+
- SQLite3
