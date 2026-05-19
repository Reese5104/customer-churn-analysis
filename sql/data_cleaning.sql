DELETE FROM telco_customers;

INSERT INTO telco_customers (
    customer_id,
    gender,
    senior_citizen,
    partner,
    dependents,
    tenure,
    tenure_group,
    phone_service,
    multiple_lines,
    internet_service,
    online_security,
    online_backup,
    device_protection,
    tech_support,
    streaming_tv,
    streaming_movies,
    contract,
    paperless_billing,
    payment_method,
    monthly_charges,
    total_charges,
    churn,
    churn_flag
)
SELECT
    customerID AS customer_id,
    gender,
    SeniorCitizen AS senior_citizen,
    Partner AS partner,
    Dependents AS dependents,
    tenure,
    CASE
        WHEN tenure BETWEEN 0 AND 12 THEN '0-12 months'
        WHEN tenure BETWEEN 13 AND 24 THEN '13-24 months'
        WHEN tenure BETWEEN 25 AND 48 THEN '25-48 months'
        ELSE '49+ months'
    END AS tenure_group,
    PhoneService AS phone_service,
    MultipleLines AS multiple_lines,
    InternetService AS internet_service,
    OnlineSecurity AS online_security,
    OnlineBackup AS online_backup,
    DeviceProtection AS device_protection,
    TechSupport AS tech_support,
    StreamingTV AS streaming_tv,
    StreamingMovies AS streaming_movies,
    Contract AS contract,
    PaperlessBilling AS paperless_billing,
    PaymentMethod AS payment_method,
    MonthlyCharges AS monthly_charges,
    NULLIF(TRIM(TotalCharges), '') AS total_charges,
    Churn AS churn,
    CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END AS churn_flag
FROM raw_telco
WHERE customerID IS NOT NULL;

DELETE FROM telco_customers
WHERE total_charges IS NULL;
