import os
import pandas as pd

DIM = "data/processed/dim_hospital.csv"
MSPB = "data/processed/fact_mspb.csv"
READM = "data/processed/fact_readmissions.csv"
OUT = "analysis/hospital_efficiency_base.csv"

os.makedirs("analysis", exist_ok=True)

def read_csv_force_str(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, low_memory=False)

def main():
    hospitals = read_csv_force_str(DIM)
    mspb = read_csv_force_str(MSPB)
    readm = read_csv_force_str(READM)

    # Normalize join key types + whitespace (critical)
    for df in (hospitals, mspb, readm):
        if "facility_id" in df.columns:
            df["facility_id"] = df["facility_id"].astype(str).str.strip()

    # Merge cost (1:1 expected)
    df = hospitals.merge(
        mspb,
        on="facility_id",
        how="left",
        validate="one_to_one"
    )

    # Merge outcomes (can be 1:many due to multiple measures)
    df = df.merge(
        readm,
        on="facility_id",
        how="left",
        suffixes=("", "_readm")
    )

    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT} ({len(df):,} rows)")

if __name__ == "__main__":
    main()
