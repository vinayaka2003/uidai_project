import pandas as pd
import os

# CONFIGURATION

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(PROCESSED_DIR, exist_ok=True)

# LOAD CLEANED DATA

print("Loading cleaned datasets...")

biometric_df = pd.read_csv(os.path.join(CLEANED_DIR, "biometric_cleaned.csv"))
demographic_df = pd.read_csv(os.path.join(CLEANED_DIR, "demographic_cleaned.csv"))
enrolment_df = pd.read_csv(os.path.join(CLEANED_DIR, "enrolment_cleaned.csv"))

print("✅ Cleaned data loaded successfully")

# STANDARDIZE DATE & MONTH

for df in [biometric_df, demographic_df, enrolment_df]:
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

# IDENTIFY COUNT COLUMNS AUTOMATICALLY

def get_count_columns(df):
    return [
        col for col in df.columns
        if col not in [
            "date", "month", "state", "district",
            "pincode", "dataset_type"
        ]
        and pd.api.types.is_numeric_dtype(df[col])
    ]


biometric_cols = get_count_columns(biometric_df)
demographic_cols = get_count_columns(demographic_df)
enrolment_cols = get_count_columns(enrolment_df)

# AGGREGATE DATA (MONTHLY, REGION-WISE)

def aggregate_dataset(df, value_cols, label):
    agg_df = (
        df
        .groupby(["month", "state", "district", "pincode"], as_index=False)[value_cols]
        .sum()
    )
    agg_df["dataset"] = label
    agg_df["total_count"] = agg_df[value_cols].sum(axis=1)
    return agg_df


biometric_agg = aggregate_dataset(biometric_df, biometric_cols, "biometric")
demographic_agg = aggregate_dataset(demographic_df, demographic_cols, "demographic")

# Aggregate enrolment overall by location to establish a baseline enrolled population
enrolment_agg = (
    enrolment_df
    .groupby(["state", "district", "pincode"], as_index=False)[enrolment_cols]
    .sum()
)
enrolment_agg["total_enrolment"] = enrolment_agg[enrolment_cols].sum(axis=1)

# MERGE DATASETS

usage_df = pd.merge(
    biometric_agg,
    demographic_agg,
    on=["month", "state", "district", "pincode"],
    how="outer",
    suffixes=("_biometric", "_demographic")
)

usage_df["total_usage"] = (
    usage_df["total_count_biometric"].fillna(0)
    + usage_df["total_count_demographic"].fillna(0)
)

final_df = pd.merge(
    usage_df,
    enrolment_agg[["state", "district", "pincode", "total_enrolment"]],
    on=["state", "district", "pincode"],
    how="left"
)

# CALCULATE MISMATCH METRICS

# Fill missing enrolment baseline with 1 to avoid division by zero while preserving the signal
final_df["total_enrolment"] = final_df["total_enrolment"].fillna(1)

# Normalize the ratio relative to the national average for the month to control for multi-auth volume and seasonal fluctuations
national_monthly_usage = final_df.groupby("month")["total_usage"].transform("sum")
national_monthly_enrolment = final_df.groupby("month")["total_enrolment"].transform("sum")
national_monthly_ratio = (national_monthly_usage / national_monthly_enrolment).replace(0, 1)

final_df["usage_to_enrolment_ratio"] = (
    (final_df["total_usage"] / final_df["total_enrolment"]) / national_monthly_ratio
)

# CLASSIFY REGIONS (INTERPRETABLE, SAFE)

def classify_region(ratio):
    if ratio > 1.2:
        return "High Usage vs Enrolment (Possible In-migration)"
    elif ratio < 0.8:
        return "Low Usage vs Enrolment (Possible Out-migration)"
    else:
        return "Balanced"


final_df["migration_signal"] = final_df[
    "usage_to_enrolment_ratio"
].apply(classify_region)

# SAVE PROCESSED DATA

output_path = os.path.join(PROCESSED_DIR, "enrolment_usage_mismatch.csv")
final_df.to_csv(output_path, index=False)

print("✅ Mismatch analysis completed")
print(f"Processed file saved at: {output_path}")
print(f"Final rows: {final_df.shape[0]}")
