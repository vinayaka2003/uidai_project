import pandas as pd
import matplotlib.pyplot as plt
import os

# CONFIGURATION

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_DIR = os.path.join(BASE_DIR, "analysis", "eda_outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# LOAD DATA

print("Loading processed mismatch data...")

df = pd.read_csv(
    os.path.join(PROCESSED_DIR, "enrolment_usage_mismatch.csv")
)

print("✅ Data loaded successfully")
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

# BASIC OVERVIEW

print("\n=== BASIC DATA OVERVIEW ===")
print(df.describe())

#  TIME SERIES: TOTAL USAGE VS ENROLMENT (MONTHLY)

monthly_summary = (
    df
    .groupby("month")[["total_usage", "total_enrolment"]]
    .sum()
    .reset_index()
)

plt.figure()
plt.plot(monthly_summary["month"], monthly_summary["total_usage"])
plt.plot(monthly_summary["month"], monthly_summary["total_enrolment"])
plt.xticks(rotation=45)
plt.title("Monthly Aadhaar Usage vs Enrolment")
plt.xlabel("Month")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "monthly_usage_vs_enrolment.png"))
plt.close()

print("Saved: monthly_usage_vs_enrolment.png")

#  DISTRIBUTION OF USAGE–ENROLMENT RATIO

plt.figure()
df["usage_to_enrolment_ratio"].clip(0, 3).hist(bins=50)
plt.title("Distribution of Usage-to-Enrolment Ratio")
plt.xlabel("Usage / Enrolment Ratio (clipped)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "ratio_distribution.png"))
plt.close()

print("Saved: ratio_distribution.png")

# STATE-LEVEL AGGREGATION

state_summary = (
    df
    .groupby("state")[["total_usage", "total_enrolment"]]
    .sum()
    .reset_index()
)

state_summary["ratio"] = (
    state_summary["total_usage"] / state_summary["total_enrolment"]
).fillna(0)

top_states = state_summary.sort_values(
    "total_usage", ascending=False
).head(10)

plt.figure()
plt.bar(top_states["state"], top_states["ratio"])
plt.xticks(rotation=45)
plt.title("Top 10 States by Usage-to-Enrolment Ratio")
plt.xlabel("State")
plt.ylabel("Usage / Enrolment Ratio")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "top_states_ratio.png"))
plt.close()

print("Saved: top_states_ratio.png")

# MIGRATION SIGNAL BREAKDOWN

migration_counts = df["migration_signal"].value_counts()

plt.figure()
migration_counts.plot(kind="bar")
plt.title("Migration Signal Classification")
plt.xlabel("Signal Type")
plt.ylabel("Number of Region-Month Records")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "migration_signal_distribution.png"))
plt.close()

print("Saved: migration_signal_distribution.png")

# DISTRICT-LEVEL VARIATION (SAMPLE)

district_variation = (
    df
    .groupby("district")["usage_to_enrolment_ratio"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure()
plt.bar(district_variation.index, district_variation.values)
plt.xticks(rotation=45)
plt.title("Top 10 Districts by Avg Usage-to-Enrolment Ratio")
plt.xlabel("District")
plt.ylabel("Avg Usage / Enrolment Ratio")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "top_districts_ratio.png"))
plt.close()

print("Saved: top_districts_ratio.png")

# COMPLETION

print("\n🎉 EDA COMPLETED SUCCESSFULLY")
print(f"Plots saved in: {OUTPUT_DIR}")
