#!/usr/bin/env python3
"""Analyze historical data and compute statistical baselines for scheduling."""

import sys
import statistics
import json
from datetime import datetime, time, date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import get_db, load_config


def categorize_time_of_day(dt: datetime | None) -> str:
    if not dt:
        return "unknown"
    h = dt.hour
    if 5 <= h < 12:
        return "morning"
    elif 12 <= h < 17:
        return "afternoon"
    elif 17 <= h < 22:
        return "evening"
    else:
        return "night"


def estimate_resource_costs(activity_name: str, category: str | None) -> tuple[float, float, float]:
    name_lower = activity_name.lower()
    cat_lower = (category or "").lower()
    
    config = load_config()
    cats = config.get("categories", {})
    
    mental = 10.0
    physical = 5.0
    willpower = 10.0
    
    if any(k in name_lower or k in cat_lower for k in cats.get("deep_work", [])):
        mental = 50.0
        willpower = 40.0
    elif any(k in name_lower or k in cat_lower for k in cats.get("physical", [])):
        physical = 50.0
        mental = 15.0
        willpower = 30.0
    elif any(k in name_lower or k in cat_lower for k in cats.get("admin", [])):
        mental = 20.0
        willpower = 15.0
    elif any(k in name_lower or k in cat_lower for k in cats.get("chores", [])):
        physical = 25.0
        willpower = 20.0
    elif any(k in name_lower or k in cat_lower for k in cats.get("food", [])):
        mental = 5.0
        physical = 5.0
        willpower = 0.0
    elif any(k in name_lower or k in cat_lower for k in cats.get("recovery", [])):
        mental = -10.0
        willpower = -15.0
    elif any(k in name_lower or k in cat_lower for k in cats.get("routine", [])):
        mental = 5.0
        physical = 5.0
        willpower = 5.0
    
    return max(0.0, mental), max(0.0, physical), max(0.0, willpower)


