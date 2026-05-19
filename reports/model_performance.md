# Model Performance

Baseline model: logistic regression with one-hot encoded categorical features, standardized numeric features, and balanced class weights.

ROC AUC: `0.839`

```text
              precision    recall  f1-score   support

    Retained       0.91      0.71      0.80      1291
     Churned       0.50      0.80      0.62       467

    accuracy                           0.73      1758
   macro avg       0.70      0.76      0.71      1758
weighted avg       0.80      0.73      0.75      1758
```
