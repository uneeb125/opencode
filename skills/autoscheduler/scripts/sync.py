#!/usr/bin/env python3
"""Sync tasks from gtasks and events from khal into the autoscheduler database."""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import get_db


def get_tasklists() -> list:
    result = subprocess.run(
        ["gtasks", "tasklists", "view"],
        capture_output=True, text=True, check=True
    )
    lists = []
    for line in result.stdout.strip().split('\n'):
        match = re.match(r'\[(\d+)\]\s+(.+)', line.strip())
        if match:
            lists.append(match.group(2).strip())
    return lists


def parse_gtasks_table(output: str, tasklist: str) -> list:
    tasks = []
    lines = output.strip().split('\n')
    
    header_idx = None
    for i, line in enumerate(lines):
        if 'NO' in line and 'TITLE' in line:
            header_idx = i
            break
    
    if header_idx is None:
        return tasks
    
    separator_idx = header_idx + 1
    if separator_idx >= len(lines):
        return tasks
    
    for line in lines[separator_idx + 1:]:
        if not line.strip() or line.strip().startswith('-'):
            continue
        
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 5:
            continue
        
        no = parts[0]
        title = parts[1]
        description = parts[2] if len(parts) > 2 else ""
        status = parts[3].lower() if len(parts) > 3 else "pending"
        due = parts[4] if len(parts) > 4 else ""
        
        if status == "completed":
            continue
        
        due_date = None
        if due and due != "":
            try:
                due_date = datetime.strptime(due, "%d %B %Y").date()
            except ValueError:
                try:
                    due_date = datetime.strptime(due, "%Y-%m-%d").date()
                except ValueError:
                    pass
        
        tasks.append({
            "id": f"{tasklist}_{no}",
            "title": title,
            "notes": description,
            "due": due_date,
            "status": status
        })
    
    return tasks


def sync_gtasks() -> int:
    db = get_db()
    cursor = db.cursor()
    count = 0
    
    try:
        tasklists = get_tasklists()
        
        for tasklist in tasklists:
            result = subprocess.run(
                ["gtasks", "tasks", "view", "-l", tasklist],
                capture_output=True, text=True, check=True
            )
            tasks = parse_gtasks_table(result.stdout, tasklist)
            
            for task in tasks:
                cursor.execute("SELECT id FROM tasks WHERE gtasks_id = ?", (task["id"],))
                existing = cursor.fetchone()
                
                if existing:
                    cursor.execute("""
                        UPDATE tasks 
                        SET tasklist = ?, title = ?, notes = ?, due_date = ?, status = 'pending'
                        WHERE gtasks_id = ?
                    """, (tasklist, task["title"], task["notes"], task["due"], task["id"]))
                else:
                    cursor.execute("""
                        INSERT INTO tasks 
                        (gtasks_id, tasklist, title, notes, due_date, status)
                        VALUES (?, ?, ?, ?, ?, 'pending')
                    """, (task["id"], tasklist, task["title"], task["notes"], task["due"]))
                count += 1
                
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not sync gtasks: {e}")
    
    db.commit()
    db.close()
    return count


def parse_khal_text(output: str) -> list:
    events = []
    current_date = None
    
    for line in output.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        
        date_match = re.match(r'Today,\s+(\d{4}-\d{2}-\d{2})', line)
        if date_match:
            current_date = date_match.group(1)
            continue
        
        date_match = re.match(r'(\w+),\s+(\d{4}-\d{2}-\d{2})', line)
        if date_match:
            current_date = date_match.group(2)
            continue
        
        if line.startswith('→'):
            all_day_match = re.match(r'→(.+?)\s+(.+)', line)
            if all_day_match:
                time_str = all_day_match.group(1).strip()
                title = all_day_match.group(2).strip()
                title = re.sub(r'\s+::\s+.*$', '', title)
                title = re.sub(r'\s+[⟳⏰]+', '', title).strip()
                
                if current_date:
                    events.append({
                        "title": title,
                        "start": f"{current_date} 00:00:00",
                        "end": f"{current_date} 23:59:59",
                        "calendar": "",
                        "is_all_day": True
                    })
        
        timed_match = re.match(r'(\d{2}:\d{2}\s+(?:AM|PM))-(\d{2}:\d{2}\s+(?:AM|PM))\s+(.+)', line)
        if timed_match:
            start_str = timed_match.group(1).strip()
            end_str = timed_match.group(2).strip()
            title = timed_match.group(3).strip()
            title = re.sub(r'\s+::\s+.*$', '', title)
            title = re.sub(r'\s+[⟳⏰]+', '', title).strip()
            
            if current_date:
                start_dt = datetime.strptime(f"{current_date} {start_str}", "%Y-%m-%d %I:%M %p")
                end_dt = datetime.strptime(f"{current_date} {end_str}", "%Y-%m-%d %I:%M %p")
                
                events.append({
                    "title": title,
                    "start": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "end": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "calendar": "",
                    "is_all_day": False
                })
    
    return events


def sync_khal() -> tuple[int, int]:
    db = get_db()
    cursor = db.cursor()
    count = 0
    planned_count = 0
    
    try:
        result = subprocess.run(
            ["khal", "list", "today", "+7d"],
            capture_output=True, text=True, check=True
        )
        events = parse_khal_text(result.stdout)
        
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
            
            if start_time:
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
                """, ("khal", event["title"], event["title"], start_time, end_time, duration_minutes, plan_date))
                if cursor.rowcount > 0:
                    planned_count += 1
                
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not sync khal: {e}")
    
    db.commit()
    db.close()
    return count, planned_count


def main() -> None:
    print("Syncing gtasks...")
    task_count = sync_gtasks()
    print(f"  Synced {task_count} pending tasks")
    
    print("Syncing khal calendar...")
    event_count, planned_count = sync_khal()
    print(f"  Synced {event_count} calendar events")
    print(f"  Added {planned_count} planned events")
    
    print("\nDone! Run /autoscheduler analyze to update statistics.")


if __name__ == "__main__":
    main()
