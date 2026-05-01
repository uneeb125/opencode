#!/usr/bin/env python3
"""Main entry point for the autoscheduler skill commands."""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

import init
import import_log
import sync
import analyze
import plan
import commit
import schedule_tasks


def print_help():
    print("""AutoScheduler - AI-Powered Automatic Scheduling

Usage: /autoscheduler <command> [args]

Commands:
  init                    Initialize database and configuration
  import-log <path>       Import Simple Tracker CSV export
  sync                    Sync tasks from ntasks and events from ncal
  analyze                 Run statistical analysis on historical data
  plan [YYYY-MM-DD]       Generate AI schedule draft (default: today)
  commit [YYYY-MM-DD]     Push approved plan to ncal Generated calendar
  schedule-tasks [args]   Schedule ntasks items as ncal events (dry-run by default)
  schedule [args]         Alias for schedule-tasks
  stats [activity]        Show historical stats for activities
  suggest-break           Quick recommendation based on today's state
  reconcile [YYYY-MM-DD]  Compare planned vs actual
  help                    Show this help message

Quick Start:
  /autoscheduler init
  /autoscheduler import-log ~/Downloads/tracker_export.csv
  /autoscheduler sync
  /autoscheduler analyze
  /autoscheduler plan
  /autoscheduler commit

Schedule Tasks:
  /autoscheduler schedule-tasks -c Tasks -d 2026-04-27
  /autoscheduler schedule-tasks -c Tasks -d 2026-04-27 --commit
""")


def main():
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    if command == "init":
        init.main()
    elif command == "import-log":
        if args:
            sys.argv = [sys.argv[0], args[0]]
            import_log.main()
        else:
            print("Usage: /autoscheduler import-log <csv_path>")
    elif command == "sync":
        sync.main()
    elif command == "analyze":
        analyze.main()
    elif command == "plan":
        if args:
            sys.argv = [sys.argv[0], args[0]]
        else:
            sys.argv = [sys.argv[0]]
        plan.main()
    elif command == "commit":
        if args:
            sys.argv = [sys.argv[0], args[0]]
        else:
            sys.argv = [sys.argv[0]]
        commit.main()
    elif command in ("schedule-tasks", "schedule"):
        sys.argv = [sys.argv[0]] + args
        schedule_tasks.main()
    elif command == "stats":
        print("Stats command not yet implemented. Use /autoscheduler analyze for now.")
    elif command == "suggest-break":
        print("Suggest-break command not yet implemented.")
    elif command == "reconcile":
        print("Reconcile command not yet implemented.")
    elif command in ("help", "--help", "-h"):
        print_help()
    else:
        print(f"Unknown command: {command}")
        print_help()


if __name__ == "__main__":
    main()
