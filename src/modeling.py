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


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed" / "churn_cleaned.csv"
DEFAULT_REPORT = PROJECT_ROOT / "reports" / "model_performance.md"


def load_data(path: Path = DEFAULT_INPUT) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found at {path}. Run src/data_cleaning.py first.")
    return pd.read_csv(path)


def build_pipeline(categorical_features: list[str], numeric_features: list[str]) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
            ("numeric", StandardScaler(), numeric_features),
        ],
        sparse_threshold=0.0,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", LogisticRegression(max_iter=1000, class_weight="balanced", solver="liblinear")),
        ]
    )


def train_model(df: pd.DataFrame) -> tuple[str, float]:
    target = "churn_flag"
    excluded = {"customer_id", "churn", target}
    numeric_features = ["senior_citizen", "tenure", "monthly_charges", "total_charges", "avg_charge_per_tenure_month"]
    categorical_features = [column for column in df.columns if column not in excluded and column not in numeric_features]

    x = df[categorical_features + numeric_features]
    y = df[target]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    pipeline = build_pipeline(categorical_features, numeric_features)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning, module="sklearn.utils.extmath")
        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)
        probabilities = pipeline.predict_proba(x_test)[:, 1]

    report = classification_report(y_test, predictions, target_names=["Retained", "Churned"])
    auc = roc_auc_score(y_test, probabilities)
    return report, auc


def write_report(classification_text: str, auc: float, output_path: Path = DEFAULT_REPORT) -> None:
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a baseline customer churn model.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to cleaned CSV.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="Path for model report.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = load_data(args.input)
    report, auc = train_model(df)
    write_report(report, auc, args.report)
    print(f"ROC AUC: {auc:.3f}")
    print(f"Saved model report to {args.report}")


if __name__ == "__main__":
    main()
