#!/usr/bin/env python3
"""Generate AI-powered daily schedules using historical data and LLM reasoning."""

import json
import sys
from datetime import datetime, timedelta, time, date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import get_db, load_config


def get_fixed_events(target_date: date) -> list:
    """Get non-Generated calendar events for the target date."""
    db = get_db()
    cursor = db.cursor()
    
    start = datetime.combine(target_date, time.min)
    end = datetime.combine(target_date, time.max)
    
    cursor.execute("""
        SELECT calendar, title, start_time, end_time, is_all_day
        FROM calendar_events
        WHERE start_time >= ? AND start_time < ?
        AND calendar != 'Generated'
        ORDER BY start_time
    """, (start, end))
    
    events = []
    for row in cursor.fetchall():
        events.append({
            "calendar": row["calendar"],
            "title": row["title"],
            "start": row["start_time"],
            "end": row["end_time"],
            "is_all_day": bool(row["is_all_day"])
        })
    
    db.close()
    return events


def get_pending_tasks() -> list:
    """Get pending tasks from ntasks, sorted by priority."""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT tasklist, title, notes, due_date, estimated_duration_minutes
        FROM tasks
        WHERE status = 'pending'
        ORDER BY 
            CASE WHEN due_date IS NULL THEN 1 ELSE 0 END,
            due_date ASC,
            priority DESC
    """)
    
    tasks = []
    for row in cursor.fetchall():
        tasks.append({
            "tasklist": row["tasklist"],
            "title": row["title"],
            "notes": row["notes"],
            "due_date": row["due_date"],
            "estimated_duration": row["estimated_duration_minutes"] or 60
        })
    
    db.close()
    return tasks


def get_activity_stats() -> dict:
    """Get learned statistics for all activities."""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT activity_name, time_of_day, avg_duration_minutes, stddev_duration,
               avg_mental_cost, avg_physical_cost, avg_willpower_cost,
               efficiency_rating, sample_size
        FROM time_patterns
        WHERE pattern_type = 'time_of_day'
    """)
    
    stats = {}
    for row in cursor.fetchall():
        stats[row["activity_name"]] = {
            "category": row["time_of_day"],
            "avg_duration": row["avg_duration_minutes"],
            "stddev": row["stddev_duration"],
            "mental_cost": row["avg_mental_cost"],
            "physical_cost": row["avg_physical_cost"],
            "willpower_cost": row["avg_willpower_cost"],
            "best_time": row["time_of_day"],
            "efficiency": row["efficiency_rating"],
            "sample_size": row["sample_size"]
        }
    
    db.close()
    return stats


