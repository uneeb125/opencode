# Khal Calendar Reference

Detailed reference for Khal CLI calendar client.

## Installation Check

```bash
which khal  # Should return /usr/bin/khal
khal --version  # Returns version info
```

## Global Options

- `-v, --verbosity LVL` - Log level: CRITICAL, ERROR, WARNING, INFO, DEBUG
- `-l, --logfile LOGFILE` - Log to file (default: stdout)
- `-c, --config PATH` - Config file path
- `--color / --no-color` - Enable/disable colored output

## Calendar Setup

### First Time Setup

After adding new calendars in Google Calendar, run:

```bash
vdirsyncer sync           # Sync events
vdirsyncer metasync       # Sync metadata (names, colors)
khal printcalendars       # Verify pretty names show
```

### Calendar Reference

Available calendars:

| Name                    | Command Example                              |
| ----------------------- | -------------------------------------------- |
| Primary                 | `-a "uneebkamal125@gmail.com"`              |
| Routine                 | `-a "Routine"`                              |
| Family                  | `-a "Family"`                               |
| Events                  | `-a "Events"`                               |
| Learning                | `-a "Learning"`                             |
| Research                | `-a "Research"`                             |
| TA                      | `-a "TA"`                                   |
| Logistics               | `-a "Logistics"`                            |
| Assignments             | `-a "Assignments"`                          |
| Chores                  | `-a "Chores"`                               |
| Lectures                | `-a "Lectures"`                             |
| Appointments            | `-a "Appointments"`                         |
| META                    | `-a "META"`                                 |
| Holidays in Pakistan    | `-a "Holidays in Pakistan"`                 |
| Tracking                | `-a "Tracking"`                             |
| MIRABILIs               | `-a "MIRABILIs"`                            |

## Calendar Management

### List All Calendars

```bash
khal printcalendars
```

### Filter by Calendar

Include specific calendar:
```bash
khal list -a "Routine"
khal calendar -a "Routine"
khal at -a "Routine" now
```

Exclude specific calendar:
```bash
khal list -d "Family"
```

## Event Listing

### List Events (Default: Today)

```bash
khal list
khal list today
```

Output format:
```
Today, 2026-03-22
→04:00 Sleep ⟳ :: BC2-Color: -3815995
Eid-ul-Fitr Holiday :: Public holiday
04:00-04:30 Exercise ⟳
12:30-13:30 Lunch ⟳ ⏰
```

Legend:
- `→` - All-day event
- `⟳` - Recurring event
- `⏰` - Has alarm/reminder

### List Events for Date Range

```bash
khal list 2026-03-22 2026-03-25
khal list tomorrow
khal list "2026-03-22 14:00" "2026-03-22 18:00"
khal list today +7d
```

### Show Events at Specific Time

```bash
khal at now
khal at "2026-03-22 13:00"
```

### Calendar View with Agenda

```bash
khal calendar
```

Shows monthly calendar with daily agenda.

### Print Each Event Once

```bash
khal list --once
khal calendar --once
```

### Show Only Upcoming Events

```bash
khal list --notstarted
khal at --notstarted now
```

## Event Searching

### Search for Events

```bash
khal search "Lunch"
khal search "meeting"
```

Search is case-insensitive.

### Search in Specific Calendar

```bash
khal search "meeting" -a "Routine"
khal search "Lunch" -d "Family"
```

## Creating Events

**Important:** After creating events, always run `vdirsyncer sync` to upload to Google Calendar.

### Basic Syntax

```bash
khal new [DATE] START [END] "TITLE" [:: "DESCRIPTION"]
```

### Examples

Today at time:
```bash
khal new 14:00 "Team Meeting"
```

With end time:
```bash
khal new 14:00 15:00 "Team Meeting"
```

Specific date:
```bash
khal new 2026-03-22 14:00 15:00 "Team Meeting"
```

With description:
```bash
khal new 2026-03-22 14:00 15:00 "Meeting" :: "Discuss project updates"
```

### Options