def analyze_time_patterns() -> dict:
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT activity_name, actual_duration_minutes, actual_start, 
               category, tags, mental_cost, physical_cost, willpower_cost
        FROM actual_events
        WHERE actual_duration_minutes > 0
        ORDER BY activity_name, actual_start
    """)
    
    activity_data: dict[str, dict] = {}
    for row in cursor.fetchall():
        name = row["activity_name"]
        if name not in activity_data:
            activity_data[name] = {
                "durations": [],
                "morning_durations": [],
                "afternoon_durations": [],
                "evening_durations": [],
                "mental_costs": [],
                "physical_costs": [],
                "willpower_costs": [],
                "categories": set()
            }
        
        data = activity_data[name]
        
        if row["actual_duration_minutes"]:
            data["durations"].append(row["actual_duration_minutes"])
            tod = categorize_time_of_day(row["actual_start"])
            if tod == "morning":
                data["morning_durations"].append(row["actual_duration_minutes"])
            elif tod == "afternoon":
                data["afternoon_durations"].append(row["actual_duration_minutes"])
            elif tod == "evening":
                data["evening_durations"].append(row["actual_duration_minutes"])
        
        if row["mental_cost"] is not None:
            data["mental_costs"].append(row["mental_cost"])
        if row["physical_cost"] is not None:
            data["physical_costs"].append(row["physical_cost"])
        if row["willpower_cost"] is not None:
            data["willpower_costs"].append(row["willpower_cost"])
        
        if row["category"]:
            data["categories"].add(row["category"])
    
    results = {}
    for name, data in activity_data.items():
        if len(data["durations"]) < 1:
            continue
        
        avg_duration = statistics.mean(data["durations"])
        stddev = statistics.stdev(data["durations"]) if len(data["durations"]) > 1 else 0.0
        
        eff_morning = statistics.mean(data["morning_durations"]) if data["morning_durations"] else avg_duration
        eff_afternoon = statistics.mean(data["afternoon_durations"]) if data["afternoon_durations"] else avg_duration
        eff_evening = statistics.mean(data["evening_durations"]) if data["evening_durations"] else avg_duration
        
        categories_str = ",".join(data["categories"])
        est_mental, est_physical, est_willpower = estimate_resource_costs(name, categories_str)
        
        avg_mental = statistics.mean(data["mental_costs"]) if data["mental_costs"] else est_mental
        avg_physical = statistics.mean(data["physical_costs"]) if data["physical_costs"] else est_physical
        avg_willpower = statistics.mean(data["willpower_costs"]) if data["willpower_costs"] else est_willpower
        
        best_time = "morning"
        durations_by_tod = {
            "morning": eff_morning,
            "afternoon": eff_afternoon,
            "evening": eff_evening
        }
        best_time = min(durations_by_tod.keys(), key=lambda k: durations_by_tod[k])
        
        efficiency_rating = 0.0
        if data["mental_costs"]:
            avg_cost = statistics.mean(data["mental_costs"])
            efficiency_rating = max(0.0, 100.0 - avg_cost)
        
        results[name] = {
            "avg_duration": round(avg_duration, 1),
            "stddev": round(stddev, 1),
            "best_time": best_time,
            "efficiency_morning": round(eff_morning, 1),
            "efficiency_afternoon": round(eff_afternoon, 1),
            "efficiency_evening": round(eff_evening, 1),
            "sample_size": len(data["durations"]),
            "avg_mental_cost": round(avg_mental, 1),
            "avg_physical_cost": round(avg_physical, 1),
            "avg_willpower_cost": round(avg_willpower, 1),
            "efficiency_rating": round(efficiency_rating, 1)
        }
        
        cursor.execute("""
            INSERT INTO time_patterns 
            (activity_name, pattern_type, time_of_day, avg_duration_minutes, stddev_duration,
             avg_mental_cost, avg_physical_cost, avg_willpower_cost, efficiency_rating, sample_size)
            VALUES (?, 'time_of_day', ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(activity_name, pattern_type, time_of_day) DO UPDATE SET
                avg_duration_minutes = excluded.avg_duration_minutes,
                stddev_duration = excluded.stddev_duration,
                avg_mental_cost = excluded.avg_mental_cost,
                avg_physical_cost = excluded.avg_physical_cost,
                avg_willpower_cost = excluded.avg_willpower_cost,
                efficiency_rating = excluded.efficiency_rating,
                sample_size = excluded.sample_size,
                last_updated = CURRENT_TIMESTAMP
        """, (name, best_time, avg_duration, stddev, avg_mental, avg_physical, avg_willpower, efficiency_rating, len(data["durations"])))
    
    db.commit()
    db.close()
    return results


def analyze_deviations() -> dict:
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT m.planned_event_id, m.actual_event_id, m.deviation_minutes,
               p.title as planned_title, p.planned_start, p.planned_duration_minutes,
               a.activity_name as actual_name, a.actual_start, a.actual_duration_minutes
        FROM event_mappings m
        JOIN planned_events p ON m.planned_event_id = p.id
        JOIN actual_events a ON m.actual_event_id = a.id
        WHERE m.deviation_minutes IS NOT NULL
    """)
    
    deviations = []
    total_deviation = 0
    count = 0
    
    for row in cursor.fetchall():
        deviations.append({
            "planned": row["planned_title"],
            "actual": row["actual_name"],
            "deviation_minutes": row["deviation_minutes"],
            "planned_duration": row["planned_duration_minutes"],
            "actual_duration": row["actual_duration_minutes"]
        })
        total_deviation += abs(row["deviation_minutes"] or 0)
        count += 1
    
    avg_deviation = total_deviation / count if count > 0 else 0
    
    db.close()
    return {
        "count": count,
        "avg_deviation_minutes": round(avg_deviation, 1),
        "deviations": deviations
    }


