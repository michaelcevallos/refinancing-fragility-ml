import sqlite3
import pandas as pd

from fetch_filings import build_company_dataset
from features import build_features


df = pd.concat([
    build_company_dataset("AAPL"),
    build_company_dataset("MSFT")
], ignore_index=True)

features = build_features(df)

with sqlite3.connect("data/refinancing_fragility.db") as conn:
    features.to_sql(
        "company_quarter_features",
        conn,
        if_exists="replace",
        index=False
    )

    result = pd.read_sql_query(
        """
        SELECT
            ticker,
            fiscal_year,
            quarter,
            free_cash_flow,
            near_term_debt,
            liquidity_coverage,
            funding_shortfall,
            fcf_forecast_12m,
            prospective_liquidity_coverage
        FROM company_quarter_features
        WHERE free_cash_flow IS NOT NULL
        ORDER BY ticker, fiscal_year DESC, quarter DESC
        """,
        conn
    )

print(result.groupby("ticker").head(10).to_string(index=False))