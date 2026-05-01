#!/usr/bin/env python3
"""Schedule ntasks items as ncal calendar events with conflict detection."""

import argparse
import re
import subprocess
import sys
from datetime import datetime, timedelta, date, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import load_config


def run_cmd(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout + result.stderr


def parse_ntasks_list(output: str) -> list[dict]:
    tasks = []
    lines = output.strip().split("\n")
    current_task = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("- [ ]"):
            if current_task:
                tasks.append(current_task)
            current_task = parse_task_line(line)
        elif current_task and line.startswith("Default Tasks.org description"):
            current_task["description"] = ""
        elif current_task and not line.startswith("Calendar:") and not line.startswith("- ["):
            current_task["description"] = line

    if current_task:
        tasks.append(current_task)

    return tasks


def parse_task_line(line: str) -> dict:
    task = {"title": "", "start": None, "due": None, "priority": 5, "tags": "", "status": "todo", "description": ""}

    title_match = re.search(r"- \[ \] (.+?) \|", line)
    if title_match:
        task["title"] = title_match.group(1).strip()

    start_match = re.search(r"start:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})", line)
    if start_match:
        task["start"] = datetime.strptime(start_match.group(1), "%Y-%m-%d %H:%M")

    due_match = re.search(r"due:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})", line)
    if due_match:
        task["due"] = datetime.strptime(due_match.group(1), "%Y-%m-%d %H:%M")

    priority_match = re.search(r"priority:\s*(\d+)", line)
    if priority_match:
        task["priority"] = int(priority_match.group(1))

    tags_match = re.search(r"tags:\s*([^|]+)", line)
    if tags_match:
        task["tags"] = tags_match.group(1).strip()

    status_match = re.search(r"status:\s*(\w+)", line)
    if status_match:
        task["status"] = status_match.group(1).strip()

    return task


def upsert_tasks_to_db(tasks: list[dict], tasklist: str) -> None:
    from utils import get_db
    import hashlib
    db = get_db()
    cursor = db.cursor()
    for task in tasks:
        task_id = hashlib.md5(f"{tasklist}:{task['title']}".encode()).hexdigest()
        cursor.execute(
            """
            INSERT INTO tasks (task_id, tasklist, title, notes, start_date, due_date, priority, status, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(task_id) DO UPDATE SET
                start_date = excluded.start_date,
                due_date = excluded.due_date,
                priority = excluded.priority,
                status = excluded.status,
                category = excluded.category
            """,
            (
                task_id,
                tasklist,
                task["title"],
                task.get("description", ""),
                task["start"].date() if task.get("start") else None,
                task["due"].date() if task.get("due") else None,
                task.get("priority", 5),
                task.get("status", "todo"),
                task.get("tags", ""),
            ),
        )
    db.commit()
    db.close()


def parse_ncal_list(output: str, target_date: date) -> list[dict]:
    events = []
    for line in output.strip().split("\n"):
        line = line.strip()
        if not line.startswith("-"):
            continue

        match = re.search(
            r"-\s+(\d{1,2}):(\d{2})\s+(AM|PM)\s+-\s+(\d{1,2}):(\d{2})\s+(AM|PM)\s+\|\s+([^|]+)\s+\|\s+([^|]+)",
            line,
            re.IGNORECASE
        )
        if match:
            sh, sm, sp, eh, em, ep, cal, title = match.groups()
            start = parse_time(int(sh), int(sm), sp, target_date)
            end = parse_time(int(eh), int(em), ep, target_date)
            if end < start:
                end += timedelta(days=1)
            events.append({"start": start, "end": end, "calendar": cal.strip(), "title": title.strip()})
            continue

        match2 = re.search(
            r"-\s+(\d{1,2}):(\d{2})\s+(AM|PM)\s+-\s+--:--\s+\|\s+([^|]+)\s+\|\s+([^|]+)",
            line,
            re.IGNORECASE
        )
        if match2:
            sh, sm, sp, cal, title = match2.groups()
            start = parse_time(int(sh), int(sm), sp, target_date)
            events.append({"start": start, "end": start + timedelta(hours=1), "calendar": cal.strip(), "title": title.strip()})

    return events


def parse_time(hour: int, minute: int, period: str, base_date: date) -> datetime:
    h = hour % 12
    if period.upper() == "PM":
        h += 12
    return datetime.combine(base_date, time(h, minute))


def events_overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
    return start1 < end2 and start2 < end1


def merge_intervals(intervals: list[tuple[datetime, datetime]]) -> list[tuple[datetime, datetime]]:
    if not intervals:
        return []
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = [sorted_intervals[0]]
    for start, end in sorted_intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def find_slot(task_start: datetime, task_due: datetime, duration: timedelta,
               occupied: list[tuple[datetime, datetime]]) -> tuple[datetime, datetime] | None:
    latest_start = task_due - duration
    if latest_start < task_start:
        return None

    merged = merge_intervals(occupied)

    candidate_start = task_start
    for occ_start, occ_end in merged:
        if candidate_start >= latest_start:
            return None
        candidate_end = candidate_start + duration
        if candidate_end <= occ_start:
            return (candidate_start, candidate_end)
        candidate_start = max(candidate_start, occ_end)
        if candidate_start > latest_start:
            return None

    candidate_end = candidate_start + duration
    if candidate_end <= task_due:
        return (candidate_start, candidate_end)

    return None


def estimate_duration(title: str, default_minutes: int) -> timedelta:
    t = title.lower()
    if any(w in t for w in ["email", "message", "text", "call"]):
        return timedelta(minutes=30)
    if any(w in t for w in ["meeting", "sync", "standup", "review"]):
        return timedelta(minutes=60)
    if any(w in t for w in ["gym", "exercise", "workout", "run"]):
        return timedelta(minutes=90)
    if any(w in t for w in ["read", "reading", "study", "research"]):
        return timedelta(minutes=120)
    return timedelta(minutes=default_minutes)


def mark_task_scheduled(title: str, tasklist: str) -> None:
    from utils import get_db
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE tasks SET scheduled_at = CURRENT_TIMESTAMP WHERE title = ? AND tasklist = ?",
        (title, tasklist)
    )
    db.commit()
    db.close()


