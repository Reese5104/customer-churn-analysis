-- Overall churn rate
SELECT
    COUNT(*) AS customers,
    SUM(churn_flag) AS churned_customers,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct
FROM telco_customers;

-- Churn by contract type
SELECT
    contract,
    COUNT(*) AS customers,
    SUM(churn_flag) AS churned_customers,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM telco_customers
GROUP BY contract
ORDER BY churn_rate_pct DESC;

-- Churn by tenure group
SELECT
    tenure_group,
    COUNT(*) AS customers,
    SUM(churn_flag) AS churned_customers,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct
FROM telco_customers
GROUP BY tenure_group
ORDER BY MIN(tenure);

-- Churn by internet service
SELECT
    internet_service,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM telco_customers
GROUP BY internet_service
ORDER BY churn_rate_pct DESC;

-- Churn by payment method
SELECT
    payment_method,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct
FROM telco_customers
GROUP BY payment_method
ORDER BY churn_rate_pct DESC;

-- Monthly recurring revenue at risk by segment
SELECT
    contract,
    tenure_group,
    COUNT(*) AS customers,
    SUM(churn_flag) AS churned_customers,
    ROUND(SUM(CASE WHEN churn_flag = 1 THEN monthly_charges ELSE 0 END), 2) AS monthly_revenue_lost,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct
FROM telco_customers
GROUP BY contract, tenure_group
ORDER BY monthly_revenue_lost DESC;

-- Churn by support and security services
SELECT
    online_security,
    tech_support,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(churn_flag), 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM telco_customers
GROUP BY online_security, tech_support
HAVING COUNT(*) >= 50
ORDER BY churn_rate_pct DESC;
