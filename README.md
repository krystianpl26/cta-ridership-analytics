# CTA Ridership Recovery & Service Demand Analytics

## Project Overview
This project is a resume-ready analytics consulting case study that evaluates Chicago Transit Authority (CTA) daily ridership trends from **2001 to 2026**. It transforms raw daily boarding data into clean analytical datasets, summary metrics, and business-focused visualizations.

## Business Problem
Transit agencies need to understand how rider demand changed after the COVID-era disruption and where recovery is strongest. This project analyzes total ridership, bus vs. rail shifts, weekday/weekend dynamics, and seasonality to support service planning decisions.

## Dataset Description
- Source file: `data/raw/CTA_-_Ridership_-_Daily_Boarding_Totals_20260526.csv`
- Grain: Daily observations
- Core fields used:
  - `service_date`
  - `day_type`
  - `bus`
  - `rail_boardings`
  - `total_rides`

## Tools Used
- Python
- pandas
- numpy
- matplotlib
- Jupyter Notebook
- SQL

## Key Analysis Questions
1. How did annual ridership change from 2001 to 2026?
2. How did bus and rail demand evolve over time?
3. How much ridership has recovered since 2020 compared with the 2019 baseline?
4. How do weekday, Saturday, and Sunday/Holiday demand patterns compare (especially 2019 vs. 2025)?
5. What monthly/seasonal trends can inform service planning?

## Project Structure
```
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

deliverables/
├── executive_summary.md
└── figures/
```

## How to Run the Project
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the analysis pipeline from project root:
   ```bash
   python src/cta_analysis.py
   ```
3. Review outputs:
   - Cleaned tables in `data/cleaned/`
   - Figures in `deliverables/figures/`
   - Narrative summary in `deliverables/executive_summary.md`

## Future Improvements
- Add route/station segmentation.
- Build interactive BI dashboard (Tableau/Power BI).
- Add statistical decomposition and forecasting.
- Integrate exogenous factors (weather/events/work patterns).

## Resume Bullets (Polished)
- Built an end-to-end Python analytics pipeline on 25+ years of CTA daily ridership data (2001–2026), including data quality checks, feature engineering, and export-ready summary tables.
- Delivered executive-ready insights on post-pandemic demand recovery by quantifying annual ridership, bus/rail mode share shifts, and 2019 baseline recovery percentages.
- Produced clear, stakeholder-friendly visualizations of seasonal trends and weekday/weekend behavior to inform transit service planning recommendations.


## Streamlit Dashboard
An interactive Streamlit app is included for stakeholder-friendly exploration of ridership recovery and demand patterns.

### What the dashboard shows
- KPI cards for total rides, average daily rides, latest full-year rides, and 2025 recovery vs 2019 baseline.
- Annual ridership trend and bus-vs-rail annual trend.
- Monthly seasonality and day-type demand comparisons.
- Recovery percentage by year (2020 onward) relative to 2019.
- Auto-generated consulting insights and a filtered data preview.

### Run the dashboard
From project root:
```bash
streamlit run streamlit_app/app.py
```
