import os
import pandas as pd

RAW_DIR = "data/raw"
OUT_DIR = "data/processed"
os.makedirs(OUT_DIR, exist_ok=True)

IN_FILE = os.path.join(
    RAW_DIR, "FY_2025_Hospital_Readmissions_Reduction_Program_Hospital.csv"
)
OUT_FILE = os.path.join(OUT_DIR, "fact_readmissions.csv")

def to_snake(s: str) -> str:
    return s.strip().lower().replace(" ", "_").replace("/", "_").replace("-", "_")

def main():
    df = pd.read_csv(IN_FILE, dtype=str)

    df.columns = [to_snake(c) for c in df.columns]

    keep = [
        "facility_id",
        "measure_name",
        "excess_readmission_ratio",
        "predicted_readmission_rate",
        "expected_readmission_rate",
        "number_of_discharges",
        "number_of_readmissions",
        "start_date",
        "end_date",
    ]
    df = df[keep].copy()

    # Convert numerics
    numeric_cols = [
        "excess_readmission_ratio",
        "predicted_readmission_rate",
        "expected_readmission_rate",
        "number_of_discharges",
        "number_of_readmissions",
    ]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Dates
    for c in ["start_date", "end_date"]:
        df[c] = pd.to_datetime(df[c], errors="coerce").dt.date.astype("string")

    df["facility_id"] = df["facility_id"].astype(str).str.strip()

    df = df.dropna(subset=["facility_id", "excess_readmission_ratio"])

    df.to_csv(OUT_FILE, index=False)
    print(f"Wrote {OUT_FILE} ({len(df):,} rows)")

if __name__ == "__main__":
    main()
