
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================
# 1. LOAD CLEANED DATA
# ==========================================

downloads = Path.home() / "Downloads"

input_file = downloads / "cleaned_freight_data.csv"
output_dir = downloads / "logistics_eda_outputs"
output_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_file, parse_dates=["shipment_date"])

print("=" * 50)
print("LOGISTICS EXPLORATORY DATA ANALYSIS")
print("=" * 50)

print("\nDataset shape:", df.shape)

print("\nDataset information:")
print(df.info())

print("\nStatistical summary:")
print(df.describe())

# ==========================================
# 2. MONTHLY DEMAND TREND
# ==========================================

df["year_month"] = df["shipment_date"].dt.to_period("M").astype(str)

monthly_demand = (
    df.groupby("year_month")["demand_units"]
    .sum()
    .reset_index()
)

plt.figure(figsize=(14, 6))
plt.plot(
    monthly_demand["year_month"],
    monthly_demand["demand_units"],
    marker="o"
)

plt.title("Monthly Freight Demand Trend")
plt.xlabel("Month")
plt.ylabel("Total Demand Units")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(output_dir / "monthly_demand_trend.png", dpi=150)
plt.show()

# ==========================================
# 3. DEMAND BY ROUTE
# ==========================================

route_demand = (
    df.groupby("route")["demand_units"]
    .sum()
    .sort_values(ascending=False)
)

plt.figure(figsize=(10, 6))
route_demand.plot(kind="bar")

plt.title("Total Demand by Route")
plt.xlabel("Route")
plt.ylabel("Total Demand Units")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(output_dir / "demand_by_route.png", dpi=150)
plt.show()

# ==========================================
# 4. SEASONAL DEMAND ANALYSIS
# ==========================================

df["month"] = df["shipment_date"].dt.month

seasonal_demand = (
    df.groupby("month")["demand_units"]
    .mean()
)

plt.figure(figsize=(10, 5))
seasonal_demand.plot(kind="bar")

plt.title("Average Demand by Calendar Month")
plt.xlabel("Month (1 = January)")
plt.ylabel("Average Demand Units per Shipment")
plt.tight_layout()
plt.savefig(output_dir / "seasonal_demand.png", dpi=150)
plt.show()

# ==========================================
# 5. FREIGHT COST BY TRANSPORT MODE
# ==========================================

mode_cost = (
    df.groupby("transport_mode")["freight_cost"]
    .mean()
    .sort_values(ascending=False)
)

plt.figure(figsize=(8, 5))
mode_cost.plot(kind="bar")

plt.title("Average Freight Cost by Transport Mode")
plt.xlabel("Transport Mode")
plt.ylabel("Average Freight Cost")
plt.tight_layout()
plt.savefig(output_dir / "freight_cost_by_mode.png", dpi=150)
plt.show()

# ==========================================
# 6. DELIVERY PERFORMANCE
# ==========================================

delivery_counts = df["delivery_status"].value_counts()

plt.figure(figsize=(7, 5))
delivery_counts.plot(kind="bar")

plt.title("Shipment Delivery Status")
plt.xlabel("Delivery Status")
plt.ylabel("Number of Shipments")
plt.tight_layout()
plt.savefig(output_dir / "delivery_status.png", dpi=150)
plt.show()

# ==========================================
# 7. CORRELATION ANALYSIS
# ==========================================

numeric_cols = [
    "distance_km",
    "weight_kg",
    "demand_units",
    "freight_cost",
    "delivery_days"
]

correlation = df[numeric_cols].corr()

plt.figure(figsize=(8, 6))
plt.imshow(correlation, aspect="auto")
plt.colorbar(label="Correlation")

plt.xticks(
    range(len(numeric_cols)),
    numeric_cols,
    rotation=45,
    ha="right"
)
plt.yticks(range(len(numeric_cols)), numeric_cols)

plt.title("Correlation Between Numeric Variables")
plt.tight_layout()
plt.savefig(output_dir / "correlation_matrix.png", dpi=150)
plt.show()

# ==========================================
# 8. BUSINESS INSIGHTS
# ==========================================

print("\n" + "=" * 50)
print("KEY FINDINGS")
print("=" * 50)

print("\nTop 3 routes by demand:")
print(route_demand.head(3))

print("\nAverage demand by month:")
print(seasonal_demand.round(2))

print("\nAverage freight cost by transport mode:")
print(mode_cost.round(2))

print("\nDelivery status distribution:")
print(delivery_counts)

print("\nAll charts saved to:")
print(output_dir)
