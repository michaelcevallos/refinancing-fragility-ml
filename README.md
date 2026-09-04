# Refinancing Fragility ML

This is a machine learning project designed to identify publicly traded firms whose financial structures may be increasingly exposed to refinancing risk.

## Main Idea

A firm's financial structure can become fragile when internally generated cash & liquid resources become insufficient relative to near-term financing obligations, increasing its dependence on external financing.

This project builds a point-in-time corporate financial dataset, engineers features representing liquidity & refinancing pressure, & tests whether those features contain information about subsequent stock performance relative to the market.

## Current Pipeline

- Extract quarterly corporate financial data from SEC filings using XBRL facts
- Reconstruct quarterly cash-flow values from cumulative reported figures
- Preserve filing dates to maintain point-in-time information availability
- Engineer refinancing & liquidity features from cash flow, liquid assets, & near-term debt
- Store the resulting dataset in SQLite
- Construct 12-month forward equity returns relative to the S&P 500
- Train & evaluate a Ridge regression model against a naive baseline
- Use a time-aware train/test split that prevents future target information from leaking into model training

## Current Features

The initial model uses:

- **Liquidity coverage:** liquid assets relative to near-term debt
- **Recent cash-generation capacity:** trailing four-quarter free cash flow
- **Prospective liquidity coverage:** liquid assets plus recent cash-generation capacity relative to near-term debt

The pipeline also calculates a funding shortfall when estimated internal cash generation is insufficient to cover near-term debt.

## Current Scope

V1 currently uses Apple & Microsoft as a small proof-of-concept dataset. The purpose of this version is to demonstrate the complete research & ML pipeline rather than establish a production-ready trading strategy.

The current sample is too small to draw strong conclusions about predictive performance. Future work could expand the company universe, improve debt-maturity data, incorporate changing funding conditions & macroeconomic variables, & evaluate more sophisticated forecasting & machine learning methods.

## Tech Stack

- Python
- pandas / NumPy
- SEC EDGAR / XBRL
- SQLite
- yfinance
- scikit-learn