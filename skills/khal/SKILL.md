---
name: khal
description: CLI calendar client for managing events, calendars, and scheduling
---

# Khal Calendar Client Skill

You help users manage calendars using Khal, a CLI calendar client that supports vdirsyncer for syncing with remote calendars.

## When to Use

- User wants to list, view, or search calendar events
- User needs to create, edit, or delete events
- User wants to see calendar views with agenda
- User needs to import/export events from ICS files
- User wants to use interactive calendar UI

## Important Notes

- **Always run `vdirsyncer sync` before using khal to sync calendars from remote servers**
- Use `vdirsyncer metasync` to sync metadata (calendar names, colors) after adding new calendars
- Date/time formats are flexible (e.g., "today", "tomorrow", "2026-03-22", "now")
- Use calendar name with `-a` flag (e.g., `-a "Routine"`)

## Quick Start

```bash
# Sync calendars first
vdirsyncer sync

# See available calendars
khal printcalendars

# List today's events
khal list today

# Create event in specific calendar
khal new -a "Routine" 2026-03-22 14:00 15:00 "Meditation"

# Sync changes to Google Calendar
vdirsyncer sync
```

## Common Commands

```bash
khal printcalendars              # List all calendars
khal list today                  # Today's events
khal at now                      # Events at current time
khal calendar                    # Calendar view with agenda
khal search "meeting"            # Search events
khal new -a "CalendarName" TIME "Event Title"  # Create event
khal edit "event"                # Edit/delete event
```

## Troubleshooting

- No events showing? Run `vdirsyncer sync`
- Calendar shows as long ID? Run `vdirsyncer metasync` to fetch pretty names

For detailed documentation, see `REFERENCE.md`.