def analyze_unplanned() -> dict:
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT u.activity_name, u.category, u.tags, u.comment, u.actual_start, u.actual_end,
               a.actual_duration_minutes
        FROM unplanned_events u
        LEFT JOIN actual_events a ON u.actual_event_id = a.id
        ORDER BY u.actual_start
    """)
    
    unplanned: dict[str, list] = {}
    total_minutes = 0
    count = 0
    
    for row in cursor.fetchall():
        name = row["activity_name"]
        if name not in unplanned:
            unplanned[name] = []
        unplanned[name].append({
            "category": row["category"],
            "duration": row["actual_duration_minutes"],
            "start": row["actual_start"]
        })
        if row["actual_duration_minutes"]:
            total_minutes += row["actual_duration_minutes"]
        count += 1
    
    db.close()
    return {
        "count": count,
        "total_minutes": total_minutes,
        "by_activity": unplanned
    }


def compute_daily_summaries() -> int:
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT date(actual_start) as day,
               SUM(actual_duration_minutes) as total_actual
        FROM actual_events
        WHERE actual_start IS NOT NULL
        GROUP BY date(actual_start)
    """)
    
    actual_by_day = {row["day"]: row["total_actual"] for row in cursor.fetchall()}
    
    cursor.execute("""
        SELECT date(planned_start) as day,
               SUM(planned_duration_minutes) as total_planned
        FROM planned_events
        WHERE planned_start IS NOT NULL
        GROUP BY date(planned_start)
    """)
    
    planned_by_day = {row["day"]: row["total_planned"] for row in cursor.fetchall()}
    
    cursor.execute("""
        SELECT date(u.actual_start) as day,
               SUM(a.actual_duration_minutes) as total_unplanned
        FROM unplanned_events u
        JOIN actual_events a ON u.actual_event_id = a.id
        WHERE u.actual_start IS NOT NULL
        GROUP BY date(u.actual_start)
    """)
    
    unplanned_by_day = {row["day"]: row["total_unplanned"] for row in cursor.fetchall()}
    
    all_days = set(actual_by_day.keys()) | set(planned_by_day.keys())
    
    count = 0
    for day in all_days:
        planned = planned_by_day.get(day, 0) or 0
        actual = actual_by_day.get(day, 0) or 0
        unplanned = unplanned_by_day.get(day, 0) or 0
        
        ratio = round(actual / planned, 2) if planned > 0 else None
        
        cursor.execute("""
            INSERT INTO daily_summaries 
            (date, total_planned_minutes, total_actual_minutes, total_unplanned_minutes, planned_vs_actual_ratio)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                total_planned_minutes = excluded.total_planned_minutes,
                total_actual_minutes = excluded.total_actual_minutes,
                total_unplanned_minutes = excluded.total_unplanned_minutes,
                planned_vs_actual_ratio = excluded.planned_vs_actual_ratio
        """, (day, planned, actual, unplanned, ratio))
        count += 1
    
    db.commit()
    db.close()
    return count


def print_stats(results: dict, deviations: dict, unplanned: dict) -> None:
    print("\n" + "=" * 80)
    print("Activity Analysis Results")
    print("=" * 80)
    
    for name, stats in sorted(results.items(), key=lambda x: x[1]["sample_size"], reverse=True):
        print(f"\n{name}")
        print(f"  Sample size: {stats['sample_size']} occurrences")
        print(f"  Avg duration: {stats['avg_duration']} min (±{stats['stddev']})")
        print(f"  Best time: {stats['best_time']}")
        print(f"  Resource costs: M{stats['avg_mental_cost']} P{stats['avg_physical_cost']} W{stats['avg_willpower_cost']}")
        print(f"  Efficiency: morning={stats['efficiency_morning']}, "
              f"afternoon={stats['efficiency_afternoon']}, evening={stats['efficiency_evening']}")
    
    print("\n" + "=" * 80)
    print("Deviation Analysis (Planned vs Actual)")
    print("=" * 80)
    print(f"  Mapped events: {deviations['count']}")
    print(f"  Avg deviation: {deviations['avg_deviation_minutes']} minutes")
    
    if deviations['deviations']:
        print("\n  Top deviations:")
        sorted_devs = sorted(deviations['deviations'], key=lambda x: abs(x['deviation_minutes']), reverse=True)[:5]
        for d in sorted_devs:
            direction = "late" if d['deviation_minutes'] > 0 else "early"
            print(f"    {d['planned']} → {d['actual']}: {abs(d['deviation_minutes'])} min {direction}")
    
    print("\n" + "=" * 80)
    print("Unplanned Events Analysis")
    print("=" * 80)
    print(f"  Total unplanned: {unplanned['count']} events")
    print(f"  Total time: {unplanned['total_minutes']} minutes")
    
    if unplanned['by_activity']:
        print("\n  By activity:")
        for name, occurrences in sorted(unplanned['by_activity'].items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            total_dur = sum(o['duration'] or 0 for o in occurrences)
            print(f"    {name}: {len(occurrences)}x, {total_dur} min total")


def main() -> None:
    print("Analyzing historical data...")
    
    print("  Computing time patterns...")
    results = analyze_time_patterns()
    print(f"    Analyzed {len(results)} activities")
    
    print("  Analyzing deviations...")
    deviations = analyze_deviations()
    print(f"    Found {deviations['count']} mapped events")
    
    print("  Analyzing unplanned events...")
    unplanned = analyze_unplanned()
    print(f"    Found {unplanned['count']} unplanned events")
    
    print("  Computing daily summaries...")
    summary_count = compute_daily_summaries()
    print(f"    Updated {summary_count} daily summaries")
    
    print_stats(results, deviations, unplanned)
    
    print("\n\nDone! Run /autoscheduler plan to generate a schedule.")


if __name__ == "__main__":
    main()
