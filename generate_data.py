#!/usr/bin/env python3
"""
BMW Plant Data Generator - 30 Day Version
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import os

np.random.seed(42)
OUTPUT_DIR = "/home/debian/testproj/bmw-plant-insights"

# 15 machines across 4 lines (BMW battery plant scale)
MACHINES = {
    "M1": {"line": "LINE1", "type": "laser_welder", "capacity": 60},
    "M2": {"line": "LINE1", "type": "press", "capacity": 72},
    "M3": {"line": "LINE1", "type": "assembly", "capacity": 48},
    "M4": {"line": "LINE1", "type": "test_station", "capacity": 60},
    "M5": {"line": "LINE2", "type": "laser_welder", "capacity": 60},
    "M6": {"line": "LINE2", "type": "press", "capacity": 72},
    "M7": {"line": "LINE2", "type": "assembly", "capacity": 48},
    "M8": {"line": "LINE2", "type": "test_station", "capacity": 60},
    "M9": {"line": "LINE3", "type": "coating", "capacity": 50},
    "M10": {"line": "LINE3", "type": "formation", "capacity": 40},
    "M11": {"line": "LINE3", "type": "test_station", "capacity": 60},
    "M12": {"line": "LINE4", "type": "laser_welder", "capacity": 60},
    "M13": {"line": "LINE4", "type": "press", "capacity": 72},
    "M14": {"line": "LINE4", "type": "assembly", "capacity": 48},
    "M15": {"line": "LINE4", "type": "test_station", "capacity": 60},
}

def main():
    print("Generating 30-day plant data...")
    
    # Machines table
    machines = pd.DataFrame([
        {"machine_id": k, "line_id": v["line"], "machine_type": v["type"], "capacity": v["capacity"]}
        for k, v in MACHINES.items()
    ])
    
    # Production events - 30 days, hourly (not minute-level for speed)
    start = datetime(2026, 3, 1, 6)  # March 1
    timestamps = []
    
    for day in range(30):
        for hour in range(6, 18):  # 12-hour shifts
            timestamps.append(start + timedelta(days=day, hours=hour-6))
    
    # Generate production data
    prod_data = []
    for ts in timestamps:
        # Shift factor: second shift slightly less efficient
        shift_factor = 0.95 if ts.hour < 14 else 0.92
        
        for mach_id, props in MACHINES.items():
            # Cycle time with variation
            base_cycle = 3600 / props["capacity"]  # seconds per unit
            cycle = np.random.normal(base_cycle * shift_factor, base_cycle * 0.1)
            
            # Downtime probability (higher at shift changes)
            if ts.hour in [6, 14]:  # Shift start
                down_prob = 0.12
            else:
                down_prob = 0.03
            
            is_down = np.random.choice([0, 1], p=[1 - down_prob, down_prob])
            
            if is_down:
                units = 0
                reason = np.random.choice(["maintenance", "material_wait", "quality_hold", "technical"])
            else:
                units = np.random.poisson(1)
                reason = None
            
            prod_data.append({
                "timestamp": ts,
                "machine_id": mach_id,
                "line_id": props["line"],
                "units_produced": units,
                "cycle_time": round(cycle, 2),
                "downtime_flag": is_down,
                "downtime_reason": reason
            })
    
    production = pd.DataFrame(prod_data)
    
    # Quality events - sample from non-downtime events
    available = production[production["downtime_flag"] == 0]
    quality_sample = available.sample(frac=0.08, random_state=42)
    
    quality = []
    for _, row in quality_sample.iterrows():
        # Defects more likely after recent downtime
        ts = row["timestamp"]
        mach = row["machine_id"]
        
        # Check for recent downtime
        recent_down = production[
            (production["machine_id"] == mach) &
            (production["timestamp"] < ts) &
            (production["timestamp"] > ts - timedelta(hours=2)) &
            (production["downtime_flag"] == 1)
        ]
        
        defect_prob = 0.12 if len(recent_down) > 0 else 0.04
        defect_count = np.random.choice([0, 1, 2], p=[1 - defect_prob, defect_prob * 0.8, defect_prob * 0.2])
        
        defect_type = None
        if defect_count > 0:
            defect_type = np.random.choice(["dimensional", "surface_finish", "assembly_misalign", "seal"])
        
        quality.append({
            "timestamp": ts,
            "machine_id": mach,
            "line_id": row["line_id"],
            "defect_count": defect_count,
            "defect_type": defect_type
        })
    
    quality = pd.DataFrame(quality)
    
    # Save to SQLite
    db_path = os.path.join(OUTPUT_DIR, "plant_data.db")
    conn = sqlite3.connect(db_path)
    machines.to_sql("machines", conn, if_exists="replace", index=False)
    production.to_sql("production_events", conn, if_exists="replace", index=False)
    quality.to_sql("quality_events", conn, if_exists="replace", index=False)
    conn.close()
    
    print(f"Saved: {len(production)} production, {len(quality)} quality events")
    print(f"Total output: {production['units_produced'].sum():,} units")
    print(f"Downtime: {production['downtime_flag'].sum()} events ({production['downtime_flag'].mean()*100:.1f}%)")
    print(f"Defects: {quality['defect_count'].sum()}")
    print("Done!")

if __name__ == "__main__":
    main()