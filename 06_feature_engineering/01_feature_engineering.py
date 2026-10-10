
import pandas as pd
from pathlib import Path

# 1. File paths
downloads = Path.home() / "Downloads"

input_file = downloads / "cleaned_freight_data.csv"
output_file = downloads / "freight_features.csv"

# 2. Read cleaned shipment data
df = pd.read_csv(input_file, parse_dates=["shipment_date"])

# 3. Aggregate shipment demand by month
df["month"] = df["shipment_date"].dt.to_period("M").dt.to_timestamp()

monthly = (
    df.groupby("month", as_index=False)
      .agg(
          demand_units=("demand_units", "sum"),
          total_shipments=("shipment_id", "count"),
          total_freight_cost=("freight_cost", "sum"),
          avg_delivery_days=("delivery_days", "mean"),
          avg_distance_km=("distance_km", "mean")
      )
      .sort_values("month")
      .reset_index(drop=True)
)

# 4. Create lag features
monthly["lag_1"] = monthly["demand_units"].shift(1)
monthly["lag_2"] = monthly["demand_units"].shift(2)
monthly["lag_3"] = monthly["demand_units"].shift(3)

# 5. Create rolling average features using past demand only
monthly["rolling_mean_3"] = (
    monthly["demand_units"].shift(1).rolling(3).mean()
)

monthly["rolling_mean_6"] = (
    monthly["demand_units"].shift(1).rolling(6).mean()
)

# 6. Create seasonality features
monthly["month_number"] = monthly["month"].dt.month
monthly["quarter"] = monthly["month"].dt.quarter

monthly["month_sin"] = __import__("numpy").sin(
    2 * __import__("numpy").pi * monthly["month_number"] / 12
)

monthly["month_cos"] = __import__("numpy").cos(
    2 * __import__("numpy").pi * monthly["month_number"] / 12
)

# 7. Create previous-year demand feature
monthly["lag_12"] = monthly["demand_units"].shift(12)

# 8. Save features
monthly.to_csv(output_file, index=False)

print("Feature engineering completed!")
print("Monthly records:", len(monthly))
print("Output saved to:", output_file)
print("\nFeature columns:")
print(monthly.columns.tolist())

print("\nFirst 10 rows:")
print(monthly.head(10).to_string(index=False))

print("\nMissing values per column:")
print(monthly.isnull().sum())
