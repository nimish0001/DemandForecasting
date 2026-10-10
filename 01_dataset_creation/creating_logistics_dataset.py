
import pandas as pd
import numpy as np
from pathlib import Path

# 1. Settings
np.random.seed(42)
n_records = 1800

dates = pd.to_datetime(
    np.random.choice(
        pd.date_range("2023-01-01", "2025-12-31"),
        n_records
    )
)

routes = [
    "Lucknow-Delhi", "Delhi-Mumbai", "Lucknow-Kanpur",
    "Mumbai-Pune", "Delhi-Jaipur", "Kanpur-Varanasi"
]

regions = {
    "Lucknow-Delhi": "North",
    "Delhi-Mumbai": "West",
    "Lucknow-Kanpur": "North",
    "Mumbai-Pune": "West",
    "Delhi-Jaipur": "North",
    "Kanpur-Varanasi": "North"
}

# 2. Generate original shipment data
df = pd.DataFrame({
    "shipment_id": range(1001, 1001 + n_records),
    "shipment_date": dates,
    "route": np.random.choice(routes, n_records),
    "transport_mode": np.random.choice(
        ["Truck", "Rail", "Air"], n_records,
        p=[0.65, 0.25, 0.10]
    ),
    "cargo_type": np.random.choice(
        ["Electronics", "Food", "Textiles", "Machinery"],
        n_records
    ),
    "distance_km": np.random.randint(100, 1800, n_records),
    "weight_kg": np.random.randint(100, 20000, n_records)
})

# 3. Seasonal demand
month = df["shipment_date"].dt.month

seasonal_factor = np.where(
    month.isin([10, 11, 12]), 1.30,
    np.where(month.isin([6, 7, 8]), 0.90, 1.0)
)

df["demand_units"] = np.maximum(
    1,
    np.round(
        np.random.normal(100, 20, n_records) * seasonal_factor
    )
).astype(int)

# 4. Freight cost
rates = df["transport_mode"].map({
    "Truck": 12, "Rail": 7, "Air": 35
})

df["freight_cost"] = (
    df["distance_km"] * rates
    + df["weight_kg"] * 0.15
).round(2)

# 5. Delivery information
df["delivery_days"] = np.maximum(
    1,
    np.round(
        df["distance_km"] / 350
        + np.random.normal(1, 1.5, n_records)
    )
).astype(int)

df["delivery_status"] = np.where(
    df["delivery_days"] > 5, "Delayed", "On Time"
)

df["region"] = df["route"].map(regions)

# 6. Introduce missing values
for col, fraction, seed in [
    ("weight_kg", 0.02, 10),
    ("freight_cost", 0.015, 11),
    ("delivery_days", 0.01, 12),
    ("route", 0.01, 13),
    ("delivery_status", 0.01, 14)
]:
    idx = df.sample(frac=fraction, random_state=seed).index
    df.loc[idx, col] = np.nan

# 7. Invalid and missing dates
df["shipment_date"] = df["shipment_date"].dt.strftime("%Y-%m-%d")

idx = df.sample(frac=0.01, random_state=15).index
df.loc[idx, "shipment_date"] = np.nan

idx = df.dropna(subset=["shipment_date"]).sample(
    frac=0.005, random_state=16
).index
df.loc[idx, "shipment_date"] = "2025-15-40"

# 8. Inconsistent text
idx = df.sample(frac=0.03, random_state=17).index
df.loc[idx, "transport_mode"] = "truck "

idx = df.sample(frac=0.02, random_state=18).index
df.loc[idx, "cargo_type"] = "electronics"

idx = df.sample(frac=0.015, random_state=19).index
df.loc[idx, "delivery_status"] = "on time "

# 9. Invalid categories
idx = df.sample(frac=0.005, random_state=21).index
df.loc[idx, "transport_mode"] = "Helicopter"

idx = df.sample(frac=0.005, random_state=22).index
df.loc[idx, "cargo_type"] = "Unknown Cargo"

# 10. Invalid numeric values
idx = df.sample(frac=0.005, random_state=23).index
df.loc[idx, "weight_kg"] = -500

idx = df.sample(frac=0.005, random_state=24).index
df.loc[idx, "distance_km"] = 0

idx = df.sample(frac=0.005, random_state=25).index
df.loc[idx, "delivery_days"] = -3

idx = df.sample(frac=0.005, random_state=26).index
df.loc[idx, "demand_units"] = -10

# 11. Incorrect data types
df["distance_km"] = df["distance_km"].astype(object)
idx = df.sample(frac=0.01, random_state=27).index
df.loc[idx, "distance_km"] = "unknown"

df["weight_kg"] = df["weight_kg"].astype(object)
idx = df.sample(frac=0.005, random_state=28).index
df.loc[idx, "weight_kg"] = "not available"

# 12. Missing shipment IDs
idx = df.sample(frac=0.003, random_state=29).index
df.loc[idx, "shipment_id"] = np.nan

# 13. Extreme freight-cost outliers
idx = df.sample(n=5, random_state=30).index
df.loc[idx, "freight_cost"] = (
    pd.to_numeric(df.loc[idx, "freight_cost"], errors="coerce") * 100
)

# 14. Duplicate records
duplicates = df.sample(n=10, random_state=31)
df = pd.concat([df, duplicates], ignore_index=True)

# 15. Save CSV directly to Downloads
downloads_folder = Path.home() / "Downloads"
downloads_folder.mkdir(parents=True, exist_ok=True)

output_file = downloads_folder / "raw_freight_data.csv"
df.to_csv(output_file, index=False)

# 16. Verify
print("Dataset generated successfully!")
print("Rows and columns:", df.shape)
print("Duplicate rows:", df.duplicated().sum())
print("\nMissing values:")
print(df.isnull().sum())
print("\nData types:")
print(df.dtypes)
print("\nCSV saved at:")
print(output_file)
