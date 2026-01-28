import os
import pandas as pd
import numpy as np

IN_FILE = "analysis/hospital_efficiency_facility.csv"
OUT_DIR = "reports/generated"
os.makedirs(OUT_DIR, exist_ok=True)

def zscore(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    return (s - s.mean()) / s.std(ddof=0)

def main():
    df = pd.read_csv(IN_FILE)

    # keep the key fields we’ll show in exec outputs
    keep = [
        "facility_id",
        "facility_name",
        "city_town",
        "state",
        "hospital_type",
        "hospital_ownership",
        "emergency_services",
        "hospital_overall_rating",
        "mspb_score",
        "readm_ratio_mean",
        "readm_measure_count",
    ]
    df = df[keep].copy()

    # numeric conversions
    df["mspb_score"] = pd.to_numeric(df["mspb_score"], errors="coerce")
    df["readm_ratio_mean"] = pd.to_numeric(df["readm_ratio_mean"], errors="coerce")
    df["hospital_overall_rating"] = pd.to_numeric(df["hospital_overall_rating"], errors="coerce")

    # only hospitals that have BOTH metrics
    both = df.dropna(subset=["mspb_score", "readm_ratio_mean"]).copy()

    # define “high cost” and “high readmissions” thresholds (simple + defensible)
    # Use quartiles so it works for any refresh of the dataset
    mspb_p75 = both["mspb_score"].quantile(0.75)
    readm_p75 = both["readm_ratio_mean"].quantile(0.75)

    both["high_cost_flag"] = both["mspb_score"] >= mspb_p75
    both["high_readm_flag"] = both["readm_ratio_mean"] >= readm_p75

    # composite risk score (z-scored sum)
    both["mspb_z"] = zscore(both["mspb_score"])
    both["readm_z"] = zscore(both["readm_ratio_mean"])
    both["efficiency_risk_score"] = both["mspb_z"] + both["readm_z"]

    # WATCHLIST = high cost + high readmissions, sorted by composite score
    watchlist = (
        both[both["high_cost_flag"] & both["high_readm_flag"]]
        .sort_values("efficiency_risk_score", ascending=False)
        .head(25)
        .reset_index(drop=True)
    )

    # Outliers (top / bottom)
    top_cost = both.sort_values("mspb_score", ascending=False).head(20).reset_index(drop=True)
    best_cost = both.sort_values("mspb_score", ascending=True).head(20).reset_index(drop=True)

    top_readm = both.sort_values("readm_ratio_mean", ascending=False).head(20).reset_index(drop=True)
    best_readm = both.sort_values("readm_ratio_mean", ascending=True).head(20).reset_index(drop=True)

    # Save CSV outputs
    watchlist.to_csv(os.path.join(OUT_DIR, "exec_watchlist_high_cost_high_readm.csv"), index=False)
    top_cost.to_csv(os.path.join(OUT_DIR, "exec_top_cost_mspb.csv"), index=False)
    best_cost.to_csv(os.path.join(OUT_DIR, "exec_best_cost_mspb.csv"), index=False)
    top_readm.to_csv(os.path.join(OUT_DIR, "exec_top_readmissions_ratio.csv"), index=False)
    best_readm.to_csv(os.path.join(OUT_DIR, "exec_best_readmissions_ratio.csv"), index=False)

    # Executive summary markdown
    lines = []
    lines.append("# Executive Summary – Hospital Efficiency & Cost Effectiveness (CMS)\n")
    lines.append("This summary is generated from CMS Provider Data using two core signals:")
    lines.append("- **MSPB (Medicare Spending Per Beneficiary)**: relative Medicare spend for an episode of care.")
    lines.append("- **Readmissions (Excess Readmission Ratio)**: relative readmission performance vs expected.\n")

    lines.append("## Overall Coverage\n")
    lines.append(f"- Total hospitals in CMS General Information: **{df['facility_id'].nunique():,}**")
    lines.append(f"- Hospitals with MSPB: **{df['mspb_score'].notna().sum():,}**")
    lines.append(f"- Hospitals with Readmissions ratio: **{df['readm_ratio_mean'].notna().sum():,}**")
    lines.append(f"- Hospitals with BOTH metrics: **{len(both):,}**\n")

    lines.append("## Key Finding (So What)\n")
    lines.append(
        "A practical action list is the **Watchlist**: hospitals that are simultaneously **high-cost** and "
        "**high-readmission** relative to peers (top quartile for each). These are the best candidates for "
        "targeted operational review (care transitions, discharge planning, post-acute coordination, avoidable utilization).\n"
    )

    lines.append("## Thresholds Used\n")
    lines.append(f"- High-cost = MSPB >= 75th percentile (**{mspb_p75:.3f}**)")
    lines.append(f"- High-readmission = Readmissions ratio >= 75th percentile (**{readm_p75:.3f}**)")
    lines.append("- Ranking = z-scored composite: `z(MSPB) + z(Readmissions)`\n")

    def md_table(d: pd.DataFrame, cols):
        # ensure clean display
        return d[cols].to_markdown(index=False)

    show_cols = [
        "facility_id","facility_name","city_town","state",
        "mspb_score","readm_ratio_mean","efficiency_risk_score",
        "hospital_overall_rating","hospital_ownership"
    ]

    lines.append("## Watchlist (High Cost + High Readmissions)\n")
    if len(watchlist) == 0:
        lines.append("_No hospitals met the combined top-quartile thresholds in this data snapshot._\n")
    else:
        lines.append(md_table(watchlist, show_cols))
        lines.append("")

    lines.append("## Highest MSPB (Cost Outliers)\n")
    lines.append(md_table(top_cost, ["facility_id","facility_name","state","mspb_score","hospital_overall_rating"]))
    lines.append("")

    lines.append("## Worst Readmissions Ratio (Outliers)\n")
    lines.append(md_table(top_readm, ["facility_id","facility_name","state","readm_ratio_mean","readm_measure_count"]))
    lines.append("")

    lines.append("## Caveats & Assumptions\n")
    lines.append("- These are **public CMS measures**; they support screening and prioritization, not final judgment.")
    lines.append("- MSPB and Readmissions are **risk-adjusted** but still reflect case-mix and service line realities.")
    lines.append("- Many hospitals are missing one of the metrics in this snapshot; coverage is documented above.")
    lines.append("- The watchlist uses **quartiles**, making it robust across refreshes of the dataset.\n")

    out_md = os.path.join(OUT_DIR, "EXEC_SUMMARY.md")
    with open(out_md, "w") as f:
        f.write("\n".join(lines))

    print("Wrote:")
    print(" -", out_md)
    print(" -", os.path.join(OUT_DIR, "exec_watchlist_high_cost_high_readm.csv"))
    print(" -", os.path.join(OUT_DIR, "exec_top_cost_mspb.csv"))
    print(" -", os.path.join(OUT_DIR, "exec_top_readmissions_ratio.csv"))

if __name__ == "__main__":
    main()
