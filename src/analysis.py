"""Create exploratory churn analysis charts."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# Define project root directory (used to build consistent file paths)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Default input dataset path (cleaned dataset from preprocessing step)
DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed" / "churn_cleaned.csv"

# Default output folder for all generated visualizations
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "visualizations"


def load_cleaned_data(path: Path = DEFAULT_INPUT) -> pd.DataFrame:
    """
    Load cleaned churn dataset from CSV.

    Raises:
        FileNotFoundError: if cleaned dataset does not exist (ensures pipeline order is correct)
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found at {path}. Run src/data_cleaning.py first."
        )
    return pd.read_csv(path)


def save_bar_chart(
    df: pd.DataFrame,
    category: str,
    title: str,
    filename: str,
    output_dir: Path,
) -> None:
    """
    Create and save a bar chart showing churn rate by categorical variable.

    Steps:
    1. Group data by category
    2. Calculate churn rate (mean of churn_flag)
    3. Convert to percentage
    4. Sort for better visualization
    """

    grouped = (
        df.groupby(category, as_index=False)["churn_flag"]
        .mean()
        .assign(churn_rate_pct=lambda data: data["churn_flag"] * 100)
        .sort_values("churn_rate_pct", ascending=False)
    )

    # Create figure
    plt.figure(figsize=(9, 5))

    # Plot churn rate by category
    sns.barplot(
        data=grouped,
        x=category,
        y="churn_rate_pct",
        color="#2f6f73",
    )

    # Chart formatting
    plt.title(title)
    plt.xlabel(category.replace("_", " ").title())
    plt.ylabel("Churn Rate (%)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()

    # Save chart to output directory
    plt.savefig(output_dir / filename, dpi=160)
    plt.close()


def create_visualizations(
    df: pd.DataFrame,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> None:
    """
    Generate all churn analysis visualizations.

    Includes:
    - Churn rate by contract type
    - Churn rate by tenure group
    - Monthly charges distribution by churn status
    - Correlation heatmap of numeric features
    """

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set consistent seaborn styling for all plots
    sns.set_theme(style="whitegrid", palette="Set2")

    # -----------------------------
    # 1. Churn by Contract Type
    # -----------------------------
    save_bar_chart(
        df,
        "contract",
        "Churn Rate by Contract Type",
        "churn_rate_by_contract.png",
        output_dir,
    )

    # -----------------------------
    # 2. Churn by Tenure Group
    # -----------------------------
    save_bar_chart(
        df,
        "tenure_group",
        "Churn Rate by Tenure Group",
        "churn_rate_by_tenure.png",
        output_dir,
    )

    # -----------------------------
    # 3. Monthly Charges vs Churn
    # -----------------------------
    plt.figure(figsize=(9, 5))

    sns.boxplot(
        data=df,
        x="churn",
        y="monthly_charges",
        hue="churn",
        palette=["#4c78a8", "#e45756"],
        legend=False,
    )

    plt.title("Monthly Charges by Churn Status")
    plt.xlabel("Churn")
    plt.ylabel("Monthly Charges")
    plt.tight_layout()

    plt.savefig(output_dir / "monthly_charges_vs_churn.png", dpi=160)
    plt.close()

    # -----------------------------
    # 4. Correlation Heatmap
    # -----------------------------
    numeric_columns = [
        "senior_citizen",
        "tenure",
        "monthly_charges",
        "total_charges",
        "avg_charge_per_tenure_month",
        "churn_flag",
    ]

    # Compute correlation matrix
    correlation = df[numeric_columns].corr(numeric_only=True)

    # Plot heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        correlation,
        annot=True,
        cmap="vlag",
        center=0,
        fmt=".2f",
        square=True,
    )

    plt.title("Correlation Heatmap")
    plt.tight_layout()

    # Save heatmap
    plt.savefig(output_dir / "correlation_heatmap.png", dpi=160)
    plt.close()


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for flexible pipeline execution.
    """
    parser = argparse.ArgumentParser(description="Generate churn analysis visualizations.")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to cleaned CSV.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for PNG charts.",
    )
    return parser.parse_args()


def main() -> None:
    """
    Main execution pipeline:
    1. Load cleaned dataset
    2. Generate visualizations
    3. Save outputs to /visualizations
    """
    args = parse_args()

    df = load_cleaned_data(args.input)
    create_visualizations(df, args.output_dir)

    print(f"Saved visualizations to {args.output_dir}")


if __name__ == "__main__":
    main()
