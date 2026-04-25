#!/usr/bin/env python3
"""Commit an approved daily plan to the khal Generated calendar."""

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


def commit_to_khal(plan: dict, target_date: date, calendar: str = "Generated") -> int:
    """Write plan items to khal calendar."""
    count = 0
    
    for item in plan["items"]:
        if not item["start"] or not item["end"]:
            continue
        
        start_time = datetime.strptime(item["start"], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(item["end"], "%Y-%m-%d %H:%M:%S")
        
        title = item["title"]
        
        resources = item.get("resources", {})
        desc_parts = []
        if resources:
            desc_parts.append(f"Resources: M{resources.get('mental', '?')} P{resources.get('physical', '?')} W{resources.get('willpower', '?')}")
        if item.get("reasoning"):
            desc_parts.append(f"Reasoning: {item['reasoning']}")
        
        description = " :: ".join(desc_parts) if desc_parts else ""
        
        start_str = start_time.strftime("%Y-%m-%d %I:%M %p")
        end_str = end_time.strftime("%Y-%m-%d %I:%M %p")
        
        cmd = [
            "khal", "new",
            "-a", calendar,
            start_str, end_str,
            title
        ]
        
        if description:
            cmd.extend(["::", description])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            count += 1
            print(f"  Created: {start_str}-{end_str} {title}")
        except subprocess.CalledProcessError as e:
            print(f"  Error creating '{title}': {e.stderr}")
    
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
    
    print("\nWriting to khal Generated calendar...")
    count = commit_to_khal(plan, target_date)
    
    if count > 0:
        mark_plan_committed(plan["id"])
        print(f"\nCommitted {count} events.")
        print("Syncing to cloud...")
        try:
            subprocess.run(["vdirsyncer", "sync"], check=True, capture_output=True, text=True)
            print("  Synced to Google Calendar.")
        except subprocess.CalledProcessError as e:
            print(f"  Sync failed: {e.stderr}")
            print("  Run 'vdirsyncer sync' manually.")
    else:
        print("\nNo events were created.")


if __name__ == "__main__":
    main()
