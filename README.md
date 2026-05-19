# Customer-churn-analysis
Customer churn analytics project using SQL, Python, and business intelligence techniques. The analysis uses the IBM Telco Customer Churn dataset to identify churn drivers, high-risk customer segments, and practical retention actions for a telecom business.

# Customer Churn Analysis

Resume-quality customer churn analytics project using SQL, Python, and business intelligence techniques. The analysis uses the IBM Telco Customer Churn dataset to identify churn drivers, high-risk customer segments, and practical retention actions for a telecom business.

## Business Objective

Customer acquisition is expensive, so reducing churn can materially improve profitability. This project answers four core business questions:

- Which factors are most strongly associated with churn?
- Which customer segments are at highest risk?
- How do demographics, contracts, tenure, services, and spending relate to churn?
- What targeted actions could reduce churn?

## Dataset

Use the IBM Telco Customer Churn dataset from Kaggle:

https://www.kaggle.com/datasets/blastchar/telco-customer-churn

Place the downloaded CSV here:

```text
data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv
```

The raw dataset is excluded from version control because it is externally sourced.

## Project Structure

```text
customer-churn-analysis/
├── data/
│   ├── raw/
│   └── processed/
├── sql/
│   ├── schema.sql
│   ├── data_cleaning.sql
│   └── business_queries.sql
├── notebooks/
│   └── churn_analysis.ipynb
├── src/
│   ├── data_cleaning.py
│   ├── analysis.py
│   └── modeling.py
├── visualizations/
├── reports/
│   ├── executive_summary.md
│   └── business_recommendations.md
├── README.md
├── requirements.txt
└── .gitignore
```

## How to Run

Create an environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Clean the raw dataset and create a SQLite database:

```bash
python src/data_cleaning.py
```

Generate exploratory charts:

```bash
python src/analysis.py
```

Train an optional baseline churn model:

```bash
python src/modeling.py
```

Run the SQL workflow in SQLite:

```bash
sqlite3 data/processed/churn.db < sql/schema.sql
sqlite3 data/processed/churn.db
```

Inside SQLite, import the raw CSV into `raw_telco`, then run:

```sql
.read sql/data_cleaning.sql
.read sql/business_queries.sql
```

## Methods

- Data cleaning: column standardization, numeric conversion, missing value handling, churn flag creation, tenure grouping, and charge-per-tenure feature engineering.
- SQL analysis: churn rate by contract, tenure, internet service, payment method, senior citizen status, monthly charge bands, and bundled services.
- Python analysis: descriptive statistics, churn segmentation, distribution analysis, visualizations, and optional predictive modeling.
- Modeling: baseline logistic regression with one-hot encoded categorical features and standardized numeric features.

## Expected Portfolio Outputs

- Cleaned analytical dataset in `data/processed/churn_cleaned.csv`
- SQLite database in `data/processed/churn.db`
- SQL queries that answer stakeholder questions
- Visualizations in `visualizations/`
- Executive summary and business recommendations in `reports/`
- Optional churn model performance report in `reports/model_performance.md`

## Key Business Hypotheses

- Month-to-month customers will churn at a materially higher rate than customers on one- or two-year contracts.
- Customers with short tenure will be less retained because they have not yet developed switching costs.
- Electronic check users may have elevated churn risk relative to automatic payment customers.
- High monthly charges without stabilizing services, such as tech support or online security, may indicate a value-perception problem.

## Recommended Next Steps

- Add the raw Kaggle CSV to `data/raw/`.
- Run the cleaning, analysis, and modeling scripts.
- Update the report files with the exact metric values generated from your local run.
- Add final visualizations and screenshots to the README before publishing to GitHub.
