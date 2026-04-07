# BMW Plant Efficiency Insight System

## 🎯 What This Is

A manufacturing decision-support system that correlates production signals → identifies inefficiencies → explains them.

Built for BMW Manufacturing Co. battery plant position application.

---

## Architecture

```
Simulated Plant Data → Python ETL → SQLite → Analytics → Streamlit Dashboard → Insights
```

---

## Files

| File | Purpose |
|------|---------|
| `generate_data.py` | Generate 30 days of simulated machine/production data |
| `etl_pipeline.py` | Process raw data → metrics + correlations |
| `app.py` | Streamlit dashboard with insight layer |
| `insights.py` | Rule-based + correlation insight engine |

---

## Quick Start

```bash
# Generate data
python3 generate_data.py

# Run ETL
python3 etl_pipeline.py

# Launch dashboard
streamlit run app.py
```

---

## Dashboard Pages

1. **Plant Overview** — OEE metrics, production trends
2. **Machine Drilldown** — Per-machine cycle time, defects, downtime
3. **Root Cause Insights** — Correlation discoveries
4. **AI Assistant** — Ask "Why is Line 2 underperforming?"

---

## Key Metrics

- **OEE_proxy** = Availability × Performance × Quality
- **Defect Rate** = defects / total_units
- **Downtime %** = downtime_events / total_events
- **Correlation Engine** — downtime → defects, cycle_time → defects

---

## Why This Matters

Maps directly to BMW job requirements:
- ✅ Dashboard development (Quicksight/Grafana alternative shown)
- ✅ Data correlation
- ✅ ETL/ELT pipeline
- ✅ AI tools (LLM insight layer)
- ✅ Process improvement
- ✅ Decision support

---

## Production Data Schema

### machines
| Column | Type | Description |
|--------|------|-------------|
| machine_id | TEXT | M1, M2, ... |
| line_id | TEXT | LINE1, LINE2 |
| machine_type | TEXT | welder, press, assembly, test |
| capacity | INT | units/hour |

### production_events
| Column | Type | Description |
|--------|------|-------------|
| timestamp | DATETIME | minute-level timestamps |
| machine_id | TEXT | FK to machines |
| units_produced | INT | 0 or 1 |
| cycle_time | REAL | seconds |
| downtime_flag | INT | 0/1 |
| downtime_reason | TEXT | null unless downtime |

### quality_events
| Column | Type | Description |
|--------|------|-------------|
| timestamp | DATETIME | |
| machine_id | TEXT | |
| defect_count | INT | Poisson(0.05) |
| defect_type | TEXT | dimensional, surface, assembly |

---

## Demo Credentials

N/A — runs locally on `localhost:8501`

---

## Next Steps

1. Deploy to Streamlit Community Cloud
2. Add real-time LLM explanations
3. Connect to live plant API (if accessible)