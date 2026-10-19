"""Data-contract test: does aqi_delhi_clean.csv match the agreed schema and rules?

Run from the repo root:
    python src/check_contract.py
    python src/check_contract.py path/to/other_file.csv

Exit code 0 means every hard check passed; 1 means at least one failed.
Warnings do not fail the check but are explained in the wrangling notebook.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils import (BUCKETS, CONTRACT_COLUMNS, DATA_CLEAN, GROUPS, POLLUTANTS,  # noqa: E402
                       SEASONS, WINDOW_END, WINDOW_START, aqi_bucket, aqi_group,
                       season_of)

failures: list[str] = []
warnings: list[str] = []


def check(ok: bool, label: str, detail: str = "") -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail and not ok else ""))
    if not ok:
        failures.append(label)


def warn(ok: bool, label: str, detail: str = "") -> None:
    if not ok:
        print(f"  [WARN] {label}" + (f"  ({detail})" if detail else ""))
        warnings.append(label)
    else:
        print(f"  [PASS] {label}")


def main(path: Path) -> int:
    print(f"Checking {path}\n")
    if not path.exists():
        print("  [FAIL] file exists")
        return 1
    df = pd.read_csv(path)

    missing_cols = [c for c in CONTRACT_COLUMNS if c not in df.columns]
    check(not missing_cols, "all contract columns present", f"missing: {missing_cols}")
    if missing_cols:
        return 1

    # Dates
    dates = pd.to_datetime(df["Date"], errors="coerce")
    check(dates.notna().all(), "every Date parses")
    check(dates.is_monotonic_increasing, "Date sorted ascending")
    check(not dates.duplicated().any(), "no duplicate dates")
    expected = pd.date_range(WINDOW_START, WINDOW_END, freq="D")
    check(
        len(dates) == len(expected) and (dates.reset_index(drop=True) == expected).all(),
        f"daily dates {WINDOW_START} to {WINDOW_END} with no gaps",
        f"got {len(dates)} rows, expected {len(expected)}",
    )

    # Values
    num_cols = POLLUTANTS + ["AQI"]
    check(df[num_cols].notna().all().all(), "no missing values in pollutants and AQI",
          str(df[num_cols].isna().sum()[lambda s: s > 0].to_dict()))
    check((df[POLLUTANTS] >= 0).all().all(), "pollutants are zero or more")
    check((df["AQI"] > 0).all(), "AQI above zero")

    # Derived columns
    check(set(df["AQI_Bucket"].dropna().unique()) <= set(BUCKETS), "AQI_Bucket values valid")
    check(df["AQI_Bucket"].notna().all(), "no missing AQI_Bucket")
    mism = (df["AQI_Bucket"] != df["AQI"].map(aqi_bucket)).sum()
    warn(mism == 0, "AQI_Bucket agrees with AQI bands", f"{mism} rows differ")

    check(df["Month"].between(1, 12).all(), "Month is 1 to 12")
    check((df["Month"] == dates.dt.month).all(), "Month matches Date")
    check((df["Year"] == dates.dt.year).all(), "Year matches Date")
    check(set(df["Season"].unique()) <= set(SEASONS), "Season values valid")
    check((df["Season"] == df["Month"].map(season_of)).all(), "Season matches Month")
    check(set(df["Poor_Flag"].unique()) <= {0, 1}, "Poor_Flag is 0 or 1")
    check((df["Poor_Flag"] == (df["AQI"] > 200).astype(int)).all(), "Poor_Flag equals AQI above 200")
    check(set(df["AQI_Group"].unique()) <= set(GROUPS), "AQI_Group values valid")
    check((df["AQI_Group"] == df["AQI"].map(aqi_group)).all(), "AQI_Group matches AQI")

    print()
    if failures:
        print(f"RESULT: FAIL ({len(failures)} failed, {len(warnings)} warnings)")
        return 1
    print(f"RESULT: PASS ({len(warnings)} warnings)")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_CLEAN
    sys.exit(main(target))
