import pandas as pd
import glob
import os
from tqdm import tqdm

# ================== STATE NORMALIZATION ==================/VG

STATE_NORMALIZATION_MAP = {
    "West Bangal": "West Bengal",
    "West Bengli": "West Bengal",
    "Westbengal": "West Bengal",
    "West  Bengal": "West Bengal",
    "Uttaranchal": "Uttarakhand",
    "Tamilnadu": "Tamil Nadu",
    "Orissa": "Odisha",
    "Pondicherry": "Puducherry",
    "Andaman And Nicobar Islands": "Andaman & Nicobar Islands",
    "Dadra & Nagar Haveli": "Dadra & Nagar Haveli and Daman & Diu",
    "Dadra And Nagar Haveli": "Dadra & Nagar Haveli and Daman & Diu",
    "Dadra And Nagar Haveli And Daman And Diu": "Dadra & Nagar Haveli and Daman & Diu",
    "Daman & Diu": "Dadra & Nagar Haveli and Daman & Diu",
    "Daman And Diu": "Dadra & Nagar Haveli and Daman & Diu",
    "Jammu And Kashmir": "Jammu & Kashmir",
    "Chhatisgarh": "Chhattisgarh",
}

VALID_INDIAN_STATES = {
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
    "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman & Nicobar Islands", "Chandigarh", "Dadra & Nagar Haveli and Daman & Diu",
    "Delhi", "Jammu & Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
}

# CONFIGURATION
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned")

os.makedirs(CLEANED_DIR, exist_ok=True)

# HELPER FUNCTIONS

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names."""
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df

def normalize_state_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize state name variations into one standard name"""

    df["state"] = (
        df["state"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )

    df["state"] = df["state"].replace(STATE_NORMALIZATION_MAP)

    return df



def parse_date_column(df: pd.DataFrame) -> pd.DataFrame:
    """Parse date column safely."""
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
        dayfirst=True
    )
    return df


def combine_csv_files(folder_path: str) -> pd.DataFrame:
    """
    Combine all CSV files inside a folder.
    Verifies schema consistency across chunks.
    """

    files = glob.glob(os.path.join(folder_path, "*.csv"))

    if not files:
        raise FileNotFoundError(f"No CSV files found in: {folder_path}")

    df_list = []
    base_columns = None

    for file in tqdm(files, desc=f"Reading {os.path.basename(folder_path)}"):
        df = pd.read_csv(file)

        if base_columns is None:
            base_columns = set(df.columns)
        else:
            if set(df.columns) != base_columns:
                raise ValueError(
                    f"Schema mismatch detected in file: {file}"
                )

        df_list.append(df)

    combined_df = pd.concat(df_list, ignore_index=True)
    return combined_df


# MAIN CLEANING PIPELINE

def clean_dataset(dataset_folder: str, dataset_type: str):
    print("\n================================================")
    print(f"Processing dataset: {dataset_folder}")
    print("================================================")

    input_path = os.path.join(RAW_DIR, dataset_folder)

    df = combine_csv_files(input_path)
    print(f"Initial rows: {df.shape[0]}")

    df = standardize_columns(df)

    required_cols = ["date", "state", "district", "pincode"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df = parse_date_column(df)
    before = df.shape[0]
    df = df.dropna(subset=["date"])
    print(f"Dropped {before - df.shape[0]} rows due to invalid dates")

    before = df.shape[0]
    df = df.drop_duplicates()
    print(f"Removed {before - df.shape[0]} duplicate rows")
    


    # Normalize state names/VG
    df = normalize_state_names(df)
    
    # Filter states to only keep valid Indian states/UTs
    before_state = df.shape[0]
    df = df[df["state"].isin(VALID_INDIAN_STATES)]
    print(f"Dropped {before_state - df.shape[0]} rows with invalid state names")
    
    # Clean district names
    df["district"] = (
        df["district"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s*\*\s*$", "", regex=True)  # strip trailing asterisks
        .str.replace(r"\.+$", "", regex=True)       # strip trailing periods
        .str.replace(r"\?", "-", regex=True)        # replace question marks with dashes
        .str.replace(r"\s+", " ", regex=True)       # replace multiple spaces with single space
        .str.title()
    )
    
    # Specific district mapping standardizations
    district_map = {
        "South 24 Pargana": "South 24 Parganas"
    }
    df["district"] = df["district"].replace(district_map)

    # Filter out invalid districts (like numbers, ?, empty, 5Th Cross, dashes)
    before_dist = df.shape[0]
    invalid_districts = ["?", "100000", "5Th Cross", "Nan", "Null", "", "-", "Unknown"]
    df = df[~df["district"].isin(invalid_districts)]
    # Drop if it is just numbers or only non-alphanumeric characters
    df = df[~df["district"].str.match(r"^\d+$", na=True)]
    df = df[~df["district"].str.match(r"^[^a-zA-Z0-9]+$", na=True)]
    # Drop if it's too short (less than 2 characters)
    df = df[df["district"].str.len() > 1]
    print(f"Dropped {before_dist - df.shape[0]} rows with invalid district names")

    df["pincode"] = pd.to_numeric(df["pincode"], errors="coerce")
    before = df.shape[0]
    df = df.dropna(subset=["pincode"])
    print(f"Dropped {before - df.shape[0]} rows due to invalid pincode")
    df["pincode"] = df["pincode"].astype(int)

    df["dataset_type"] = dataset_type
    df["month"] = df["date"].dt.to_period("M").astype(str)

    output_file = os.path.join(
        CLEANED_DIR, f"{dataset_folder}_cleaned.csv"
    )
    df.to_csv(output_file, index=False)

    print(f"✅ Cleaned file saved: {output_file}")
    print(f"Final rows: {df.shape[0]}")
    print(f"Date range: {df['date'].min()} → {df['date'].max()}")


# SCRIPT ENTRY POINT

if __name__ == "__main__":

    clean_dataset(
        dataset_folder="biometric",
        dataset_type="biometric_authentication"
    )

    clean_dataset(
        dataset_folder="demographic",
        dataset_type="demographic_authentication"
    )

    clean_dataset(
        dataset_folder="enrolment",
        dataset_type="enrolment"
    )

    print("\n ALL UIDAI DATASETS CLEANED SUCCESSFULLY")


