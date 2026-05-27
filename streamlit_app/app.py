"""Streamlit dashboard for CTA ridership analytics.

Run from project root:
    streamlit run streamlit_app/app.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(page_title="CTA Ridership Recovery Dashboard", layout="wide")


def find_cleaned_daily_file() -> Path:
    """Find the cleaned daily CTA file with required columns."""
    preferred = Path("data/cleaned/cta_cleaned.csv")
    if preferred.exists():
        return preferred

    cleaned_dir = Path("data/cleaned")
    if not cleaned_dir.exists():
        raise FileNotFoundError(
            "`data/cleaned/` does not exist. Run `python src/cta_analysis.py` first."
        )

    required_cols = {
        "service_date",
        "day_type",
        "bus",
        "rail_boardings",
        "total_rides",
        "year",
        "month",
        "month_name",
        "day_type_label",
        "bus_share",
        "rail_share",
    }

    for csv_path in sorted(cleaned_dir.glob("*.csv")):
        try:
            sample = pd.read_csv(csv_path, nrows=5)
            if required_cols.issubset(set(sample.columns)):
                return csv_path
        except Exception:
            continue

    raise FileNotFoundError(
        "Could not find a cleaned daily-level CTA CSV with required columns in `data/cleaned/`."
    )


@st.cache_data
def load_data() -> tuple[pd.DataFrame, Path]:
    file_path = find_cleaned_daily_file()
    df = pd.read_csv(file_path, parse_dates=["service_date"])

    # Safety: numeric coercion in case values are stored as text
    for col in ["bus", "rail_boardings", "total_rides", "year", "month", "bus_share", "rail_share"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["service_date", "year", "month", "total_rides"])
    df["year"] = df["year"].astype(int)
    df["month"] = df["month"].astype(int)
    return df, file_path


def build_insights(df_filtered: pd.DataFrame, annual_all: pd.DataFrame) -> list[str]:
    insights = []

    # Recovery insight
    if {2019, 2025}.issubset(set(annual_all["year"])):
        rides_2019 = annual_all.loc[annual_all["year"] == 2019, "total_rides"].iloc[0]
        rides_2025 = annual_all.loc[annual_all["year"] == 2025, "total_rides"].iloc[0]
        pct = (rides_2025 / rides_2019) * 100 if rides_2019 > 0 else np.nan
        insights.append(
            f"2025 ridership is {pct:.1f}% of the 2019 baseline, indicating the current recovery level."
        )

    # Mode share insight
    bus_total = df_filtered["bus"].sum()
    rail_total = df_filtered["rail_boardings"].sum()
    total = df_filtered["total_rides"].sum()
    if total > 0:
        bus_share = bus_total / total * 100
        rail_share = rail_total / total * 100
        dominant = "bus" if bus_share >= rail_share else "rail"
        insights.append(
            f"Within the selected filters, {dominant} is the larger mode ({max(bus_share, rail_share):.1f}% share)."
        )

    # Weekday vs weekend insight
    day_avg = df_filtered.groupby("day_type_label", as_index=False)["total_rides"].mean()
    weekday_val = day_avg.loc[day_avg["day_type_label"] == "Weekday", "total_rides"]
    weekend_val = day_avg.loc[day_avg["day_type_label"].isin(["Saturday", "Sunday/Holiday"]), "total_rides"]
    if len(weekday_val) and len(weekend_val):
        weekend_mean = weekend_val.mean()
        ratio = weekday_val.iloc[0] / weekend_mean if weekend_mean > 0 else np.nan
        insights.append(
            f"Average weekday ridership is about {ratio:.2f}x average weekend ridership in the selected period."
        )

    # Leadership monitor insight
    if len(annual_all) >= 2:
        latest_year = annual_all["year"].max()
        prev_year = latest_year - 1
        if prev_year in set(annual_all["year"]):
            latest = annual_all.loc[annual_all["year"] == latest_year, "total_rides"].iloc[0]
            prev = annual_all.loc[annual_all["year"] == prev_year, "total_rides"].iloc[0]
            yoy = ((latest - prev) / prev * 100) if prev > 0 else np.nan
            insights.append(
                f"CTA leadership should monitor year-over-year ridership momentum: {latest_year} is {yoy:+.1f}% vs {prev_year}."
            )

    if not insights:
        insights.append("Not enough data in current filters to compute insights.")

    return insights[:5]


def main() -> None:
    st.title("CTA Ridership Recovery Dashboard")
    st.write(
        "This dashboard analyzes CTA daily bus and rail ridership from 2001–2026, "
        "with a focus on pandemic recovery, bus vs. rail trends, and weekday/weekend service demand."
    )

    df, source_path = load_data()
    st.caption(f"Data source: `{source_path}`")

    # Sidebar filters
    st.sidebar.header("Filters")
    min_year, max_year = int(df["year"].min()), int(df["year"].max())
    selected_years = st.sidebar.slider("Year range", min_year, max_year, (min_year, max_year))

    all_day_types = sorted(df["day_type_label"].dropna().unique().tolist())
    selected_day_types = st.sidebar.multiselect(
        "Day type", options=all_day_types, default=all_day_types
    )

    mode_option = st.sidebar.selectbox("Mode selector", ["Total Rides", "Bus", "Rail"])
    mode_col = {"Total Rides": "total_rides", "Bus": "bus", "Rail": "rail_boardings"}[mode_option]

    # Apply filters
    filtered = df[
        (df["year"].between(selected_years[0], selected_years[1]))
        & (df["day_type_label"].isin(selected_day_types))
    ].copy()

    # KPI cards
    annual_filtered = filtered.groupby("year", as_index=False)[["total_rides", "bus", "rail_boardings"]].sum()
    annual_all = df.groupby("year", as_index=False)["total_rides"].sum()

    total_rides = filtered["total_rides"].sum()
    avg_daily = filtered["total_rides"].mean()

    full_year_counts = filtered.groupby("year")["service_date"].nunique().reset_index(name="days")
    full_years = full_year_counts.loc[full_year_counts["days"] >= 365, "year"]
    if len(full_years) > 0:
        latest_full_year = int(full_years.max())
        latest_full_year_total = annual_filtered.loc[
            annual_filtered["year"] == latest_full_year, "total_rides"
        ].iloc[0]
    else:
        latest_full_year = None
        latest_full_year_total = np.nan

    recovery_2025 = np.nan
    if {2019, 2025}.issubset(set(annual_all["year"])):
        base_2019 = annual_all.loc[annual_all["year"] == 2019, "total_rides"].iloc[0]
        rides_2025 = annual_all.loc[annual_all["year"] == 2025, "total_rides"].iloc[0]
        recovery_2025 = (rides_2025 / base_2019) * 100 if base_2019 > 0 else np.nan

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total rides (selected)", f"{total_rides:,.0f}")
    c2.metric("Average daily rides", f"{avg_daily:,.0f}")
    c3.metric(
        "Latest full-year total rides",
        f"{latest_full_year_total:,.0f}" if pd.notna(latest_full_year_total) else "N/A",
        delta=f"Year {latest_full_year}" if latest_full_year else None,
    )
    c4.metric(
        "2025 vs 2019 baseline",
        f"{recovery_2025:.1f}%" if pd.notna(recovery_2025) else "N/A",
    )

    plt.style.use("ggplot")

    # Annual ridership trend (selected mode)
    st.subheader(f"Annual Ridership Trend ({mode_option})")
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    annual_mode = filtered.groupby("year", as_index=False)[mode_col].sum()
    ax1.plot(annual_mode["year"], annual_mode[mode_col], marker="o")
    ax1.set_xlabel("Year")
    ax1.set_ylabel(mode_option)
    st.pyplot(fig1)

    # Bus vs rail annual
    st.subheader("Bus vs. Rail Annual Ridership Trend")
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(annual_filtered["year"], annual_filtered["bus"], marker="o", label="Bus")
    ax2.plot(annual_filtered["year"], annual_filtered["rail_boardings"], marker="o", label="Rail")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Annual rides")
    ax2.legend()
    st.pyplot(fig2)

    # Monthly seasonality
    st.subheader("Monthly Seasonality (Average Rides by Month)")
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    monthly = filtered.groupby(["month", "month_name"], as_index=False)[mode_col].mean()
    monthly["month_name"] = pd.Categorical(monthly["month_name"], categories=month_order, ordered=True)
    monthly = monthly.sort_values("month")
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(monthly["month_name"], monthly[mode_col], marker="o")
    ax3.set_xlabel("Month")
    ax3.set_ylabel(f"Average {mode_option}")
    ax3.tick_params(axis="x", rotation=45)
    st.pyplot(fig3)

    # Average rides by day type
    st.subheader("Average Rides by Day Type")
    day_type_avg = filtered.groupby("day_type_label", as_index=False)[mode_col].mean()
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    ax4.bar(day_type_avg["day_type_label"], day_type_avg[mode_col])
    ax4.set_xlabel("Day Type")
    ax4.set_ylabel(f"Average {mode_option}")
    st.pyplot(fig4)

    # Recovery vs 2019 from 2020 onward (total rides)
    st.subheader("Recovery Percentage vs 2019 (Years 2020+)" )
    annual_total_all = df.groupby("year", as_index=False)["total_rides"].sum()
    if 2019 in set(annual_total_all["year"]):
        baseline = annual_total_all.loc[annual_total_all["year"] == 2019, "total_rides"].iloc[0]
        recovery = annual_total_all[annual_total_all["year"] >= 2020].copy()
        recovery["pct_of_2019"] = (recovery["total_rides"] / baseline) * 100

        fig5, ax5 = plt.subplots(figsize=(10, 4))
        ax5.bar(recovery["year"].astype(str), recovery["pct_of_2019"])
        ax5.axhline(100, color="black", linestyle="--", linewidth=1)
        ax5.set_xlabel("Year")
        ax5.set_ylabel("% of 2019 ridership")
        st.pyplot(fig5)
    else:
        st.info("2019 baseline not present in data; recovery chart unavailable.")

    # Consulting insights
    st.subheader("Consulting Insights")
    insights = build_insights(filtered, annual_total_all)
    for text in insights:
        st.markdown(f"- {text}")

    # Data preview
    st.subheader("Data Preview")
    st.dataframe(filtered.head(20), use_container_width=True)


if __name__ == "__main__":
    main()
