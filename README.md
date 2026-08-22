# Refinancing Fragility ML

This is a machine learning projected intended to identify publicly traded firms whose operations are becoming increasingly dependent on external financing.

## Main idea

A firm's financial structure can become fragile when its required cash outflows exceed its internally generated cash inflows, forcing it to rely on external financing to continue its operations & investments as planned.

The project will use historical corporate financial data to measure this refinancing dependence, model how it evolves under changing funding conditions, & test whether unusually fragile firms present actionable investment risks.

## Project Goals

- Build a point-in-time dataset from publicly available corporate financial data
- Engineer features representing funding gaps & refinancing dependence
- Train & evaluate machine learning models using Python & scikit-learn/XGBoost
- Interpret model predictions using SHAP
- Backtest investment decisions based on predicted financial fragility
- Develop the project as an end-to-end, reproducible ML pipeline