"""Clean the IBM Telco churn dataset and create analysis-ready outputs."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


# --------------------------------------------
# Project paths (keeps pipeline reproducible)
# --------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Raw Kaggle dataset input
DEFAULT_INPUT = PROJECT_ROOT / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"

# Cleaned dataset output (used for analysis + modeling)
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed" / "churn_cleaned.csv"

# SQLite database output (for SQL analysis layer)
DEFAULT_DB = PROJECT_ROOT / "data" / "processed" / "churn.db"


# --------------------------------------------
# Column standardization mapping
# --------------------------------------------
# Renames raw dataset columns into analysis-friendly format
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


# --------------------------------------------
# Feature engineering helper
# --------------------------------------------
def assign_tenure_group(tenure: int) -> str:
    """
    Convert numeric tenure into business-friendly customer lifecycle stages.

    This helps segment customers for churn analysis:
    - 0–12 months → new customers (highest churn risk)
    - 13–24 months → early retention stage
    - 25–48 months → stable customers
    - 49+ months → long-term loyal customers
    """
    if tenure <= 12:
        return "0-12 months"
    if tenure <= 24:
        return "13-24 months"
    if tenure <= 48:
        return "25-48 months"
    return "49+ months"


# --------------------------------------------
# Main cleaning pipeline
# --------------------------------------------
def clean_telco_data(input_path: Path = DEFAULT_INPUT) -> pd.DataFrame:
    """
    Load raw dataset, clean it, and engineer features for analysis.

    Steps:
    1. Load CSV
    2. Rename columns for consistency
    3. Convert numeric fields
    4. Handle missing values
    5. Create churn flag
    6. Feature engineering (tenure group, avg charge)
    7. Validate schema
    """

    if not input_path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {input_path}. Download it from Kaggle and place it there."
        )

    # Load raw dataset
    df = pd.read_csv(input_path)

    # Standardize column names
    df = df.rename(columns=COLUMN_MAP)

    # -----------------------------
    # Data type conversions
    # -----------------------------
    df["total_charges"] = pd.to_numeric(df["total_charges"], errors="coerce")
    df["monthly_charges"] = pd.to_numeric(df["monthly_charges"], errors="coerce")
    df["tenure"] = pd.to_numeric(df["tenure"], errors="coerce").astype("Int64")

    # Convert senior citizen flag to integer (0/1)
    df["senior_citizen"] = (
        pd.to_numeric(df["senior_citizen"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    # -----------------------------
    # Missing value handling
    # -----------------------------
    df = df.dropna(subset=["total_charges", "monthly_charges", "tenure"]).copy()

    # -----------------------------
    # Target variable creation
    # -----------------------------
    # Convert churn into binary classification target
    df["churn_flag"] = (df["churn"] == "Yes").astype(int)

    # -----------------------------
    # Feature engineering
    # -----------------------------

    # Segment customers into lifecycle groups
    df["tenure_group"] = df["tenure"].astype(int).apply(assign_tenure_group)

    # Average revenue per month of customer lifetime
    df["avg_charge_per_tenure_month"] = (
        df["total_charges"] / df["tenure"].replace(0, pd.NA)
    )

    # Replace invalid values with monthly charge baseline
    df["avg_charge_per_tenure_month"] = df["avg_charge_per_tenure_month"].fillna(
        df["monthly_charges"]
    )

    # -----------------------------
    # Final column order (analysis-ready dataset)
    # -----------------------------
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

    # Validate schema consistency
    missing_columns = sorted(set(ordered_columns) - set(df.columns))
    if missing_columns:
        raise KeyError(
            "The cleaned dataset is missing expected columns: "
            f"{missing_columns}. Available columns: {sorted(df.columns)}"
        )

    return df[ordered_columns]


# --------------------------------------------
# Output layer (CSV + SQL database)
# --------------------------------------------
def save_outputs(
    df: pd.DataFrame,
    output_path: Path = DEFAULT_OUTPUT,
    db_path: Path = DEFAULT_DB,
) -> None:
    """
    Save cleaned dataset in two formats:
    - CSV for Python/EDA
    - SQLite DB for SQL analysis
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Save cleaned dataset
    df.to_csv(output_path, index=False)

    # Save to SQLite for SQL querying
    with sqlite3.connect(db_path) as connection:
        df.to_sql("telco_customers", connection, if_exists="replace", index=False)


# --------------------------------------------
# CLI argument parsing (flexible execution)
# --------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean IBM Telco customer churn data.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to raw CSV.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Cleaned CSV output path.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite database output path.")
    return parser.parse_args()


# --------------------------------------------
# Main execution pipeline
# --------------------------------------------
def main() -> None:
    """
    Full ETL pipeline:
    1. Load raw data
    2. Clean + feature engineer
    3. Save outputs (CSV + SQL DB)
    4. Print summary stats
    """

    args = parse_args()

    cleaned = clean_telco_data(args.input)
    save_outputs(cleaned, args.output, args.db)

    # Business summary output
    churn_rate = cleaned["churn_flag"].mean() * 100

    print(f"Cleaned {len(cleaned):,} customers.")
    print(f"Overall churn rate: {churn_rate:.2f}%")
    print(f"Saved CSV to {args.output}")
    print(f"Saved SQLite database to {args.db}")


# Entry point
if __name__ == "__main__":
    main()
