#!/usr/bin/env python3
"""Initialize the autoscheduler database and configuration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import init_database, load_config, save_config, DEFAULT_CONFIG


def run_wizard() -> None:
    print("=" * 60)
    print("AutoScheduler Initialization Wizard")
    print("=" * 60)
    
    config = DEFAULT_CONFIG.copy()
    
    print("\n1. Daily Resource Maximums")
    print("   How much capacity do you have per day? (0-100 scale)")
    config["daily_resources"]["mental"] = int(input("   Mental bandwidth [100]: ") or "100")
    config["daily_resources"]["physical"] = int(input("   Physical energy [80]: ") or "80")
    config["daily_resources"]["willpower"] = int(input("   Willpower [60]: ") or "60")
    
    print("\n2. ADHD Medication (optional)")
    med = input("   Do you take short-acting stimulant medication? (y/n) [n]: ").lower()
    if med == 'y':
        config["medication"]["enabled"] = True
        config["medication"]["name"] = input("   Medication name: ") or "Stimulant"
        config["medication"]["dose_time"] = input("   Typical dose time (HH:MM) [08:00]: ") or "08:00"
        print("   Using default pharmacokinetic profile for short-acting stimulants:")
        print("   - Onset: 45 min, Peak: 1-3h, Duration: 5h, Crash: 5.5-7h")
    
    print("\n3. Scheduling Preferences")
    config["scheduling"]["buffer_minutes"] = int(input("   Buffer between tasks (min) [15]: ") or "15")
    config["scheduling"]["recovery_after_deep_work_minutes"] = int(input("   Recovery after deep work (min) [30]: ") or "30")
    
    print("\nConfiguration saved!")
    save_config(config)


def main() -> None:
    print("Initializing AutoScheduler database...")
    init_database()
    print("Database created successfully.")
    
    if not load_config().get("initialized"):
        run_wizard()
        cfg = load_config()
        cfg["initialized"] = True
        save_config(cfg)
    else:
        print("Already initialized. Run with --reconfigure to reset.")
    
    print("\nDone! You can now use /autoscheduler commands.")


if __name__ == "__main__":
    main()
