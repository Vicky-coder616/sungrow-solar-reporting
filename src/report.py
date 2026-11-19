"""Validate normalized readings and generate a demonstration monthly CSV."""

import argparse
from collections import defaultdict
import csv
from datetime import date
import json
import math
from pathlib import Path
import re


def aggregate(rows, month):
    if not isinstance(month, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}", month):
        raise ValueError("Month must be YYYY-MM")
    date.fromisoformat(month + "-01")
    if not isinstance(rows, list):
        raise ValueError("Input must be a list of readings")
    totals = defaultdict(float)
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Each reading must be an object")
        try:
            site = row["site_id"]
            if not isinstance(site, str) or not re.fullmatch(
                r"[A-Za-z0-9_.-]{1,100}", site
            ):
                raise ValueError("Invalid site identifier")
            raw_date = row["date"]
            if not isinstance(raw_date, str) or not re.fullmatch(
                r"[0-9]{4}-[0-9]{2}-[0-9]{2}", raw_date
            ):
                raise ValueError("Reading date must be YYYY-MM-DD")
            day = date.fromisoformat(raw_date)
            raw = row["energy_kwh"]
            if isinstance(raw, bool):
                raise ValueError("Energy must be a finite nonnegative number")
            energy = float(raw)
        except (KeyError, TypeError, OverflowError) as exc:
            raise ValueError("Missing or invalid reading fields") from exc
        if not math.isfinite(energy) or energy < 0:
            raise ValueError("Energy must be a finite nonnegative number")
        key = (site, day)
        if key in seen:
            raise ValueError("Duplicate site/day reading")
        seen.add(key)
        if day.strftime("%Y-%m") == month:
            totals[site] += energy
            if not math.isfinite(totals[site]):
                raise ValueError("Monthly total exceeds numeric range")
    return [
        {"month": month, "site_id": site, "energy_kwh": round(total, 3)}
        for site, total in sorted(totals.items())
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--month", required=True)
    parser.add_argument("--output", type=Path, default=Path("output/edms.csv"))
    args = parser.parse_args()
    try:
        result = aggregate(
            json.loads(args.input.read_text(encoding="utf-8")), args.month
        )
        if args.input.resolve() == args.output.resolve():
            raise ValueError("Input and output must differ")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(
                stream, fieldnames=["month", "site_id", "energy_kwh"]
            )
            writer.writeheader()
            writer.writerows(result)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Report failed: {exc}\n")
    print(f"Wrote {len(result)} site totals to {args.output}")


if __name__ == "__main__":
    main()
