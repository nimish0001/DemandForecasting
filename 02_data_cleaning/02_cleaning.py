
import pandas as pd
import numpy as np
from pathlib import Path

# ==================================================
# 1. READ RAW DATA FROM DOWNLOADS
# ==================================================

downloads = Path.home() / "Downloads"

input_file = downloads / "raw_freight_data.csv"
output_file = downloads / "cleaned_freight_data.csv"

df = pd.read_csv(input_file)

print("=" * 55)
print("LOGISTICS DATA CLEANING")
print("=" * 55)

print("\nOriginal dataset shape:", df.shape)

# ==================================================
# 2. REMOVE EXACT DUPLICATE ROWS
# ==================================================

duplicate_count = df.duplicated().sum()
df = df.drop_duplicates()

print("\nDuplicate rows removed:", duplicate_count)

# ==================================================
# 3. CLEAN TEXT COLUMNS
# ==================================================

text_columns = [
    "route",
    "transport_mode",
    "cargo_type",
    "delivery_status",
    "region"
]

for col in text_columns:
    df[col] = df[col].astype("string").str.strip()

# Standardize text capitalization
df["transport_mode"] = df["transport_mode"].str.title()
df["cargo_type"] = df["cargo_type"].str.title()
df["delivery_status"] = df["delivery_status"].str.title()
df["route"] = df["route"].str.title()
df["region"] = df["region"].str.title()

# ==================================================
# 4. CLEAN DATE COLUMN
# ==================================================

df["shipment_date"] = pd.to_datetime(
    df["shipment_date"],
    errors="coerce"
)

invalid_dates = df["shipment_date"].isna().sum()

# Drop rows where shipment date is missing or invalid
df = df.dropna(subset=["shipment_date"])

print("Rows with invalid/missing dates removed:", invalid_dates)

# ==================================================
# 5. CONVERT NUMERIC COLUMNS
# ==================================================

numeric_columns = [
    "shipment_id",
    "distance_km",
    "weight_kg",
    "demand_units",
    "freight_cost",
    "delivery_days"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ==================================================
# 6. HANDLE INVALID VALUES
# ==================================================

# Invalid distance: zero or negative
df.loc[df["distance_km"] <= 0, "distance_km"] = np.nan

# Invalid weight: zero or negative
df.loc[df["weight_kg"] <= 0, "weight_kg"] = np.nan

# Invalid demand: zero or negative
df.loc[df["demand_units"] <= 0, "demand_units"] = np.nan

# Invalid delivery duration
df.loc[df["delivery_days"] <= 0, "delivery_days"] = np.nan

# Invalid cost
df.loc[df["freight_cost"] <= 0, "freight_cost"] = np.nan

# Invalid IDs
df.loc[df["shipment_id"] <= 0, "shipment_id"] = np.nan

# ==================================================
# 7. VALIDATE CATEGORIES
# ==================================================

valid_modes = ["Truck", "Rail", "Air"]
valid_cargo = ["Electronics", "Food", "Textiles", "Machinery"]
valid_status = ["On Time", "Delayed"]

df.loc[
    ~df["transport_mode"].isin(valid_modes),
    "transport_mode"
] = pd.NA

df.loc[
    ~df["cargo_type"].isin(valid_cargo),
    "cargo_type"
] = pd.NA

df.loc[
    ~df["delivery_status"].isin(valid_status),
    "delivery_status"
] = pd.NA

valid_routes = [
    "Lucknow-Delhi",
    "Delhi-Mumbai",
    "Lucknow-Kanpur",
    "Mumbai-Pune",
    "Delhi-Jaipur",
    "Kanpur-Varanasi"
]

df.loc[~df["route"].isin(valid_routes), "route"] = pd.NA

# Recalculate region from the validated route
route_regions = {
    "Lucknow-Delhi": "North",
    "Delhi-Mumbai": "West",
    "Lucknow-Kanpur": "North",
    "Mumbai-Pune": "West",
    "Delhi-Jaipur": "North",
    "Kanpur-Varanasi": "North"
}

df["region"] = df["route"].map(route_regions)

# ==================================================
# 8. HANDLE MISSING VALUES
# ==================================================

# Fill numeric missing values with median
median_columns = [
    "distance_km",
    "weight_kg",
    "demand_units",
    "freight_cost",
    "delivery_days"
]

for col in median_columns:
    df[col] = df[col].fillna(df[col].median())

# Fill missing categories with the most frequent value
categorical_columns = [
    "route",
    "transport_mode",
    "cargo_type",
    "delivery_status"
]

for col in categorical_columns:
    mode_values = df[col].mode()

    if not mode_values.empty:
        df[col] = df[col].fillna(mode_values.iloc[0])

# Remove records without a usable shipment ID
df = df.dropna(subset=["shipment_id"])

# Shipment IDs should be whole numbers
df["shipment_id"] = df["shipment_id"].astype("int64")

# ==================================================
# 9. INVESTIGATE EXTREME FREIGHT COSTS
# ==================================================

# Flag extreme values using the IQR rule.
# Do not automatically delete them: they may be genuine.
q1 = df["freight_cost"].quantile(0.25)
q3 = df["freight_cost"].quantile(0.75)
iqr = q3 - q1

upper_limit = q3 + 1.5 * iqr
lower_limit = max(0, q1 - 1.5 * iqr)

outlier_mask = (
    (df["freight_cost"] < lower_limit)
    | (df["freight_cost"] > upper_limit)
)

print("\nExtreme freight-cost values flagged:", outlier_mask.sum())
print("Outliers retained for investigation.")

# ==================================================
# 10. FINAL VALIDATION
# ==================================================

# Remove duplicate shipment IDs, keeping the first occurrence
duplicate_ids = df["shipment_id"].duplicated().sum()
df = df.drop_duplicates(subset=["shipment_id"], keep="first")

# Sort chronologically
df = df.sort_values("shipment_date").reset_index(drop=True)

# Save cleaned dataset
df.to_csv(output_file, index=False)

print("\n" + "=" * 55)
print("DATA CLEANING COMPLETED")
print("=" * 55)

print("\nFinal dataset shape:", df.shape)
print("Duplicate shipment IDs removed:", duplicate_ids)

print("\nRemaining missing values:")
print(df.isnull().sum())

print("\nFinal data types:")
print(df.dtypes)

print("\nDate range:")
print(df["shipment_date"].min(), "to", df["shipment_date"].max())

print("\nCleaned CSV saved at:")
print(output_file)
