#!/usr/bin/env python3
"""Database utilities and configuration management for autoscheduler."""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

SKILL_DIR = Path.home() / ".config" / "opencode" / "skills" / "autoscheduler"
DATA_DIR = SKILL_DIR / "data"
DB_PATH = DATA_DIR / "data.db"
CONFIG_PATH = DATA_DIR / "config.json"

DEFAULT_RESOURCES = {
    "mental": 100,
    "physical": 80,
    "willpower": 60
}

DEFAULT_CONFIG = {
    "daily_resources": DEFAULT_RESOURCES.copy(),
    "medication": {
        "enabled": False,
        "name": "",
        "dose_time": "08:00",
        "onset_minutes": 45,
        "peak_hours": [1.0, 3.0],
        "duration_hours": 5.0,
        "crash_hours": [5.5, 7.0]
    },
    "scheduling": {
        "auto_schedule_calendar": "Generated",
        "buffer_minutes": 15,
        "recovery_after_deep_work_minutes": 30,
        "meal_duration_minutes": 30,
        "bedtime_routine_minutes": 45,
        "morning_routine_minutes": 30
    },
    "categories": {
        "deep_work": ["coding", "research", "writing", "studying"],
        "admin": ["email", "calls", "planning", "organizing"],
        "physical": ["gym", "running", "exercise", "walking"],
        "food": ["breakfast", "lunch", "dinner", "snack", "food prep"],
        "recovery": ["meditation", "nap", "rest", "break"],
        "chores": ["cleaning", "laundry", "dishes", "groceries"],
        "routine": ["morning routine", "bedtime routine", "hygiene"]
    }
}


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_db() -> sqlite3.Connection:
    ensure_dirs()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def load_config() -> Dict[str, Any]:
    ensure_dirs()
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        merged = DEFAULT_CONFIG.copy()
        merged.update(config)
        return merged
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    ensure_dirs()
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


def init_database() -> None:
    ensure_dirs()
    conn = get_db()
    cursor = conn.cursor()
    
    # Planned events - what was scheduled
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS planned_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_id TEXT,
            title TEXT NOT NULL,
            planned_start TIMESTAMP,
            planned_end TIMESTAMP,
            planned_duration_minutes INTEGER,
            category TEXT,
            tags TEXT,
            expected_resources TEXT,
            plan_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Actual events - what actually happened (from tracker CSV)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actual_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_name TEXT NOT NULL,
            actual_start TIMESTAMP,
            actual_end TIMESTAMP,
            actual_duration_minutes INTEGER,
            category TEXT,
            tags TEXT,
            comment TEXT,
            mental_cost REAL,
            physical_cost REAL,
            willpower_cost REAL,
            mental_state TEXT,
            physical_state TEXT,
            willpower_state TEXT,
            context_notes TEXT,
            source_file TEXT,
            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Event mappings - links planned to actual
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            planned_event_id INTEGER,
            actual_event_id INTEGER,
            match_confidence REAL,
            deviation_minutes INTEGER,
            deviation_reason TEXT,
            FOREIGN KEY (planned_event_id) REFERENCES planned_events(id),
            FOREIGN KEY (actual_event_id) REFERENCES actual_events(id)
        )
    """)
    
    # Unplanned events - tracker items with no corresponding plan
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS unplanned_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actual_event_id INTEGER NOT NULL,
            activity_name TEXT NOT NULL,
            actual_start TIMESTAMP,
            actual_end TIMESTAMP,
            category TEXT,
            tags TEXT,
            comment TEXT,
            likely_reason TEXT,
            FOREIGN KEY (actual_event_id) REFERENCES actual_events(id)
        )
    """)
    
    # Resource snapshots - state over time with ADHD medication tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resource_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activity_id INTEGER,
            mental_level REAL,
            physical_level REAL,
            willpower_level REAL,
            focus_level REAL,
            context TEXT,
            medication_taken INTEGER DEFAULT 0,
            medication_type TEXT,
            medication_dose_time TIMESTAMP,
            medication_phase TEXT,
            medication_effectiveness REAL,
            time_of_day TEXT
        )
    """)
    
    # Time patterns - learned statistical patterns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS time_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_name TEXT NOT NULL,
            pattern_type TEXT NOT NULL,
            time_of_day TEXT,
            avg_duration_minutes REAL,
            stddev_duration REAL,
            avg_mental_cost REAL,
            avg_physical_cost REAL,
            avg_willpower_cost REAL,
            efficiency_rating REAL,
            sample_size INTEGER,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Daily summaries - aggregate stats per day
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE UNIQUE NOT NULL,
            total_planned_minutes INTEGER,
            total_actual_minutes INTEGER,
            total_unplanned_minutes INTEGER,
            planned_vs_actual_ratio REAL,
            adhd_relevant_insights TEXT,
            medication_effectiveness TEXT,
            energy_curve TEXT
        )
    """)
    
    # Tasks from ntasks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT UNIQUE NOT NULL,
            tasklist TEXT NOT NULL,
            title TEXT NOT NULL,
            notes TEXT,
            start_date DATE,
            due_date DATE,
            priority INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            estimated_duration_minutes INTEGER,
            required_resources TEXT,
            category TEXT,
            scheduled_at TIMESTAMP,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Calendar events from ncal
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            calendar TEXT NOT NULL,
            event_uid TEXT,
            title TEXT NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            description TEXT,
            location TEXT,
            categories TEXT,
            is_all_day INTEGER DEFAULT 0,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_date DATE NOT NULL,
            status TEXT DEFAULT 'draft',
            reasoning TEXT,
            initial_resources TEXT,
            final_resources TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            committed_at TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plan_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL,
            item_type TEXT NOT NULL,
            title TEXT NOT NULL,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            predicted_resources TEXT,
            reasoning TEXT,
            FOREIGN KEY (plan_id) REFERENCES daily_plans(id)
        )
    """)
    
    # Indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_planned_events_date ON planned_events(plan_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_actual_events_time ON actual_events(actual_start)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_mappings_planned ON event_mappings(planned_event_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_mappings_actual ON event_mappings(actual_event_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_resource_snapshots_time ON resource_snapshots(snapshot_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_time_patterns_activity ON time_patterns(activity_name)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_time_patterns_unique ON time_patterns(activity_name, pattern_type, COALESCE(time_of_day, ''))")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_due ON tasks(due_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_calendar_events_time ON calendar_events(start_time, end_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_plans_date ON daily_plans(plan_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_plan_items_plan ON plan_items(plan_id)")

    # Migrate: add scheduled_at to tasks if missing
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [row[1] for row in cursor.fetchall()]
    if "scheduled_at" not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN scheduled_at TIMESTAMP")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()
    print(f"Database initialized at {DB_PATH}")
