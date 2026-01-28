import os
import pandas as pd

DIM = "data/processed/dim_hospital.csv"
MSPB = "data/processed/fact_mspb.csv"
READM = "data/processed/fact_readmissions.csv"

OUT = "analysis/hospital_efficiency_facility.csv"
os.makedirs("analysis", exist_ok=True)

def read_csv_force_str(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, low_memory=False)

def to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")

def main():
    hospitals = read_csv_force_str(DIM)
    mspb = read_csv_force_str(MSPB)
    readm = read_csv_force_str(READM)

    # normalize key
    for df in (hospitals, mspb, readm):
        df["facility_id"] = df["facility_id"].astype(str).str.strip()

    # ---- MSPB (should be 1 row per facility already)
    mspb["score_num"] = to_num(mspb["score"])
    mspb_fac = (
        mspb.groupby("facility_id", as_index=False)
            .agg(
                mspb_score=("score_num", "mean"),
                mspb_start_date=("start_date", "max"),
                mspb_end_date=("end_date", "max"),
            )
    )

    # ---- Readmissions (many measures per facility -> aggregate)
    # keep numeric ratio only
    if "excess_readmission_ratio" in readm.columns:
        readm["excess_readmission_ratio_num"] = to_num(readm["excess_readmission_ratio"])
    else:
        readm["excess_readmission_ratio_num"] = pd.NA

    readm_fac = (
        readm.groupby("facility_id", as_index=False)
            .agg(
                readm_ratio_mean=("excess_readmission_ratio_num", "mean"),
                readm_ratio_median=("excess_readmission_ratio_num", "median"),
                readm_ratio_worst=("excess_readmission_ratio_num", "max"),
                readm_measure_count=("measure_name", "nunique"),
                readm_start_date=("start_date", "max"),
                readm_end_date=("end_date", "max"),
            )
    )

    # ---- Merge to one row per facility
    df = hospitals.merge(mspb_fac, on="facility_id", how="left", validate="one_to_one")
    df = df.merge(readm_fac, on="facility_id", how="left", validate="one_to_one")

    # Optional: quick derived flag fields
    df["has_mspb"] = df["mspb_score"].notna()
    df["has_readm"] = df["readm_ratio_mean"].notna()

    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT} ({len(df):,} rows, {df['facility_id'].nunique():,} unique hospitals)")

if __name__ == "__main__":
    main()
