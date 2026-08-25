# ============================================================
# UIDAI Hackathon – Trend Modeling Using Full 2025 Data
# File: analysis/forecasting.py
# ============================================================
# PURPOSE:
# ✔ Use ALL available 2025 data
# ✔ Fit a simple ARIMA model
# ✔ Show trend + fitted values (in-sample)
# ✔ NO future year forecasting or claims
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import os
from statsmodels.tsa.arima.model import ARIMA

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_DIR = os.path.join(BASE_DIR, "analysis", "forecast_outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# LOAD PROCESSED DATA
# ============================================================

print("Loading processed mismatch data...")

df = pd.read_csv(
    os.path.join(PROCESSED_DIR, "enrolment_usage_mismatch.csv")
)

df["month"] = pd.to_datetime(df["month"])

print("✅ Data loaded successfully")

# ============================================================
# AGGREGATE NATIONAL MONTHLY DATA (FULL AVAILABLE 2025)
# ============================================================

monthly = (
    df
    .groupby("month")[["total_usage", "total_enrolment"]]
    .sum()
    .reset_index()
    .sort_values("month")
)

monthly["usage_gap"] = monthly["total_usage"] - monthly["total_enrolment"]

monthly.set_index("month", inplace=True)

print("\nNational monthly data used for trend modeling:")
print(monthly)

# ============================================================
# FIT ARIMA MODEL (IN-SAMPLE TREND)
# ============================================================

# Simple, explainable model
model = ARIMA(monthly["total_usage"], order=(1, 1, 1))
fitted_model = model.fit()

# Store fitted (trend) values
monthly["usage_trend_fitted"] = fitted_model.fittedvalues

# ============================================================
# SAVE TREND DATA
# ============================================================

output_csv = os.path.join(
    OUTPUT_DIR, "national_usage_trend_2025.csv"
)

monthly.reset_index().to_csv(output_csv, index=False)

print(f"\n✅ Trend data saved: {output_csv}")

# ============================================================
# PLOT OBSERVED VS TREND
# ============================================================

plt.figure(figsize=(10, 5))
plt.plot(
    monthly.index,
    monthly["total_usage"],
    label="Observed Usage",
    marker="o"
)
plt.plot(
    monthly.index,
    monthly["usage_trend_fitted"],
    linestyle="--",
    label="Model-Fitted Trend (ARIMA)"
)

plt.title("National Aadhaar Usage Trend (2025 – In-Sample Model)")
plt.xlabel("Month")
plt.ylabel("Usage Count")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plot_path = os.path.join(
    OUTPUT_DIR, "national_usage_trend_2025.png"
)

plt.savefig(plot_path)
plt.close()

print(f"✅ Trend plot saved: {plot_path}")
print("\n🎉 TREND MODELING COMPLETED SUCCESSFULLY (NO FUTURE YEAR CLAIMS)")
