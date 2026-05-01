#!/usr/bin/env python3
"""Sync tasks from ntasks and events from ncal into the autoscheduler database."""

import hashlib
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import get_db


def parse_ntasks_output(output: str) -> list[dict]:
    tasks = []
    current_calendar = None

    for line in output.strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        cal_match = re.match(r'^Calendar:\s+(.+)$', line)
        if cal_match:
            current_calendar = cal_match.group(1).strip()
            continue

        task_match = re.match(
            r'^-\s+\[([ x])\]\s+(.+?)\s*\|\s*start:\s*([^\|]*?)\s*\|\s*due:\s*([^\|]*?)\s*\|\s*priority:\s*(\d+)\s*\|\s*status:\s*(\w+)',
            line
        )
        if task_match and current_calendar:
            done = task_match.group(1) == 'x'
            title = task_match.group(2).strip()
            start_str = task_match.group(3).strip()
            due_str = task_match.group(4).strip()
            priority = int(task_match.group(5))
            status = task_match.group(6)

            if done or status in ('completed', 'done'):
                continue

            start_date = None
            if start_str and start_str != '-':
                for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
                    try:
                        start_date = datetime.strptime(start_str.strip(), fmt).date()
                        break
                    except ValueError:
                        continue

            due_date = None
            if due_str and due_str != '-':
                for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
                    try:
                        due_date = datetime.strptime(due_str.strip(), fmt).date()
                        break
                    except ValueError:
                        continue

            task_id = f"{current_calendar}_{hashlib.md5(title.encode()).hexdigest()[:8]}"

            tasks.append({
                "id": task_id,
                "tasklist": current_calendar,
                "title": title,
                "notes": "",
                "start": start_date,
                "due": due_date,
                "priority": priority,
                "status": "pending"
            })

    return tasks


def sync_ntasks() -> int:
    db = get_db()
    cursor = db.cursor()
    count = 0

    try:
        result = subprocess.run(
            ["ntasks", "list"],
            capture_output=True, text=True, check=True
        )
        tasks = parse_ntasks_output(result.stdout)

        for task in tasks:
            cursor.execute("SELECT id FROM tasks WHERE task_id = ?", (task["id"],))
            existing = cursor.fetchone()

            if existing:
                cursor.execute("""
                    UPDATE tasks 
                    SET tasklist = ?, title = ?, notes = ?, start_date = ?, due_date = ?, priority = ?, status = 'pending'
                    WHERE task_id = ?
                """, (task["tasklist"], task["title"], task["notes"], task["start"], task["due"], task["priority"], task["id"]))
            else:
                cursor.execute("""
                    INSERT INTO tasks 
                    (task_id, tasklist, title, notes, start_date, due_date, priority, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
                """, (task["id"], task["tasklist"], task["title"], task["notes"], task["start"], task["due"], task["priority"]))
            count += 1

    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not sync ntasks: {e}")

    db.commit()
    db.close()
    return count


def parse_ncal_output(output: str) -> list[dict]:
    events = []
    current_date = None

    for line in output.strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        date_line_match = re.match(r'^(\d{4}-\d{2}-\d{2})$', line)
        if date_line_match:
            current_date = date_line_match.group(1)
            continue

        match = re.match(
            r'^-\s+(.+?)\s*\|\s*([^|]*?)\s*\|\s*(.+?)\s*\|\s*location:\s*[^|]*\|\s*tags:\s*(.*?)$',
            line
        )
        if not match:
            continue

        time_range = match.group(1).strip()
        category = match.group(2).strip()
        title = match.group(3).strip()
        tags = match.group(4).strip()

        time_parts = time_range.split(' - ')
        if len(time_parts) != 2:
            continue
        start_str_raw = time_parts[0].strip()
        end_str_raw = time_parts[1].strip()

        has_date = re.match(r'^\d{4}-\d{2}-\d{2}', start_str_raw)

        if has_date:
            full_start = start_str_raw
            full_end = end_str_raw if re.match(r'^\d{4}-\d{2}-\d{2}', end_str_raw) else f"{current_date or datetime.now().strftime('%Y-%m-%d')} {end_str_raw}"
        elif current_date:
            full_start = f"{current_date} {start_str_raw}"
            full_end = f"{current_date} {end_str_raw}"
        else:
            today = datetime.now().strftime("%Y-%m-%d")
            full_start = f"{today} {start_str_raw}"
            full_end = f"{today} {end_str_raw}"

        start_dt = None
        end_dt = None
        for fmt in ("%Y-%m-%d %I:%M %p",):
            try:
                start_dt = datetime.strptime(full_start, fmt)
                end_dt = datetime.strptime(full_end, fmt)
                if end_dt < start_dt:
                    from datetime import timedelta
                    end_dt = end_dt.replace(day=end_dt.day + 1)
                break
            except ValueError:
                continue

        events.append({
            "title": title,
            "start": start_dt.strftime("%Y-%m-%d %H:%M:%S") if start_dt else "",
            "end": end_dt.strftime("%Y-%m-%d %H:%M:%S") if end_dt else "",
            "calendar": category,
            "is_all_day": False,
            "tags": tags
        })

    return events


def sync_ncal() -> tuple[int, int]:
    db = get_db()
    cursor = db.cursor()
    count = 0
    planned_count = 0

    try:
        result = subprocess.run(
            ["ncal", "list"],
            capture_output=True, text=True, check=True
        )
        events = parse_ncal_output(result.stdout)

        for event in events:
            start_time = None
            end_time = None
            is_all_day = 1 if event["is_all_day"] else 0
            duration_minutes = 0

            if event["start"]:
                try:
                    start_time = datetime.strptime(event["start"], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass

            if event["end"]:
                try:
                    end_time = datetime.strptime(event["end"], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass

            if start_time and end_time:
                duration_minutes = int((end_time - start_time).total_seconds() / 60)

            if start_time and end_time:
                cursor.execute("""
                    INSERT OR REPLACE INTO calendar_events 
                    (calendar, event_uid, title, start_time, end_time, description, location, is_all_day)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (event["calendar"], "", event["title"], start_time, end_time, "", "", is_all_day))
                count += 1

                plan_date = start_time.date()
                cursor.execute("""
                    INSERT OR IGNORE INTO planned_events 
                    (source, source_id, title, planned_start, planned_end, planned_duration_minutes, plan_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("ncal", event["title"], event["title"], start_time, end_time, duration_minutes, plan_date))
                if cursor.rowcount > 0:
                    planned_count += 1

    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not sync ncal: {e}")

    db.commit()
    db.close()
    return count, planned_count


def main() -> None:
    print("Syncing ntasks...")
    task_count = sync_ntasks()
    print(f"  Synced {task_count} pending tasks")

    print("Syncing ncal calendar...")
    event_count, planned_count = sync_ncal()
    print(f"  Synced {event_count} calendar events")
    print(f"  Added {planned_count} planned events")

    print("\nDone! Run /autoscheduler analyze to update statistics.")


if __name__ == "__main__":
    main()
