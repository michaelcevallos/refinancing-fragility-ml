import numpy as np
import pandas as pd

from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from fetch_filings import build_company_dataset
from features import build_features
from targets import add_forward_returns


df = pd.concat([
    build_company_dataset("AAPL"),
    build_company_dataset("MSFT")
], ignore_index=True)

features = build_features(df)
dataset = add_forward_returns(features)

feature_columns = [
    "liquidity_coverage",
    "fcf_forecast_12m",
    "prospective_liquidity_coverage"
]

target_column = "forward_12m_excess_return"

model_data = dataset.dropna(subset=feature_columns + [target_column]).copy()
model_data = model_data.sort_values("filing_date").reset_index(drop=True)

split_index = int(len(model_data) * 0.8)
test_start_date = model_data.iloc[split_index]["filing_date"]
train_cutoff_date = test_start_date - pd.Timedelta(days=365)

train = model_data[model_data["filing_date"] <= train_cutoff_date].copy()
test = model_data[model_data["filing_date"] >= test_start_date].copy()

X_train = train[feature_columns]
y_train = train[target_column]

X_test = test[feature_columns]
y_test = test[target_column]

baseline = DummyRegressor(strategy="mean")
baseline.fit(X_train, y_train)
baseline_predictions = baseline.predict(X_test)

model = Pipeline([
    ("scaler", StandardScaler()),
    ("ridge", Ridge(alpha=1.0))
])

model.fit(X_train, y_train)
predictions = model.predict(X_test)


def print_metrics(name, actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    r2 = r2_score(actual, predicted)

    print(f"\n{name}")
    print(f"MAE:  {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²:   {r2:.4f}")


print(f"Training observations: {len(train)}")
print(f"Test observations: {len(test)}")
print(f"Train through: {train['filing_date'].max().date()}")
print(f"Test starts: {test['filing_date'].min().date()}")

print_metrics("Dummy baseline", y_test, baseline_predictions)
print_metrics("Ridge regression", y_test, predictions)

results = test[
    [
        "ticker",
        "fiscal_year",
        "quarter",
        "filing_date",
        target_column
    ]
].copy()

results["predicted_excess_return"] = predictions

print("\nOut-of-sample predictions:")
print(results.to_string(index=False))