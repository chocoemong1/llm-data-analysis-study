"""Trusted Chapter 12 harness for a reviewed, in-memory analysis candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ch12_approved_analysis import build_completed_sales  # noqa: E402


REQUIRED_INPUTS = {
    "products": "products_clean.csv",
    "orders": "orders_clean.csv",
    "order_items": "order_items_clean.csv",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    input_dir = args.input_dir.resolve(strict=True)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    frames = {
        name: pd.read_csv(input_dir / filename)
        for name, filename in REQUIRED_INPUTS.items()
    }
    category_sales, monthly_sales, validation = build_completed_sales(
        frames["order_items"], frames["products"], frames["orders"]
    )

    category_sales.to_csv(output_dir / "category_sales.csv", index=False, encoding="utf-8-sig")
    monthly_sales.to_csv(output_dir / "monthly_sales.csv", index=False, encoding="utf-8-sig")
    validation.to_csv(output_dir / "post_validation.csv", index=False, encoding="utf-8-sig")
    summary = {
        "input_rows": {name: int(len(frame)) for name, frame in frames.items()},
        "output_rows": {
            "category_sales": int(len(category_sales)),
            "monthly_sales": int(len(monthly_sales)),
            "post_validation": int(len(validation)),
        },
        "all_checks_pass": bool(validation["status"].eq("PASS").all()),
    }
    (output_dir / "execution_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
