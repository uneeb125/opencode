#!/usr/bin/env python3
"""Commit an approved daily plan to the ncal Generated calendar."""

import json
import subprocess
import sys
from datetime import datetime, date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import get_db


def get_draft_plan(target_date: date) -> dict | None:
    """Retrieve the draft plan for a specific date."""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT id, reasoning, initial_resources, final_resources
        FROM daily_plans
        WHERE plan_date = ? AND status = 'draft'
        ORDER BY created_at DESC
        LIMIT 1
    """, (target_date,))
    
    plan_row = cursor.fetchone()
    if not plan_row:
        db.close()
        return None
    
    plan_id = plan_row["id"]
    
    cursor.execute("""
        SELECT item_type, title, start_time, end_time, predicted_resources, reasoning
        FROM plan_items
        WHERE plan_id = ?
        ORDER BY start_time
    """, (plan_id,))
    
    items = []
    for row in cursor.fetchall():
        items.append({
            "type": row["item_type"],
            "title": row["title"],
            "start": row["start_time"],
            "end": row["end_time"],
            "resources": json.loads(row["predicted_resources"] or "{}"),
            "reasoning": row["reasoning"]
        })
    
    db.close()
    
    return {
        "id": plan_id,
        "reasoning": plan_row["reasoning"],
        "initial_resources": json.loads(plan_row["initial_resources"] or "{}"),
        "final_resources": json.loads(plan_row["final_resources"] or "{}"),
        "items": items
    }


def check_date_bounds(title: str, start_time: datetime, end_time: datetime, cursor) -> tuple[bool, str]:
    rows = cursor.execute(
        "SELECT start_date, due_date FROM tasks WHERE title LIKE ? AND status = 'pending'",
        (f"%{title}%",)
    ).fetchall()

    if not rows:
        return True, ""

    task_start = None
    task_due = None
    for row in rows:
        start_val = row["start_date"]
        due_val = row["due_date"]
        if start_val:
            task_start = start_val
        if due_val:
            task_due = due_val

    if task_start and start_time < task_start:
        return False, f"starts before task start date ({task_start})"
    if task_due and end_time.date() > task_due:
        return False, f"ends after task due date ({task_due})"

    return True, ""


def commit_to_ncal(plan: dict, target_date: date, calendar: str = "Generated") -> int:
    db = get_db()
    cursor = db.cursor()
    count = 0
    now = datetime.now()
    
    for item in plan["items"]:
        if not item["start"] or not item["end"]:
            continue
        
        start_time = datetime.strptime(item["start"], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(item["end"], "%Y-%m-%d %H:%M:%S")
        
        if start_time <= now:
            print(f"  Skipped '{item['title']}': start time {start_time} is in the past")
            continue

        title = item["title"]

        ok, reason = check_date_bounds(title, start_time, end_time, cursor)
        if not ok:
            print(f"  Skipped '{title}': {reason}")
            continue
        
        resources = item.get("resources", {})
        desc_parts = []
        if resources:
            desc_parts.append(f"Resources: M{resources.get('mental', '?')} P{resources.get('physical', '?')} W{resources.get('willpower', '?')}")
        if item.get("reasoning"):
            desc_parts.append(f"Reasoning: {item['reasoning']}")
        
        description = " :: ".join(desc_parts) if desc_parts else ""
        
        start_iso = start_time.strftime("%Y-%m-%dT%H:%M:%S-05:00")
        end_iso = end_time.strftime("%Y-%m-%dT%H:%M:%S-05:00")
        
        cmd = [
            "ncal", "add",
            "-s", start_iso,
            "-e", end_iso,
            "-c", calendar,
            title
        ]
        
        if description:
            cmd.extend(["--description", description])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            count += 1
            print(f"  Created: {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')} {title}")
        except subprocess.CalledProcessError as e:
            print(f"  Error creating '{title}': {e.stderr}")

    db.close()
    return count


def mark_plan_committed(plan_id: int) -> None:
    """Update plan status to committed."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE daily_plans 
        SET status = 'committed', committed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (plan_id,))
    db.commit()
    db.close()


def main() -> None:
    if len(sys.argv) > 1:
        target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    else:
        target_date = date.today()
    
    print(f"Committing plan for {target_date}...")
    
    plan = get_draft_plan(target_date)
    if not plan:
        print("No draft plan found for this date.")
        print("Run /autoscheduler plan first.")
        sys.exit(1)
    
    print(f"\nPlan: {plan['reasoning'][:100]}...")
    print(f"Items to schedule: {len(plan['items'])}")
    
    print("\nWriting to ncal Generated calendar...")
    count = commit_to_ncal(plan, target_date)
    
    if count > 0:
        mark_plan_committed(plan["id"])
        print(f"\nCommitted {count} events to ncal.")
        print("Syncing to Nextcloud...")
        try:
            subprocess.run(["ncal", "sync"], check=True, capture_output=True, text=True)
            print("  Synced.")
        except subprocess.CalledProcessError as e:
            print(f"  Sync failed: {e.stderr}")
    else:
        print("\nNo events were created.")


if __name__ == "__main__":
    main()
