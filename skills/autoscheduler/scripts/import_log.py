#!/usr/bin/env python3
"""Import Simple Tracker CSV exports into the autoscheduler database."""

import csv
import sys
import re
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import get_db, load_config


def parse_datetime(dt_str: str) -> datetime | None:
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str.strip(), fmt)
        except ValueError:
            continue
    return None


def parse_duration(duration_str: str) -> int:
    if not duration_str:
        return 0
    
    parts = duration_str.strip().split(':')
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 60 + int(minutes) + (1 if int(seconds) >= 30 else 0)
    elif len(parts) == 2:
        hours, minutes = parts
        return int(hours) * 60 + int(minutes)
    
    return 0


def extract_resource_costs(comment: str) -> dict[str, int | None]:
    costs: dict[str, int | None] = {"mental": None, "physical": None, "willpower": None}
    
    if not comment:
        return costs
    
    cost_match = re.search(r'cost:\s*m(\d+)\s*p(\d+)\s*w(\d+)', comment, re.IGNORECASE)
    if cost_match:
        costs["mental"] = int(cost_match.group(1))
        costs["physical"] = int(cost_match.group(2))
        costs["willpower"] = int(cost_match.group(3))
    
    return costs


def extract_medication_info(comment: str) -> dict:
    info = {"medication_taken": 0, "medication_type": None, "medication_phase": None}
    
    if not comment:
        return info
    
    if re.search(r'\b(med|medication|stimulant|adderall|ritalin|vyvanse)\b', comment, re.IGNORECASE):
        info["medication_taken"] = 1
        med_match = re.search(r'\b(adderall|ritalin|vyvanse|concerta|focalin)\b', comment, re.IGNORECASE)
        if med_match:
            info["medication_type"] = med_match.group(1).lower()
    
    phase_match = re.search(r'\b(onset|peak|maintenance|crash|coming down)\b', comment, re.IGNORECASE)
    if phase_match:
        info["medication_phase"] = phase_match.group(1).lower()
    
    return info


def extract_state_notes(comment: str) -> dict[str, str | None]:
    states: dict[str, str | None] = {"mental_state": None, "physical_state": None, "willpower_state": None}
    
    if not comment:
        return states
    
    mental_match = re.search(r'mental[:\s]+([^,\n]+)', comment, re.IGNORECASE)
    if mental_match:
        states["mental_state"] = mental_match.group(1).strip()
    
    physical_match = re.search(r'physical[:\s]+([^,\n]+)', comment, re.IGNORECASE)
    if physical_match:
        states["physical_state"] = physical_match.group(1).strip()
    
    willpower_match = re.search(r'willpower[:\s]+([^,\n]+)', comment, re.IGNORECASE)
    if willpower_match:
        states["willpower_state"] = willpower_match.group(1).strip()
    
    return states


def import_csv(file_path: str) -> dict:
    db = get_db()
    cursor = db.cursor()
    count = 0
    unplanned_count = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            activity_name = row.get('activity name', '').strip().strip('"')
            if not activity_name:
                continue
            
            time_started = parse_datetime(row.get('time started', ''))
            time_ended = parse_datetime(row.get('time ended', ''))
            comment = row.get('comment', '').strip().strip('"')
            categories = row.get('categories', '').strip()
            record_tags = row.get('record tags', '').strip()
            duration = row.get('duration', '').strip()
            duration_minutes = parse_duration(duration)
            
            if not duration_minutes and time_started and time_ended:
                duration_minutes = int((time_ended - time_started).total_seconds() / 60)
            
            costs = extract_resource_costs(comment)
            med_info = extract_medication_info(comment)
            states = extract_state_notes(comment)
            
            cursor.execute("""
                INSERT INTO actual_events 
                (activity_name, actual_start, actual_end, actual_duration_minutes,
                 category, tags, comment, mental_cost, physical_cost, willpower_cost,
                 mental_state, physical_state, willpower_state, context_notes, source_file)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                activity_name, time_started, time_ended, duration_minutes,
                categories, record_tags, comment, costs["mental"], costs["physical"], costs["willpower"],
                states["mental_state"], states["physical_state"], states["willpower_state"],
                comment, file_path
            ))
            
            actual_id = cursor.lastrowid
            
            # Check if this was planned by looking for matching planned_event
            cursor.execute("""
                SELECT id FROM planned_events 
                WHERE title LIKE ? 
                AND date(planned_start) = date(?)
                AND ABS(strftime('%s', planned_start) - strftime('%s', ?)) < 3600
            """, (f"%{activity_name}%", time_started, time_started))
            
            planned = cursor.fetchone()
            
            if planned:
                deviation = 0
                if planned["planned_start"] and time_started:
                    planned_start = datetime.strptime(planned["planned_start"], "%Y-%m-%d %H:%M:%S")
                    deviation = int((time_started - planned_start).total_seconds() / 60)
                
                cursor.execute("""
                    INSERT INTO event_mappings 
                    (planned_event_id, actual_event_id, match_confidence, deviation_minutes)
                    VALUES (?, ?, 0.8, ?)
                """, (planned["id"], actual_id, deviation))
            else:
                cursor.execute("""
                    INSERT INTO unplanned_events 
                    (actual_event_id, activity_name, actual_start, actual_end, category, tags, comment)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (actual_id, activity_name, time_started, time_ended, categories, record_tags, comment))
                unplanned_count += 1
            
            # Add resource snapshot with medication info
            if costs["mental"] is not None or costs["physical"] is not None or costs["willpower"] is not None:
                time_of_day = "morning" if time_started and 5 <= time_started.hour < 12 else \
                             "afternoon" if time_started and 12 <= time_started.hour < 17 else \
                             "evening" if time_started and 17 <= time_started.hour < 22 else "night"
                
                cursor.execute("""
                    INSERT INTO resource_snapshots 
                    (snapshot_time, activity_id, mental_level, physical_level, willpower_level,
                     medication_taken, medication_type, medication_phase, time_of_day)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (time_started, actual_id, costs["mental"], costs["physical"], costs["willpower"],
                      med_info["medication_taken"], med_info["medication_type"], med_info["medication_phase"], time_of_day))
            
            count += 1
    
    db.commit()
    db.close()
    
    return {"total": count, "unplanned": unplanned_count}


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: import_log.py <csv_path>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    if not Path(csv_path).exists():
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)
    
    result = import_csv(csv_path)
    print(f"Imported {result['total']} log entries from {csv_path}")
    print(f"  Unplanned events: {result['unplanned']}")
    print("Run /autoscheduler analyze to process and learn patterns.")


if __name__ == "__main__":
    main()
