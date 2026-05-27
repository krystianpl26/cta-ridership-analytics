"""CTA Ridership Recovery & Service Demand Analytics.

Run from project root:
    python src/cta_analysis.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# -----------------------------
# Project paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "CTA_-_Ridership_-_Daily_Boarding_Totals_20260526.csv"
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
FIGURES_DIR = PROJECT_ROOT / "deliverables" / "figures"


# -----------------------------
# Data preparation helpers
# -----------------------------
def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names to snake_case style."""
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )
    return df


def add_engineered_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add date and ridership share features."""
    df = df.copy()

    df["year"] = df["service_date"].dt.year
    df["month"] = df["service_date"].dt.month
    df["month_name"] = df["service_date"].dt.month_name()
    df["quarter"] = "Q" + df["service_date"].dt.quarter.astype(str)
    df["day_of_week"] = df["service_date"].dt.day_name()

    day_type_map = {"W": "Weekday", "A": "Saturday", "U": "Sunday/Holiday"}
    df["day_type_label"] = df["day_type"].map(day_type_map).fillna("Unknown")

    df["bus_share"] = np.where(df["total_rides"] > 0, df["bus"] / df["total_rides"], np.nan)
    df["rail_share"] = np.where(
        df["total_rides"] > 0, df["rail_boardings"] / df["total_rides"], np.nan
    )

    return df


def validate_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Check whether bus + rail is close to total rides."""
    out = df.copy()

    numeric_cols = ["bus", "rail_boardings", "total_rides"]

    for col in numeric_cols:
        out[col] = (
            out[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        out[col] = pd.to_numeric(out[col], errors="coerce")

    if out[numeric_cols].isnull().any().any():
        missing_counts = out[numeric_cols].isnull().sum()
        raise ValueError(
            f"Numeric conversion failed. Missing values found:\n{missing_counts}"
        )

    out["components_sum"] = out["bus"] + out["rail_boardings"]
    out["difference"] = out["total_rides"] - out["components_sum"]
    out["difference_pct_of_total"] = np.where(
        out["total_rides"] != 0,
        out["difference"] / out["total_rides"],
        np.nan,
    )

    return out


# -----------------------------
# Aggregations
# -----------------------------
def annual_summary(df: pd.DataFrame) -> pd.DataFrame:
    annual = (
        df.groupby("year", as_index=False)
        .agg(
            total_annual_rides=("total_rides", "sum"),
            average_daily_rides=("total_rides", "mean"),
            total_bus_rides=("bus", "sum"),
            total_rail_rides=("rail_boardings", "sum"),
        )
        .sort_values("year")
    )
    annual["bus_share"] = annual["total_bus_rides"] / annual["total_annual_rides"]
    annual["rail_share"] = annual["total_rail_rides"] / annual["total_annual_rides"]
    return annual


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby(["year", "month", "month_name"], as_index=False)
        .agg(
            monthly_total_rides=("total_rides", "sum"),
            monthly_bus_rides=("bus", "sum"),
            monthly_rail_rides=("rail_boardings", "sum"),
        )
        .sort_values(["year", "month"])
    )
    return monthly


def pandemic_recovery(annual_df: pd.DataFrame, baseline_year: int = 2019) -> pd.DataFrame:
    baseline_value = annual_df.loc[
        annual_df["year"] == baseline_year, "total_annual_rides"
    ].iloc[0]

    recovery = annual_df.loc[annual_df["year"] >= 2020, ["year", "total_annual_rides"]].copy()
    recovery["pct_of_2019"] = (recovery["total_annual_rides"] / baseline_value) * 100
    recovery["pct_change_from_2019"] = ((recovery["total_annual_rides"] - baseline_value) / baseline_value) * 100
    return recovery


def day_type_comparison(df: pd.DataFrame, years=(2019, 2025)) -> pd.DataFrame:
    comp = (
        df[df["year"].isin(years)]
        .groupby(["year", "day_type_label"], as_index=False)
        .agg(avg_rides=("total_rides", "mean"))
    )
    return comp


# -----------------------------
# Charts
# -----------------------------
def create_visualizations(annual: pd.DataFrame, monthly: pd.DataFrame, recovery: pd.DataFrame, day_comp: pd.DataFrame) -> None:
    plt.style.use("ggplot")

    # 1) Annual total rides trend
    plt.figure(figsize=(10, 5))
    plt.plot(annual["year"], annual["total_annual_rides"] / 1_000_000, marker="o")
    plt.title("CTA Annual Total Rides (Millions)")
    plt.xlabel("Year")
    plt.ylabel("Total Rides (Millions)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "annual_total_rides_trend.png", dpi=150)
    plt.close()

    # 2) Bus vs Rail annual trend
    plt.figure(figsize=(10, 5))
    plt.plot(annual["year"], annual["total_bus_rides"] / 1_000_000, marker="o", label="Bus")
    plt.plot(annual["year"], annual["total_rail_rides"] / 1_000_000, marker="o", label="Rail")
    plt.title("CTA Annual Bus vs Rail Rides (Millions)")
    plt.xlabel("Year")
    plt.ylabel("Rides (Millions)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "annual_bus_vs_rail_trend.png", dpi=150)
    plt.close()

    # 3) 2019 vs 2025 day type comparison
    pivot = day_comp.pivot(index="day_type_label", columns="year", values="avg_rides")
    ax = pivot.plot(kind="bar", figsize=(10, 5), rot=0)
    ax.set_title("Average Daily Rides by Day Type: 2019 vs 2025")
    ax.set_xlabel("Day Type")
    ax.set_ylabel("Average Rides")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "day_type_2019_vs_2025.png", dpi=150)
    plt.close()

    # 4) Monthly ridership seasonality (average month across all years)
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    seasonal = monthly.groupby("month_name", as_index=False)["monthly_total_rides"].mean()
    seasonal["month_name"] = pd.Categorical(seasonal["month_name"], categories=month_order, ordered=True)
    seasonal = seasonal.sort_values("month_name")

    plt.figure(figsize=(11, 5))
    plt.plot(seasonal["month_name"], seasonal["monthly_total_rides"] / 1_000_000, marker="o")
    plt.title("CTA Monthly Ridership Seasonality (Average Monthly Rides)")
    plt.xlabel("Month")
    plt.ylabel("Average Monthly Rides (Millions)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "monthly_seasonality.png", dpi=150)
    plt.close()

    # 5) Recovery percentage by year since 2020
    plt.figure(figsize=(10, 5))
    plt.bar(recovery["year"].astype(str), recovery["pct_of_2019"])
    plt.axhline(100, color="black", linestyle="--", linewidth=1)
    plt.title("CTA Recovery vs 2019 Baseline")
    plt.xlabel("Year")
    plt.ylabel("Ridership as % of 2019")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "recovery_pct_by_year.png", dpi=150)
    plt.close()


def main() -> None:
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # 1-3) Load, parse date, clean columns
    df = pd.read_csv(RAW_PATH)
    df = clean_column_names(df)
    df["service_date"] = pd.to_datetime(df["service_date"])
    numeric_cols = ["bus", "rail_boardings", "total_rides"]

    for col in numeric_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
    df[col] = pd.to_numeric(df[col], errors="coerce")

    # 4-5) Validate totals + features
    validated = validate_totals(df)
    enriched = add_engineered_columns(validated)

    # 6-9) Build analytics tables
    annual = annual_summary(enriched)
    monthly = monthly_summary(enriched)
    recovery = pandemic_recovery(annual)
    day_comp = day_type_comparison(enriched, years=(2019, 2025))

    # 10) Export cleaned datasets
    enriched.to_csv(CLEANED_DIR / "cta_ridership_cleaned.csv", index=False)
    annual.to_csv(CLEANED_DIR / "annual_summary.csv", index=False)
    monthly.to_csv(CLEANED_DIR / "monthly_summary.csv", index=False)
    recovery.to_csv(CLEANED_DIR / "pandemic_recovery_summary.csv", index=False)
    day_comp.to_csv(CLEANED_DIR / "day_type_comparison_2019_vs_2025.csv", index=False)

    create_visualizations(annual, monthly, recovery, day_comp)

    max_abs_diff = enriched["difference"].abs().max()
    print("Analysis complete.")
    print(f"Max absolute difference between total_rides and bus+rail: {max_abs_diff:,.2f}")
    print(f"Cleaned outputs written to: {CLEANED_DIR}")
    print(f"Figures written to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
