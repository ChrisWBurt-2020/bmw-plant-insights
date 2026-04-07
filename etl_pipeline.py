#!/usr/bin/env python3
"""
BMW Plant ETL Pipeline - Simplified
"""

import pandas as pd
import sqlite3
import os

OUTPUT_DIR = "/home/debian/testproj/bmw-plant-insights"
DB_PATH = os.path.join(OUTPUT_DIR, "plant_data.db")

def main():
    print("Running ETL pipeline...")
    conn = sqlite3.connect(DB_PATH)
    
    production = pd.read_sql("SELECT * FROM production_events", conn)
    quality = pd.read_sql("SELECT * FROM quality_events", conn)
    machines = pd.read_sql("SELECT * FROM machines", conn)
    conn.close()
    
    # Convert timestamps
    production["timestamp"] = pd.to_datetime(production["timestamp"])
    quality["timestamp"] = pd.to_datetime(quality["timestamp"])
    
    # Compute hourly metrics
    prod = production.copy()
    prod["hour"] = prod["timestamp"].dt.floor("h")
    
    hourly = prod.groupby(["hour", "machine_id"]).agg({
        "units_produced": "sum",
        "cycle_time": "mean",
        "downtime_flag": "sum"
    }).reset_index()
    
    hourly.rename(columns={"downtime_flag": "downtime_events"}, inplace=True)
    
    # Merge machine capacity
    hourly = hourly.merge(machines[["machine_id", "capacity", "line_id"]], on="machine_id")
    
    # Calculate OEE proxy components
    hourly["availability"] = (60 - hourly["downtime_events"]) / 60
    hourly["ideal_units"] = hourly["capacity"]
    hourly["performance"] = (hourly["units_produced"] / hourly["ideal_units"]).clip(0, 1.2)
    
    # Quality from quality table
    qual = quality.copy()
    qual["hour"] = qual["timestamp"].dt.floor("h")
    qual_hourly = qual.groupby(["hour", "machine_id"])["defect_count"].sum().reset_index()
    
    hourly = hourly.merge(qual_hourly, on=["hour", "machine_id"], how="left")
    hourly["defect_count"] = hourly["defect_count"].fillna(0)
    
    total = hourly["units_produced"] + hourly["defect_count"]
    total = total.replace(0, 1)
    hourly["quality"] = hourly["units_produced"] / total
    
    # OEE
    hourly["oee"] = hourly["availability"] * hourly["performance"] * hourly["quality"]
    
    # Line stats
    line_stats = hourly.groupby("line_id").agg({
        "units_produced": "sum",
        "downtime_events": "sum",
        "oee": "mean"
    }).reset_index()
    
    line_stats["total_slots"] = len(hourly) * 60
    line_stats["availability"] = (line_stats["total_slots"] - line_stats["downtime_events"]) / line_stats["total_slots"]
    
    # Correlations
    correlations = []
    corr_ct = hourly["cycle_time"].corr(hourly["defect_count"])
    correlations.append({"metric": "cycle_time_vs_defects", "correlation": corr_ct, "description": f"Cycle time vs defects: {corr_ct:.2f}"})
    
    # Hourly/daily trends
    prod["hour_of_day"] = prod["timestamp"].dt.hour
    hourly_trends = prod.groupby("hour_of_day").agg({"units_produced": "sum", "downtime_flag": "sum"}).reset_index()
    hourly_trends["downtime_rate"] = hourly_trends["downtime_flag"] / hourly_trends["units_produced"]
    
    prod["date"] = prod["timestamp"].dt.date
    daily_trends = prod.groupby("date").agg({"units_produced": "sum", "downtime_flag": "sum"}).reset_index()
    
    # Save
    conn = sqlite3.connect(DB_PATH)
    hourly.to_sql("hourly_metrics", conn, if_exists="replace", index=False)
    line_stats.to_sql("line_stats", conn, if_exists="replace", index=False)
    pd.DataFrame(correlations).to_sql("correlations", conn, if_exists="replace", index=False)
    hourly_trends.to_sql("hourly_trends", conn, if_exists="replace", index=False)
    daily_trends.to_sql("daily_trends", conn, if_exists="replace", index=False)
    conn.close()
    
    print(f"ETL complete: {len(hourly)} hourly records")
    print(f"Avg OEE: {hourly['oee'].mean():.1%}")
    print("Done!")

if __name__ == "__main__":
    main()