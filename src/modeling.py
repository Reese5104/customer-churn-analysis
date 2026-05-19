"""Train a baseline churn prediction model."""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# --------------------------------------------
# Project paths (ensures reproducibility)
# --------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Input: cleaned dataset from data_cleaning.py
DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed" / "churn_cleaned.csv"

# Output: model evaluation report
DEFAULT_REPORT = PROJECT_ROOT / "reports" / "model_performance.md"


# --------------------------------------------
# Data loading
# --------------------------------------------
def load_data(path: Path = DEFAULT_INPUT) -> pd.DataFrame:
    """
    Load cleaned dataset for model training.

    Ensures the ETL pipeline has already been executed.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found at {path}. Run src/data_cleaning.py first."
        )
    return pd.read_csv(path)


# --------------------------------------------
# Machine learning pipeline builder
# --------------------------------------------
def build_pipeline(
    categorical_features: list[str],
    numeric_features: list[str],
) -> Pipeline:
    """
    Build a preprocessing + modeling pipeline.

    Steps:
    - OneHotEncode categorical variables (convert categories → numeric)
    - Standardize numeric variables (mean=0, variance=1)
    - Train Logistic Regression model
    """

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_features,
            ),
            (
                "numeric",
                StandardScaler(),
                numeric_features,
            ),
        ],
        sparse_threshold=0.0,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",  # handles churn class imbalance
                    solver="liblinear",
                ),
            ),
        ]
    )


# --------------------------------------------
# Model training + evaluation
# --------------------------------------------
def train_model(df: pd.DataFrame) -> tuple[str, float]:
    """
    Train a churn prediction model and evaluate performance.

    Returns:
        classification_report (text)
        ROC AUC score (float)
    """

    # Target variable (what we are predicting)
    target = "churn_flag"

    # Columns excluded from features
    excluded = {"customer_id", "churn", target}

    # Numeric features used directly in model
    numeric_features = [
        "senior_citizen",
        "tenure",
        "monthly_charges",
        "total_charges",
        "avg_charge_per_tenure_month",
    ]

    # All remaining columns (excluding target + numeric) treated as categorical
    categorical_features = [
        column
        for column in df.columns
        if column not in excluded and column not in numeric_features
    ]

    # Split features (X) and target (y)
    x = df[categorical_features + numeric_features]
    y = df[target]

    # Train/test split with stratification (preserves churn ratio)
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    # Build full ML pipeline
    pipeline = build_pipeline(categorical_features, numeric_features)

    # Suppress sklearn warnings for cleaner output
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=RuntimeWarning,
            module="sklearn.utils.extmath",
        )

        # Train model
        pipeline.fit(x_train, y_train)

        # Predict class labels
        predictions = pipeline.predict(x_test)

        # Predict probabilities for ROC-AUC
        probabilities = pipeline.predict_proba(x_test)[:, 1]

    # Generate classification report (precision, recall, f1-score)
    report = classification_report(
        y_test,
        predictions,
        target_names=["Retained", "Churned"],
    )

    # Compute ROC-AUC (measures ranking quality of predictions)
    auc = roc_auc_score(y_test, probabilities)

    return report, auc


# --------------------------------------------
# Report writer (Markdown output)
# --------------------------------------------
def write_report(
    classification_text: str,
    auc: float,
    output_path: Path = DEFAULT_REPORT,
) -> None:
    """
    Save model performance results into a Markdown report
    for GitHub / portfolio presentation.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        "# Model Performance\n\n"
        "Baseline model: logistic regression with one-hot encoded categorical features, "
        "standardized numeric features, and balanced class weights.\n\n"
        f"ROC AUC: `{auc:.3f}`\n\n"
        "```text\n"
        f"{classification_text}"
        "```\n",
        encoding="utf-8",
    )


# --------------------------------------------
# CLI argument parsing
# --------------------------------------------
def parse_args() -> argparse.Namespace:
    """
    Allows script to be run flexibly from terminal.
    """
    parser = argparse.ArgumentParser(description="Train a baseline customer churn model.")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to cleaned CSV.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        help="Path for model report.",
    )
    return parser.parse_args()


# --------------------------------------------
# Main pipeline execution
# --------------------------------------------
def main() -> None:
    """
    Full ML pipeline:
    1. Load cleaned dataset
    2. Train model
    3. Evaluate performance
    4. Save report to markdown file
    """

    args = parse_args()

    df = load_data(args.input)
    report, auc = train_model(df)
    write_report(report, auc, args.report)

    # Console output for quick validation
    print(f"ROC AUC: {auc:.3f}")
    print(f"Saved model report to {args.report}")


# Entry point
if __name__ == "__main__":
    main()
