# Executive Summary

## Objective

This project analyzes telecom customer churn to identify the customer profiles and product experiences most associated with cancellation. The goal is to help the business prioritize retention campaigns and improve customer lifetime value.

## Business Context

Customer retention is typically more cost-effective than new customer acquisition. By understanding churn patterns across contract type, tenure, services, payment methods, and monthly charges, the company can target interventions before high-risk customers leave.

## Analytical Approach

The analysis combines SQL and Python:

- SQL is used for reproducible data cleaning, type conversion, aggregation, and stakeholder-ready business queries.
- Python is used for exploratory data analysis, visualization, feature engineering, and optional predictive modeling.
- Business intelligence techniques are used to translate findings into segments and recommended actions.

## Expected Findings to Validate

After running the project with the raw IBM Telco dataset, update this section with exact values. The analysis is designed to test whether:

- Month-to-month contracts have the highest churn rate.
- Newer customers churn more often than long-tenured customers.
- Customers using electronic checks are more likely to churn than customers using automatic payment methods.
- Customers with higher monthly charges and fewer support/security services show elevated churn risk.
- Fiber optic internet customers may require closer review because higher spending does not always translate into stronger retention.

## Business Impact

The output of this project should help stakeholders:

- Prioritize customers for retention outreach.
- Design contract migration offers.
- Identify product bundles that improve stickiness.
- Reduce churn by addressing high-friction service and billing experiences.