def generate_plan_prompt(target_date: date, events: list, tasks: list, stats: dict) -> str:
    """Build a detailed prompt for the LLM to generate a schedule."""
    config = load_config()
    resources = config["daily_resources"]
    med = config["medication"]
    sched = config["scheduling"]
    
    prompt = f"""You are an intelligent scheduling assistant optimizing a daily plan for someone with ADHD who takes short-acting stimulant medication.

## TODAY'S DATE: {target_date.strftime('%A, %B %d, %Y')}

## PERSONAL PROFILE
- Daily Resource Maximums: Mental={resources['mental']}, Physical={resources['physical']}, Willpower={resources['willpower']}
- Buffer between tasks: {sched['buffer_minutes']} minutes
- Recovery after deep work: {sched['recovery_after_deep_work_minutes']} minutes
"""
    
    if med["enabled"]:
        dose_time = med["dose_time"]
        prompt += f"""
## MEDICATION SCHEDULE
- Medication: {med['name']} at {dose_time}
- Pharmacokinetic Profile:
  - Onset: {med['onset_minutes']} min post-dose
  - Peak focus: {med['peak_hours'][0]}-{med['peak_hours'][1]} hours post-dose
  - Effective duration: ~{med['duration_hours']} hours
  - Crash window: {med['crash_hours'][0]}-{med['crash_hours'][1]} hours post-dose
- SCHEDULING RULES:
  - During ONSET (0-1h): Light setup tasks, routines, low-demand activities
  - During PEAK (1-3h): Deep work, complex tasks, creative work
  - During MAINTENANCE (3-5h): Standard productive work, meetings
  - During CRASH (5.5-7h): Admin, chores, low-stimulation tasks, recovery
  - POST-MEDICATION (>7h): Wind-down, preparation, very light tasks only
"""
    
    prompt += f"""
## FIXED CALENDAR EVENTS (cannot be moved)
"""
    
    if not events:
        prompt += "None scheduled.\n"
    else:
        for event in events:
            start_str = event["start"].strftime("%H:%M") if event["start"] else "All day"
            end_str = event["end"].strftime("%H:%M") if event["end"] and not event["is_all_day"] else ""
            prompt += f"- [{start_str}-{end_str}] {event['title']} ({event['calendar']})\n"
    
    prompt += f"""
## PENDING TASKS (to be scheduled)
"""
    
    if not tasks:
        prompt += "No pending tasks.\n"
    else:
        for i, task in enumerate(tasks[:15], 1):  # Limit to top 15
            due_str = f" (Due: {task['due_date']})" if task['due_date'] else ""
            prompt += f"{i}. {task['title']}{due_str}\n"
            if task['notes']:
                prompt += f"   Notes: {task['notes']}\n"
    
    prompt += f"""
## LEARNED ACTIVITY STATISTICS
"""
    
    if not stats:
        prompt += "No historical data available yet. Use general heuristics.\n"
    else:
        for name, s in list(stats.items())[:20]:  # Limit to top 20
            prompt += f"- {name}: avg={s['avg_duration']:.0f}min, best_time={s['best_time']}, "
            prompt += f"costs=M{s['mental_cost']:.0f}/P{s['physical_cost']:.0f}/W{s['willpower_cost']:.0f}\n"
    
    prompt += """
## SCHEDULING CONSTRAINTS & GUIDELINES

1. ENERGY MANAGEMENT:
   - Deep work should be scheduled during peak mental energy
   - Physical activity should be spaced apart (recovery needed)
   - Food events should be planned; expect 20-30 min post-meal drowsiness
   - Willpower depletes through the day; reserve complex decisions for morning

2. ADHD-SPECIFIC:
   - Task switch cost is high; batch similar tasks when possible
   - Include explicit transition buffers between context switches
   - Alternate high-focus and low-focus activities
   - Never schedule back-to-back deep work without a recovery break
   - Account for hyperfocus risk: set explicit end times for engaging tasks

3. MEDICATION-AWARE (if applicable):
   - Peak medication window = maximum cognitive capacity
   - Crash window = reduced executive function; avoid novel/complex tasks
   - Consider medication timing when planning wake-up and bedtime

4. RECOVERY:
   - Schedule decompression after intense activities
   - Menial tasks (face washing, bedtime routine) are required buffers
   - Include at least one extended break (30+ min) if deep work is scheduled

5. OUTPUT FORMAT:
   Return a structured schedule in this exact JSON format:
   
   {
     "reasoning": "Brief explanation of your scheduling strategy",
     "initial_resources": {"mental": X, "physical": Y, "willpower": Z},
     "final_resources": {"mental": X, "physical": Y, "willpower": Z},
     "schedule": [
       {
         "time": "HH:MM-HH:MM",
         "title": "Activity name",
         "type": "fixed|task|routine|meal|recovery|buffer",
         "resources": {"mental": X, "physical": Y, "willpower": Z},
         "reasoning": "Why this activity at this time"
       }
     ]
   }

   Ensure all time blocks cover the entire waking day without gaps.
"""
    
    return prompt


def save_plan(target_date: date, plan_data: dict) -> int:
    """Save a generated plan to the database as a draft."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM daily_plans WHERE plan_date = ? AND status = 'draft'", (target_date,))
    
    cursor.execute("""
        INSERT INTO daily_plans (plan_date, status, reasoning, initial_resources, final_resources)
        VALUES (?, 'draft', ?, ?, ?)
    """, (
        target_date,
        plan_data.get("reasoning", ""),
        json.dumps(plan_data.get("initial_resources", {})),
        json.dumps(plan_data.get("final_resources", {}))
    ))
    
    plan_id = cursor.lastrowid or 0
    
    for item in plan_data.get("schedule", []):
        time_range = item.get("time", "")
        if "-" in time_range:
            start_str, end_str = time_range.split("-")
            start_time = datetime.strptime(f"{target_date} {start_str.strip()}", "%Y-%m-%d %H:%M")
            end_time = datetime.strptime(f"{target_date} {end_str.strip()}", "%Y-%m-%d %H:%M")
        else:
            start_time = None
            end_time = None
        
        cursor.execute("""
            INSERT INTO plan_items (plan_id, item_type, title, start_time, end_time, predicted_resources, reasoning)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            plan_id,
            item.get("type", "task"),
            item.get("title", ""),
            start_time,
            end_time,
            json.dumps(item.get("resources", {})),
            item.get("reasoning", "")
        ))
    
    db.commit()
    db.close()
    return plan_id


def main() -> None:
    if len(sys.argv) > 1:
        target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    else:
        target_date = date.today()
    
    print(f"Generating plan for {target_date}...")
    
    events = get_fixed_events(target_date)
    tasks = get_pending_tasks()
    stats = get_activity_stats()
    
    print(f"  Found {len(events)} fixed events")
    print(f"  Found {len(tasks)} pending tasks")
    print(f"  Found {len(stats)} learned activities")
    
    prompt = generate_plan_prompt(target_date, events, tasks, stats)
    
    print("\n" + "=" * 80)
    print("LLM PROMPT FOR SCHEDULE GENERATION")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    print("\nCopy the above prompt to an LLM to generate the schedule.")
    print("Then paste the JSON response to commit it.")
    print("\nOr use the interactive mode (not yet implemented).")


if __name__ == "__main__":
    main()