def build_ncal_command(task: dict, slot_start: datetime, slot_end: datetime, calendar: str) -> list[str]:
    start_str = slot_start.strftime("%Y-%m-%dT%H:%M:%S-05:00")
    end_str = slot_end.strftime("%Y-%m-%dT%H:%M:%S-05:00")

    cmd = ["ncal", "add", task["title"], "-s", start_str, "-e", end_str, "-c", calendar]

    if task.get("description"):
        cmd.extend(["-d", task["description"]])

    tags = task.get("tags", "")
    if tags:
        tags = f"{tags},scheduled"
    else:
        tags = "scheduled"
    cmd.extend(["-t", tags])

    return cmd


def main():
    parser = argparse.ArgumentParser(description="Schedule ntasks as ncal events")
    parser.add_argument("--calendar", "-c", default="Tasks", help="ntasks calendar name")
    parser.add_argument("--target-date", "-d", help="Target date (YYYY-MM-DD), default tomorrow")
    parser.add_argument("--target-cal", "-t", default="Generated", help="ncal calendar to add events to")
    parser.add_argument("--commit", action="store_true", help="Actually create events (default is dry-run)")
    parser.add_argument("--default-duration", type=int, default=60, help="Default task duration in minutes")
    args = parser.parse_args()

    if args.target_date:
        target_date = datetime.strptime(args.target_date, "%Y-%m-%d").date()
    else:
        target_date = date.today() + timedelta(days=1)

    print(f"Fetching tasks from ntasks calendar: '{args.calendar}'")
    ntasks_output = run_cmd(["ntasks", "list", "-c", args.calendar])
    tasks = parse_ntasks_list(ntasks_output)
    upsert_tasks_to_db(tasks, args.calendar)

    target_tasks = [t for t in tasks if (t.get("start") and t["start"].date() == target_date) or (t.get("due") and t["due"].date() == target_date)]

    if not target_tasks:
        print(f"No tasks found for {target_date} in '{args.calendar}'")
        print("\nAll tasks in this calendar:")
        for t in tasks:
            start_str = t["start"].strftime("%Y-%m-%d %H:%M") if t.get("start") else "no start"
            due_str = t["due"].strftime("%Y-%m-%d %H:%M") if t.get("due") else "no due"
            print(f"  - {t['title']} | start: {start_str} | due: {due_str}")
        return

    target_tasks.sort(key=lambda t: (t.get("due") or datetime.max, -t.get("priority", 5)))

    print(f"\nFound {len(target_tasks)} task(s) for {target_date}:\n")

    print(f"Fetching existing events from ncal for {target_date}...")
    ncal_output = run_cmd(["ncal", "list", "-d", target_date.strftime("%Y-%m-%d")])
    existing_events = parse_ncal_list(ncal_output, target_date)

    if existing_events:
        print(f"  {len(existing_events)} existing event(s):\n")
        for ev in existing_events:
            print(f"    [{ev['start'].strftime('%H:%M')}-{ev['end'].strftime('%H:%M')}] {ev['title']} ({ev['calendar']})")
    else:
        print("  No existing events.\n")

    occupied = [(ev["start"], ev["end"]) for ev in existing_events]
    scheduled_tasks = []
    skipped = []

    print("=" * 70)
    print("DRAFT SCHEDULE")
    print("=" * 70)

    for task in target_tasks:
        t_start = task.get("start")
        t_due = task.get("due")
        if not t_start or not t_due:
            print(f"\nTask: {task['title']}")
            print("  SKIPPED: missing start or due date")
            skipped.append(task)
            continue

        duplicate = next((ev for ev in existing_events if ev["title"].strip().lower() == task["title"].strip().lower()), None)
        if duplicate:
            print(f"\nTask: {task['title']}")
            print(f"  SKIPPED: already exists as calendar event [{duplicate['start'].strftime('%H:%M')}-{duplicate['end'].strftime('%H:%M')}] on {duplicate['calendar']}")
            mark_task_scheduled(task["title"], args.calendar)
            skipped.append(task)
            continue

        duration = estimate_duration(task["title"], args.default_duration)
        slot = find_slot(t_start, t_due, duration, occupied)

        print(f"\nTask: {task['title']}")
        print(f"  Window:   {t_start.strftime('%H:%M')} - {t_due.strftime('%H:%M')} (needs {duration.seconds // 60} min)")

        if not slot:
            print("  SKIPPED: no free slot fits within guardrails")
            skipped.append(task)
            continue

        slot_start, slot_end = slot
        print(f"  Scheduled: {slot_start.strftime('%H:%M')} - {slot_end.strftime('%H:%M')}")

        conflicts = []
        for ev in existing_events:
            if events_overlap(slot_start, slot_end, ev["start"], ev["end"]):
                conflicts.append(f"[{ev['start'].strftime('%H:%M')}-{ev['end'].strftime('%H:%M')}] {ev['title']}")
        for other_task, other_slot, _ in scheduled_tasks:
            if events_overlap(slot_start, slot_end, other_slot[0], other_slot[1]):
                conflicts.append(f"[{other_slot[0].strftime('%H:%M')}-{other_slot[1].strftime('%H:%M')}] {other_task['title']}")

        if conflicts:
            print("  ⚠️  CONFLICTS:")
            for c in conflicts:
                print(f"    - {c}")
            skipped.append(task)
            continue

        cmd = build_ncal_command(task, slot_start, slot_end, args.target_cal)
        cmd_str = " ".join(f'"{x}"' if " " in x else x for x in cmd)
        print(f"  Command:  {cmd_str}")

        occupied.append((slot_start, slot_end))
        scheduled_tasks.append((task, (slot_start, slot_end), cmd))

    print("\n" + "=" * 70)
    print(f"Summary: {len(scheduled_tasks)} to schedule, {len(skipped)} skipped")
    print("=" * 70)

    if not args.commit:
        print("\nThis is a DRY RUN. No events were created.")
        print(f"To commit, run:")
        print(f"  /autoscheduler schedule-tasks -c '{args.calendar}' -d {target_date} --commit")
        return

    if not scheduled_tasks:
        print("\nNo events to commit.")
        return

    print("\nCommitting events to ncal...")
    for task, slot, cmd in scheduled_tasks:
        print(f"  Creating: {task['title']} ...", end=" ")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("OK")
            mark_task_scheduled(task["title"], args.calendar)
        else:
            print(f"FAILED: {result.stderr.strip()}")

    print("\nSyncing with server...")
    sync_result = subprocess.run(["ncal", "sync"], capture_output=True, text=True)
    if sync_result.returncode == 0:
        print("Sync complete.")
    else:
        print(f"Sync warning: {sync_result.stderr.strip()}")


if __name__ == "__main__":
    main()
