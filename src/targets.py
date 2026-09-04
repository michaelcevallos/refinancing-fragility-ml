import pandas as pd
import yfinance as yf

from fetch_filings import build_company_dataset
from features import build_features


def get_price_on_or_after(prices, date):
    available_prices = prices.loc[prices.index >= date]

    if available_prices.empty:
        return None

    return available_prices.iloc[0]["Close"]


def add_forward_returns(features, benchmark="SPY", horizon_days=365):
    targets = features.copy()

    tickers = targets["ticker"].dropna().unique().tolist()
    price_data = {}

    start_date = targets["filing_date"].min() - pd.Timedelta(days=7)
    end_date = targets["filing_date"].max() + pd.Timedelta(days=horizon_days + 7)

    for ticker in tickers + [benchmark]:
        prices = yf.Ticker(ticker).history(
            start=start_date,
            end=end_date,
            auto_adjust=True
        )

        prices.index = prices.index.tz_localize(None)
        price_data[ticker] = prices

    company_returns = []
    benchmark_returns = []
    excess_returns = []

    for _, row in targets.iterrows():
        filing_date = row["filing_date"]
        future_date = filing_date + pd.Timedelta(days=horizon_days)

        company_prices = price_data[row["ticker"]]
        benchmark_prices = price_data[benchmark]

        company_start = get_price_on_or_after(company_prices, filing_date)
        company_end = get_price_on_or_after(company_prices, future_date)

        benchmark_start = get_price_on_or_after(benchmark_prices, filing_date)
        benchmark_end = get_price_on_or_after(benchmark_prices, future_date)

        if (
            company_start is None
            or company_end is None
            or benchmark_start is None
            or benchmark_end is None
        ):
            company_returns.append(None)
            benchmark_returns.append(None)
            excess_returns.append(None)
            continue

        company_return = company_end / company_start - 1
        benchmark_return = benchmark_end / benchmark_start - 1
        excess_return = company_return - benchmark_return

        company_returns.append(company_return)
        benchmark_returns.append(benchmark_return)
        excess_returns.append(excess_return)

    targets["forward_12m_return"] = company_returns
    targets["benchmark_forward_12m_return"] = benchmark_returns
    targets["forward_12m_excess_return"] = excess_returns

    return targets


if __name__ == "__main__":
    df = pd.concat([
        build_company_dataset("AAPL"),
        build_company_dataset("MSFT")
    ], ignore_index=True)

    features = build_features(df)
    targets = add_forward_returns(features)

    print(
        targets[
            [
                "ticker",
                "fiscal_year",
                "quarter",
                "filing_date",
                "liquidity_coverage",
                "funding_shortfall",
                "prospective_liquidity_coverage",
                "forward_12m_return",
                "benchmark_forward_12m_return",
                "forward_12m_excess_return"
            ]
        ]
        .dropna(subset=["forward_12m_excess_return"])
        .groupby("ticker")
        .tail(10)
        .to_string(index=False)
    )