---
name: ncal
description: CLI calendar client for managing events via CalDAV (Nextcloud)
---

# Ncal Calendar Client Skill

You help users manage calendars using ncal, a CLI calendar client that syncs with Nextcloud via CalDAV.

## When to Use

- User wants to list, view, or search calendar events
- User needs to create, edit, or delete events
- User wants to see calendar views with agenda
- User needs to manage calendar events synced with Nextcloud

## Important Notes

- **Always run `ncal sync` before using ncal to sync calendars from the server**
- **When adding events, ALWAYS specify both `--start` and `--end`**
- Date/time formats: use ISO format `YYYY-MM-DDTHH:MM:SS` or `YYYY-MM-DD` for dates
- Use calendar name with `-c` flag (e.g., `-c "Routine"`)
- Timezone offset required: use `-05:00` format (not `+0500`)

## Quick Start

```bash
# Sync calendars first
ncal sync

# See available calendars
ncal calendars

# List today's events
ncal list

# Create event in specific calendar
ncal add "Meditation" -s "2026-03-22T14:00:00-05:00" -e "2026-03-22T15:00:00-05:00" -c "Routine"

# Sync changes to server
ncal sync
```

## Common Commands

```bash
ncal calendars                     # List all calendars
ncal list                          # Today's events
ncal list -t                       # Tomorrow's events
ncal list -d "2026-03-22"          # Specific date
ncal list --range "2026-03-22" "2026-03-25"  # Date range
ncal show "meeting"                # Show event details
ncal add "Event Title" -s "START" -e "END"  # Create event (always include both)
ncal remove "uid"                  # Remove event by UID
ncal sync                          # Sync from server
```

## Troubleshooting

- No events showing? Run `ncal sync`
- Calendar not found? Run `ncal calendars` to see available names
- Timezone issues? Use `-05:00` format, not `+0500`

For detailed documentation, see `REFERENCE.md`.
