#!/usr/bin/env python3
"""
BMW Plant Efficiency Dashboard v2
Fixed: real insights, query builder, computed correlations
"""

import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="BMW Plant Insights", page_icon="🏭", layout="wide")

def get_db_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "plant_data.db")

def load_table(table):
    conn = sqlite3.connect(get_db_path())
    try:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
    finally:
        conn.close()
    return df

def load_data():
    data = {}
    for table in ["machines", "production_events", "hourly_metrics", "line_stats", "correlations"]:
        try:
            data[table] = load_table(table)
        except:
            data[table] = pd.DataFrame()
    
    if "production_events" in data and not data["production_events"].empty:
        data["production_events"]["timestamp"] = pd.to_datetime(data["production_events"]["timestamp"])
    if "hourly_metrics" in data and not data["hourly_metrics"].empty:
        data["hourly_metrics"]["hour"] = pd.to_datetime(data["hourly_metrics"]["hour"])
    
    return data

def page_overview(data):
    st.title("🏭 Plant Overview")
    prod = data.get("production_events", pd.DataFrame())
    hourly = data.get("hourly_metrics", pd.DataFrame())
    lines = data.get("line_stats", pd.DataFrame())
    
    if prod.empty:
        st.warning("No data")
        return
    
    total = prod["units_produced"].sum()
    downtime = prod["downtime_flag"].sum()
    events = len(prod)
    avg_oee = hourly["oee"].mean() if not hourly.empty else 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Output", f"{total:,}")
    c2.metric("Downtime", f"{downtime} ({downtime/events:.1%})")
    c3.metric("Events", f"{events:,}")
    c4.metric("OEE", f"{avg_oee:.1%}")
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Daily Output")
        daily =prod.groupby(prod["timestamp"].dt.date)["units_produced"].sum()
        if not daily.empty:
            st.line_chart(daily)
    with c2:
        st.subheader("By Line")
        if not lines.empty:
            st.dataframe(lines[["line_id", "units_produced", "availability", "oee"]], hide_index=True)

def page_drilldown(data):
    st.title("🔧 Machine Analysis")
    prod = data.get("production_events", pd.DataFrame())
    machines = data.get("machines", pd.DataFrame())
    
    if prod.empty:
        st.warning("No data")
        return
    
    machines_list = prod["machine_id"].unique()
    selected = st.selectbox("Machine", machines_list)
    
    m = prod[prod["machine_id"] == selected]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Output", m["units_produced"].sum())
    c2.metric("Downtime", m["downtime_flag"].sum())
    c3.metric("Avg Cycle", f"{m['cycle_time'].mean():.1f}s")
    
    # Compute actual metrics from data
    downtimes = m[m["downtime_flag"] == 1]
    if not downtimes.empty:
        st.subheader("Downtime Events")
        st.dataframe(downtimes[["timestamp", "downtime_reason"]].head(10), hide_index=True)

def page_insights(data):
    st.title("💡 Computed Insights")
    prod = data.get("production_events", pd.DataFrame())
    hourly = data.get("hourly_metrics", pd.DataFrame())
    corr_db = data.get("correlations", pd.DataFrame())
    
    if prod.empty:
        st.warning("No data")
        return
    
    # Real computed insights
    st.subheader("🔗 From Actual Data")
    
    # 1. Downtime by machine
    dt_by_machine = prod.groupby("machine_id")["downtime_flag"].sum().sort_values(ascending=False)
    st.write("**Downtime count by machine:**")
    for mach, count in dt_by_machine.head(5).items():
        st.write(f"  • {mach}: {count} events")
    
    # 2. Output by machine
    out_by_machine = prod.groupby("machine_id")["units_produced"].sum().sort_values(ascending=False)
    st.write("**Output by machine:**")
    for mach, count in out_by_machine.head(5).items():
        st.write(f"  • {mach}: {count:,} units")
    
    # 3. Shift analysis
    prod["shift"] = prod["timestamp"].dt.hour.apply(lambda h: "Day" if h < 14 else "Night")
    shift_output = prod.groupby("shift")["units_produced"].sum()
    st.write("**Day vs Night shift:**")
    for shift, count in shift_output.items():
        st.write(f"  • {shift}: {count:,} units")
    
    # 4. OEE by line
    if not hourly.empty:
        line_oee = hourly.groupby("line_id")["oee"].mean().sort_values(ascending=False)
        st.write("**OEE by line:**")
        for line, oee in line_oee.items():
            st.write(f"  • {line}: {oee:.1%}")
    
    # 5. Compute actual correlation
    if not hourly.empty:
        st.divider()
        st.subheader("📊 Correlation: Cycle Time vs Defects")
        
        corr_df = hourly[["cycle_time", "defect_count"]].dropna()
        if len(corr_df) > 2:
            corr = corr_df["cycle_time"].corr(corr_df["defect_count"])
            st.write(f"Pearson correlation: **{corr:.3f}**")
            
            if abs(corr) > 0.5:
                st.success("Strong correlation detected")
            elif abs(corr) > 0.3:
                st.info("Moderate correlation")
            else:
                st.write("Weak/no correlation in synthetic data")
    
    # Recommendations based on data
    st.divider()
    st.subheader("🎯 Actionable Findings")
    
    worst_machine = dt_by_machine.idxmax()
    worst_count = dt_by_machine.max()
    st.write(f"• **{worst_machine}** has highest downtime ({worst_count} events) — investigate maintenance schedule")
    
    best_line = line_oee.idxmax() if not line_oee.empty else "N/A"
    st.write(f"• **{best_line}** is best performing line by OEE")

def page_query():
    st.title("🔍 Query Builder")
    st.markdown("Write SQL to explore the data:")
    
    query = st.text_area("SQL Query", "SELECT line_id, SUM(units_produced) as total FROM production_events GROUP BY line_id", height=100)
    
    if st.button("Run Query"):
        try:
            conn = sqlite3.connect(get_db_path())
            result = pd.read_sql(query, conn)
            conn.close()
            st.dataframe(result, use_container_width=True)
            st.write(f"_{len(result)} rows_")
        except Exception as e:
            st.error(f"Error: {e}")

def main():
    data = load_data()
    
    if not data.get("production_events", pd.DataFrame()).empty:
        st.sidebar.title("🏭 BMW Plant")
        st.sidebar.markdown(f"**{len(data['production_events'])} events loaded**")
        
        page = st.sidebar.radio("Navigate", ["Overview", "Machine Analysis", "Computed Insights", "Query Builder"])
        
        if page == "Overview":
            page_overview(data)
        elif page == "Machine Analysis":
            page_drilldown(data)
        elif page == "Computed Insights":
            page_insights(data)
        elif page == "Query Builder":
            page_query()
    else:
        st.error("No data found. Generate data first.")

if __name__ == "__main__":
    main()