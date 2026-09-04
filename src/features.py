import numpy as np
import pandas as pd


def build_features(df):
    features = df.copy()
    features["quarter_number"] = features["quarter"].str[1].astype(int)
    features = features.sort_values(["ticker", "fiscal_year", "quarter_number"]).copy()

    features["free_cash_flow"] = features["ocf"] - features["capex"]
    features["liquidity_coverage"] = features["liquid_assets"] / features["near_term_debt"].replace(0, np.nan)
    features["fcf_forecast_12m"] = features.groupby("ticker")["free_cash_flow"].rolling(4).sum().reset_index(level=0, drop=True)
    features["funding_shortfall"] = (features["near_term_debt"] - features["fcf_forecast_12m"]).clip(lower=0)
    features["prospective_liquidity_coverage"] = (features["liquid_assets"] + features["fcf_forecast_12m"]) / features["near_term_debt"].replace(0, np.nan)
    
    features = features.drop(columns=["quarter_number"])

    return features

if __name__ == "__main__":
    from fetch_filings import build_company_dataset

    df = pd.concat([
        build_company_dataset("AAPL"),
        build_company_dataset("MSFT")
    ], ignore_index=True)

    features = build_features(df)

    print(
        features[
            [
                "ticker",
                "fiscal_year",
                "quarter",
                "free_cash_flow",
                "funding_shortfall",
                "near_term_debt",
                "liquid_assets",
                "liquidity_coverage",
                "fcf_forecast_12m",
                "prospective_liquidity_coverage"
            ]
        ].groupby("ticker").tail(12).to_string(index=False)
    )