# CTA Ridership Recovery & Service Demand Analytics

## Project Overview

This project analyzes Chicago Transit Authority (CTA) daily bus and rail ridership from 2001–2026 to evaluate long-term transit demand, post-pandemic recovery, weekday/weekend service patterns, and bus vs. rail usage trends.

The project is framed as a data analytics consulting case study focused on Chicago public transportation and service demand planning. It includes a reproducible Python analysis pipeline, cleaned summary datasets, SQL queries, static visualizations, and an interactive Streamlit dashboard.

## Business Problem

Transit agencies need to understand how rider demand has changed since the COVID-era disruption and where recovery is strongest or weakest. This project analyzes CTA ridership trends to support service planning, commuter demand monitoring, and public-sector decision-making.

Key areas of focus include:

- Long-term ridership trends from 2001–2026
- Post-pandemic recovery compared to the 2019 baseline
- Bus vs. rail ridership recovery
- Weekday, Saturday, and Sunday/Holiday demand patterns
- Monthly and seasonal ridership trends

## Dataset

**Source file:** `data/raw/CTA_-_Ridership_-_Daily_Boarding_Totals_20260526.csv`  
**Grain:** Daily CTA ridership observations  
**Records:** 9,200+ daily records  
**Time period:** 2001–2026

Core fields used:

- `service_date`
- `day_type`
- `bus`
- `rail_boardings`
- `total_rides`

Engineered fields include:

- `year`
- `month`
- `month_name`
- `quarter`
- `day_of_week`
- `day_type_label`
- `bus_share`
- `rail_share`

## Tools Used

- Python
- pandas
- NumPy
- matplotlib
- Streamlit
- Jupyter Notebook
- SQL

## Key Analysis Questions

1. How did annual CTA ridership change from 2001–2026?
2. How much has ridership recovered compared to the 2019 pre-pandemic baseline?
3. Did bus and rail ridership recover at different rates?
4. How do weekday, Saturday, and Sunday/Holiday ridership patterns compare?
5. What monthly or seasonal trends could inform service planning?

## Key Findings

- CTA ridership dropped sharply during the pandemic period and has gradually recovered since 2020.
- 2025 total ridership reached approximately 74% of 2019 ridership levels.
- Bus ridership recovered more strongly than rail, reaching approximately 84% of 2019 levels compared to approximately 63% for rail.
- Weekday ridership remains an important indicator of commuter and school-related travel demand.
- Monthly and day-type trends provide useful signals for transit service planning and demand monitoring.

## Project Structure

```text
data/
├── raw/
└── cleaned/

notebooks/
├── 01_data_cleaning.ipynb
└── 02_exploratory_analysis.ipynb

src/
└── cta_analysis.py

sql/
└── analysis_queries.sql

streamlit_app/
└── app.py

deliverables/
├── executive_summary.md
└── figures/
```

## How to Run the Analysis

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the analysis pipeline from the project root:

```bash
python src/cta_analysis.py
```

Generated outputs:

- Cleaned datasets: `data/cleaned/`
- Figures: `deliverables/figures/`
- Executive summary: `deliverables/executive_summary.md`

## How to Run the Streamlit Dashboard

From the project root, run:

```bash
streamlit run streamlit_app/app.py
```

The dashboard includes:

- Year range and day-type filters
- KPI cards for ridership totals and averages
- Annual ridership trends
- Bus vs. rail comparisons
- Monthly seasonality
- Day-type ridership patterns
- Recovery metrics compared to 2019

## SQL Analysis

The `sql/analysis_queries.sql` file includes example queries for:

- Annual ridership totals
- Monthly ridership trends
- Bus vs. rail totals
- Day-type comparisons
- Pandemic recovery against a 2019 baseline

## Future Improvements

- Add route-level or station-level segmentation.
- Deploy the Streamlit dashboard publicly.
- Add forecasting for future ridership trends.
- Integrate external factors such as weather, major events, gas prices, or remote-work trends.
- Compare CTA recovery patterns with other major U.S. transit systems.
