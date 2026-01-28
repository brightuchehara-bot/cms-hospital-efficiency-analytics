import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
OUT_FILE = Path("docs/01_data_profile.md")


def main():
    lines = []

    lines.append("# CMS Hospital Efficiency – Raw Data Profile\n\n")
    lines.append(
        "This report documents raw file structure, row counts, column definitions, "
        "and join keys for CMS hospital datasets.\n\n"
    )

    for csv in sorted(RAW_DIR.glob("*.csv")):
        df = pd.read_csv(csv, low_memory=False)

        lines.append(f"## {csv.name}\n")
        lines.append(f"- Rows: **{len(df):,}**\n")
        lines.append(f"- Columns: **{len(df.columns)}**\n\n")

        lines.append("### Columns\n")
        for col in df.columns:
            missing = df[col].isna().mean() * 100
            lines.append(f"- `{col}` (missing: {missing:.1f}%)\n")

        lines.append("\n")

    OUT_FILE.parent.mkdir(exist_ok=True)
    OUT_FILE.write_text("".join(lines))
    print(f"Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
