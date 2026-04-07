# BMW Plant Efficiency Insight System

## The Problem

Battery production generates thousands of data points per hour — machine cycles, quality checks, downtime events. Engineers need to find patterns in that noise to improve output and reduce defects. Right now, that analysis happens in spreadsheets or not at all.

## The Solution

A lightweight decision-support system that:

1. Ingests production data from multiple sources
2. Computes OEE metrics (Availability × Performance × Quality)
3. Finds correlations automatically
4. Exposes a query interface so engineers can explore the data themselves

## What I Built

- **Data Generator**: Creates realistic production events with realistic failure modes
- **ETL Pipeline**: Python → SQLite with computed metrics
- **Dashboard**: Streamlit with four views — Overview, Machine Analysis, Computed Insights, Query Builder
- **Query Interface**: Direct SQL access for custom analysis

## Architecture

```
machines + production_events + quality_events
                ↓
           Python ETL
                ↓
           SQLite
                ↓
        Streamlit UI
```

The data is simulated (30 days, 15 machines, 4 lines), but the pipeline and queries work with real plant data.

## What This Demonstrates

- End-to-end system thinking (not just algorithms)
- Manufacturing KPIs (OEE is the industry standard)
- SQL proficiency for analysis
- Dashboard development
- ETL pipeline design

## Running It

```bash
cd bmw-plant-insights
streamlit run app.py
```

Live at: https://bmw-plant-insights.streamlit.app

## Why This Matters

BMW is ramping battery production. They need people who can connect data systems and find insights. This project shows I can build that foundation — now I need the chance to prove it on real data.