import os
import pandas as pd

RAW_DIR = "data/raw"
OUT_DIR = "data/processed"
os.makedirs(OUT_DIR, exist_ok=True)

HOSPITAL_FILE = os.path.join(RAW_DIR, "Hospital_General_Information.csv")
OUT_FILE = os.path.join(OUT_DIR, "dim_hospital.csv")

KEEP_COLS = [
    "Facility ID",
    "Facility Name",
    "Address",
    "City/Town",
    "State",
    "ZIP Code",
    "County/Parish",
    "Telephone Number",
    "Hospital Type",
    "Hospital Ownership",
    "Emergency Services",
    "Hospital overall rating",
]

def main():
    df = pd.read_csv(HOSPITAL_FILE, dtype=str)
    df = df[KEEP_COLS].copy()

    # Normalize column names to snake_case for analysis convenience
    df.columns = [c.strip().lower().replace(" ", "_").replace("/", "_") for c in df.columns]

    # Basic cleanup
    df["facility_id"] = df["facility_id"].astype(str).str.strip()
    df = df.drop_duplicates(subset=["facility_id"])

    df.to_csv(OUT_FILE, index=False)
    print(f"Wrote {OUT_FILE} ({len(df):,} rows)")

if __name__ == "__main__":
    main()