With location:
```bash
khal new -l "Conference Room A" 14:00 "Team Sync"
```

With categories:
```bash
khal new -g "work,important" 14:00 "Critical Meeting"
```

With alarm:
```bash
khal new -m "15m" 14:00 "Meeting with reminder"
khal new -m "1h,15m" 14:00 "Meeting with multiple alarms"
```

### Recurring Events

Daily:
```bash
khal new -r daily 09:00 "Daily Standup"
```

Weekly:
```bash
khal new -r weekly 09:00 "Weekly Review"
```

Monthly:
```bash
khal new -r monthly "15th" "Monthly Report"
```

Yearly:
```bash
khal new -r yearly "2026-03-22" "Anniversary"
```

With end date:
```bash
khal new -r weekly -u 2026-06-30 09:00 "Project Sprint"
```

### In Specific Calendar

```bash
khal new -a "Routine" 14:00 15:00 "Meditation"
khal new -a "Routine" 2026-03-22 14:00 15:00 "Meditation"
```

### Interactive Creation

```bash
khal new -i 14:00
```

## Editing Events

### Edit Interactively

```bash
khal edit "search term"
```

Navigate: Arrow keys to select, Enter to edit field.
Delete: Press D, then y to confirm.

After editing:
```bash
vdirsyncer sync
```

### Edit in Specific Calendar

```bash
khal edit "meeting" -a "Routine"
```

### Include Past Events

```bash
khal edit "old event" --show-past
```

## Importing and Exporting

### Import from ICS

```bash
khal import events.ics
khal import -a "Routine" events.ics
khal import --batch events.ics      # No confirmations
khal import -r events.ics            # Random UID
```

### Preview ICS Without Importing

```bash
khal printics events.ics
cat events.ics | khal printics -
```

## Interactive UI

```bash
khal interactive
ikhal

khal interactive --mouse     # Enable mouse
khal interactive --no-mouse  # Disable mouse

khal interactive -a "Routine"  # Filter calendar
```

## Date/Time Formats

- `now` - Current time
- `today` - Today's date
- `tomorrow` - Tomorrow's date
- `2026-03-22` - Specific date
- `14:00` - Time today
- `2026-03-22 14:00` - Specific datetime
- `2026-03-22 14:00 15:00` - Datetime with end time
- `+3d` - 3 days from now
- `-1w` - 1 week ago

### Check Formats

```bash
khal printformats
```

## Output Formats

### Custom Format

```bash
khal list -f "{start:%H:%M} {title}"
```

### JSON Output

```bash
khal list --json summary,start,end
khal at --json summary,start
khal search --json summary,start,end
```

### Day Format

```bash
khal list -df "%Y-%m-%d"
```

## Common Workflows

### Create Event and Sync

```bash
khal new -a "Routine" 2026-03-22 14:00 15:00 "Meditation"
vdirsyncer sync
```

### Delete Event and Sync

```bash
khal edit "Meditation"
# Press D, then y
vdirsyncer sync
```

### Check Today's Schedule

```bash
vdirsyncer sync && khal list today
```

### Check This Week

```bash
khal list today +7d
```

### Find Free Slots

```bash
khal list today | grep -v "→"
```

### Export Events

```bash
khal list 2026-01-01 2026-12-31 > events_2026.txt
```

## Troubleshooting

### No Events Showing

1. `vdirsyncer sync`
2. `khal printcalendars`
3. `khal list -a "CalendarName"`

### Calendar Shows as Long ID

```bash
vdirsyncer metasync
khal printcalendars
```

### Verbose Debugging

```bash
khal -v DEBUG list today
khal -v TRACE list today
```

## File Locations

- Khal config: `~/.config/khal/config`
- vdirsyncer config: `~/.config/vdirsyncer/config`
- Calendar files: `~/.local/share/calendar/google/`

## vdirsyncer Commands

```bash
vdirsyncer sync           # Sync events and metadata
vdirsyncer metasync       # Sync only metadata (names, colors)
vdirsyncer discover       # Discover new calendars
```