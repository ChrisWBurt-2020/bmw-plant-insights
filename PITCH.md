# BMW Plant Efficiency Insight System

## One-Page Pitch

---

### Problem
BMW's battery plant produces fragmented data across 15+ machines and 4 production lines. Engineers struggle to identify root causes of defects and downtime because:

- No unified view of production signals
- Correlations hidden across systems
- Manual analysis too slow for production pace

---

### Solution
**Plant Efficiency Insight System** — a decision-support pipeline that:

1. Aggregates machine/production/quality data
2. Computes real-time OEE metrics
3. Discovers correlations automatically
4. Explains insights in plain language

---

### Key Features

| Feature | Description |
|---------|-------------|
| OEE Dashboard | Availability × Performance × Quality scores per machine/line |
| Correlation Engine | Auto-detects: cycle time → defects, downtime → defects |
| Root Cause Insights | Ranked list of actionable findings |
| AI Assistant | Natural language Q&A over plant data |

---

### Technical Architecture

```
Data Source → Python ETL → SQLite → Analytics → Streamlit Dashboard
```

- **Data**: 7 days × 6 machines × 12 hours = 504 production events
- **Storage**: SQLite (simple, portable, no setup)
- **Visualization**: Streamlit (Python-native, BMW-relevant: Quicksight/Grafana alternative)
- **Insights**: Rule-based correlation engine (LLM-ready)

---

### Relevance to BMW Job Requirements

| BMW Requirement | This Project Demonstrates |
|-----------------|------------------------|
| Dashboard development | Streamlit dashboard with 4 pages |
| Data correlation | Correlation engine discovering cycle_time→defects |
| ETL/ELT pipeline | Python ETL → SQLite → Analytics |
| AI tools | AI Assistant page with Q&A |
| Process improvement | Root cause insights自动生成 |
| Decision support | OEE scores, anomaly detection |

---

### Impact Demonstrated

- **OEE tracking**: Real-time efficiency visibility
- **Correlation discovery**: Automated root cause hints
- **Decision speed**: Seconds to answer "Why is Line 2 underperforming?"
- **Scalability**: Ready for PostgreSQL, LLM integration

---

### Why This Matters for BMW

This project shows I can:

1. **Build end-to-end systems** (not just algorithms)
2. **Map to industrial context** (manufacturing KPIs)
3. **Ship usable tools** (not research demos)
4. **Communicate technically** (engineers → managers)

That's exactly what BMW described: "correlation large data systems together" + "intuitively guide our engineers."

---

### Files

```
bmw-plant-insights/
├── README.md          # This document
├── generate_data.py   # Data generator
├── etl_pipeline.py   # ETL + analytics
├── app.py           # Streamlit dashboard
└── plant_data.db    # SQLite database
```

---

### Running It

```bash
cd bmw-plant-insights
python3 generate_data.py  # Create data
python3 etl_pipeline.py # Run ETL
streamlit run app.py     # Launch dashboard
```

---

### Contact

This project was built for the BMW Manufacturing Co. Production Digitalization Intern application.

**Builder**: Christopher  
**Role**: Systems builder + AI tool fluency  
**Goal**: Demonstrate ability to deliver results inside BMW's digitalization scope

---

*Not a generic AI project — a manufacturing decision system.*