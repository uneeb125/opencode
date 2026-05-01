# Ncal Calendar Reference

Detailed reference for ncal CLI calendar client.

## Installation Check

```bash
which ncal  # Should return path to binary
ncal --version  # Returns version info
```

## Global Options

- `-d, --debug` - Enable debug output
- `-h, --help` - Print help
- `-V, --version` - Print version

## Calendar Setup

### First Time Setup

After configuring Nextcloud connection:

```bash
ncal sync              # Sync events from server
ncal calendars         # Verify calendars show
```

### Calendar Reference

Use `ncal calendars` to list available calendars. Common calendars include:

| Name                    | Command Example                              |
| ----------------------- | -------------------------------------------- |
| Primary                 | `-c "uneebkamal125@gmail.com"`              |
| Routine                 | `-c "Routine"`                              |
| Family                  | `-c "Family"`                               |
| Events                  | `-c "Events"`                               |
| Learning                | `-c "Learning"`                             |
| Research                | `-c "Research"`                             |
| TA                      | `-c "TA"`                                   |
| Logistics               | `-c "Logistics"`                            |
| Assignments             | `-c "Assignments"`                          |
| Chores                  | `-c "Chores"`                               |
| Lectures                | `-c "Lectures"`                             |
| Appointments            | `-c "Appointments"`                         |
| META                    | `-c "META"`                                 |
| Holidays in Pakistan    | `-c "Holidays in Pakistan"`                 |
| Tracking                | `-c "Tracking"`                             |
| MIRABILIs               | `-c "MIRABILIs"`                            |

## Calendar Management

### List All Calendars

```bash
ncal calendars
```

### Filter by Calendar

```bash
ncal list -c "Routine"
ncal list -d "2026-03-22" -c "Routine"
```

## Event Listing

### List Events (Default: Today)

```bash
ncal list
ncal list -t           # Tomorrow
ncal list -d "2026-03-22"  # Specific date
```

Output format:
```
2026-03-22
  14:00-15:00 Meditation (Routine)
  16:00-17:00 Meeting (Work)
```

### List Events for Date Range

```bash
ncal list --range "2026-03-22" "2026-03-25"
```

### Show Event Details

```bash
ncal show "meeting"
ncal show "meeting" -c "Routine"
```

## Creating Events

**Important:** After creating events, always run `ncal sync` to upload to Nextcloud.

**Required:** When adding events, you MUST always specify both `--start` and `--end`.

### Basic Syntax

```bash
ncal add "TITLE" -s "START" -e "END" [-c "CALENDAR"]
```

### Examples

Today at time:
```bash
ncal add "Team Meeting" -s "2026-03-22T14:00:00-05:00" -e "2026-03-22T15:00:00-05:00"
```

With description:
```bash
ncal add "Meeting" -s "2026-03-22T14:00:00-05:00" -e "2026-03-22T15:00:00-05:00" --description "Discuss project updates"
```

With location:
```bash
ncal add "Team Sync" -s "2026-03-22T14:00:00-05:00" -e "2026-03-22T15:00:00-05:00" -l "Conference Room A"
```

With tags/categories:
```bash
ncal add "Critical Meeting" -s "2026-03-22T14:00:00-05:00" -e "2026-03-22T15:00:00-05:00" -t "work,important"
```

With recurrence:
```bash
ncal add "Daily Standup" -s "2026-03-22T09:00:00-05:00" -e "2026-03-22T09:30:00-05:00" --rrule "FREQ=DAILY;COUNT=5"
```

### In Specific Calendar

```bash
ncal add "Meditation" -s "2026-03-22T14:00:00-05:00" -e "2026-03-22T15:00:00-05:00" -c "Routine"
```

## Removing Events

### Remove by UID

```bash
ncal remove "event-uid-here"
```

### Find UID First

```bash
ncal show "Meeting" -c "Routine"
# Then use the UID from output
ncal remove "uid-from-output"
```

## Syncing

```bash
ncal sync              # Sync events from server
```

## Date/Time Formats

- `YYYY-MM-DD` - Specific date (for `-d` flag)
- `YYYY-MM-DDTHH:MM:SS-05:00` - ISO datetime with timezone offset
- Always include timezone offset: `-05:00` for EST

## Common Workflows

### Create Event and Sync

```bash
ncal add "Meditation" -s "2026-03-22T14:00:00-05:00" -e "2026-03-22T15:00:00-05:00" -c "Routine"
ncal sync
```

### Check Today's Schedule

```bash
ncal sync && ncal list
```

### Check This Week

```bash
ncal list --range "2026-03-22" "2026-03-29"
```

## Troubleshooting

### No Events Showing

1. `ncal sync`
2. `ncal calendars`
3. `ncal list -c "CalendarName"`

### Debug Output

```bash
ncal -d list
ncal -d sync
```

## File Locations

- ncal binary: `~/.cargo/bin/ncal`
- ntasks binary: `~/.cargo/bin/ntasks`
