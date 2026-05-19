"""Clean the IBM Telco churn dataset and create analysis-ready outputs."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed" / "churn_cleaned.csv"
DEFAULT_DB = PROJECT_ROOT / "data" / "processed" / "churn.db"


COLUMN_MAP = {
    "customerID": "customer_id",
    "SeniorCitizen": "senior_citizen",
    "Partner": "partner",
    "Dependents": "dependents",
    "PhoneService": "phone_service",
    "MultipleLines": "multiple_lines",
    "InternetService": "internet_service",
    "OnlineSecurity": "online_security",
    "OnlineBackup": "online_backup",
    "DeviceProtection": "device_protection",
    "TechSupport": "tech_support",
    "StreamingTV": "streaming_tv",
    "StreamingMovies": "streaming_movies",
    "Contract": "contract",
    "PaperlessBilling": "paperless_billing",
    "PaymentMethod": "payment_method",
    "MonthlyCharges": "monthly_charges",
    "TotalCharges": "total_charges",
    "Churn": "churn",
}


def assign_tenure_group(tenure: int) -> str:
    """Group customer tenure into business-friendly lifecycle buckets."""
    if tenure <= 12:
        return "0-12 months"
    if tenure <= 24:
        return "13-24 months"
    if tenure <= 48:
        return "25-48 months"
    return "49+ months"


def clean_telco_data(input_path: Path = DEFAULT_INPUT) -> pd.DataFrame:
    """Load, clean, and enrich the raw Telco churn CSV."""
    if not input_path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {input_path}. Download it from Kaggle and place it there."
        )

    df = pd.read_csv(input_path)
    df = df.rename(columns=COLUMN_MAP)

    df["total_charges"] = pd.to_numeric(df["total_charges"], errors="coerce")
    df["monthly_charges"] = pd.to_numeric(df["monthly_charges"], errors="coerce")
    df["tenure"] = pd.to_numeric(df["tenure"], errors="coerce").astype("Int64")
    df["senior_citizen"] = pd.to_numeric(df["senior_citizen"], errors="coerce").fillna(0).astype(int)

    df = df.dropna(subset=["total_charges", "monthly_charges", "tenure"]).copy()
    df["churn_flag"] = (df["churn"] == "Yes").astype(int)
    df["tenure_group"] = df["tenure"].astype(int).apply(assign_tenure_group)
    df["avg_charge_per_tenure_month"] = df["total_charges"] / df["tenure"].replace(0, pd.NA)
    df["avg_charge_per_tenure_month"] = df["avg_charge_per_tenure_month"].fillna(df["monthly_charges"])

    ordered_columns = [
        "customer_id",
        "gender",
        "senior_citizen",
        "partner",
        "dependents",
        "tenure",
        "tenure_group",
        "phone_service",
        "multiple_lines",
        "internet_service",
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies",
        "contract",
        "paperless_billing",
        "payment_method",
        "monthly_charges",
        "total_charges",
        "avg_charge_per_tenure_month",
        "churn",
        "churn_flag",
    ]
    missing_columns = sorted(set(ordered_columns) - set(df.columns))
    if missing_columns:
        raise KeyError(
            "The cleaned dataset is missing expected columns: "
            f"{missing_columns}. Available columns: {sorted(df.columns)}"
        )

    return df[ordered_columns]


def save_outputs(df: pd.DataFrame, output_path: Path = DEFAULT_OUTPUT, db_path: Path = DEFAULT_DB) -> None:
    """Save the cleaned dataset as CSV and SQLite table."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)
    with sqlite3.connect(db_path) as connection:
        df.to_sql("telco_customers", connection, if_exists="replace", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean IBM Telco customer churn data.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to raw Kaggle CSV.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path for cleaned CSV.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Path for SQLite database.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cleaned = clean_telco_data(args.input)
    save_outputs(cleaned, args.output, args.db)

    churn_rate = cleaned["churn_flag"].mean() * 100
    print(f"Cleaned {len(cleaned):,} customers.")
    print(f"Overall churn rate: {churn_rate:.2f}%")
    print(f"Saved CSV to {args.output}")
    print(f"Saved SQLite database to {args.db}")


if __name__ == "__main__":
    main()
