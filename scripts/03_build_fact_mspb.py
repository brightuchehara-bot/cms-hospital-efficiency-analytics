import os
import pandas as pd

RAW_DIR = "data/raw"
OUT_DIR = "data/processed"
os.makedirs(OUT_DIR, exist_ok=True)

IN_FILE = os.path.join(RAW_DIR, "Medicare_Hospital_Spending_Per_Patient-Hospital.csv")
OUT_FILE = os.path.join(OUT_DIR, "fact_mspb.csv")

def to_snake(s: str) -> str:
    return s.strip().lower().replace(" ", "_").replace("/", "_").replace("-", "_")

def main():
    df = pd.read_csv(IN_FILE, dtype=str)

    # Standardize column names
    df.columns = [to_snake(c) for c in df.columns]

    # Keep only the fields we need (everything else lives in dim_hospital)
    keep = [
        "facility_id",
        "measure_id",
        "measure_name",
        "score",
        "footnote",
        "start_date",
        "end_date",
    ]
    df = df[keep].copy()

    # Clean strings
    df["facility_id"] = df["facility_id"].astype(str).str.strip()
    df["measure_id"] = df["measure_id"].astype(str).str.strip()

    # Score should be numeric (coerce invalids to NaN)
    df["score"] = pd.to_numeric(df["score"], errors="coerce")

    # Dates (keep as YYYY-MM-DD strings for now; Power BI will parse easily)
    for c in ["start_date", "end_date"]:
        df[c] = pd.to_datetime(df[c], errors="coerce").dt.date.astype("string")

    # Drop rows missing key fields
    df = df.dropna(subset=["facility_id", "measure_id", "score"])

    df.to_csv(OUT_FILE, index=False)
    print(f"Wrote {OUT_FILE} ({len(df):,} rows)")

if __name__ == "__main__":
    main()
