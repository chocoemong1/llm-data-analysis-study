"""Human-reviewed Chapter 12 analysis candidate.

The module performs an in-memory completed-order aggregation.  It intentionally
contains no file I/O, network access, process execution, dynamic execution, or
package installation.  A separate, trusted harness controls inputs and outputs.
"""

from __future__ import annotations

import pandas as pd


TOLERANCE = 1e-6


def build_completed_sales(
    order_items: pd.DataFrame,
    products: pd.DataFrame,
    orders: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return validated category/monthly totals for completed orders."""
    items_required = {
        "order_item_id",
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
    }
    products_required = {"product_id", "category"}
    orders_required = {"order_id", "order_date", "order_status"}
    for name, frame, required in [
        ("order_items", order_items, items_required),
        ("products", products, products_required),
        ("orders", orders, orders_required),
    ]:
        missing = required - set(frame.columns)
        if missing:
            raise KeyError(f"{name} missing columns: {sorted(missing)}")

    if order_items["order_item_id"].isna().any() or order_items["order_item_id"].duplicated().any():
        raise ValueError("order_items.order_item_id must be a complete primary key")
    if products["product_id"].isna().any() or products["product_id"].duplicated().any():
        raise ValueError("products.product_id must be unique before merge")
    if orders["order_id"].isna().any() or orders["order_id"].duplicated().any():
        raise ValueError("orders.order_id must be unique before merge")

    items = order_items.copy()
    items["quantity"] = pd.to_numeric(items["quantity"], errors="coerce")
    items["unit_price"] = pd.to_numeric(items["unit_price"], errors="coerce")
    expected_line_total = items["quantity"] * items["unit_price"]
    if expected_line_total.isna().any():
        raise ValueError("quantity or unit_price conversion failed")
    if "line_total" in items.columns:
        observed_line_total = pd.to_numeric(items["line_total"], errors="coerce")
        mismatch = (observed_line_total - expected_line_total).abs().gt(TOLERANCE)
        if observed_line_total.isna().any() or mismatch.any():
            raise ValueError("line_total does not equal quantity * unit_price")
    items["line_total"] = expected_line_total

    item_rows = len(items)
    merged = items.merge(
        orders[["order_id", "order_date", "order_status"]],
        on="order_id",
        how="left",
        validate="many_to_one",
        indicator="_order_merge",
    )
    order_unmatched = int(merged["_order_merge"].ne("both").sum())
    if len(merged) != item_rows or order_unmatched:
        raise ValueError("order merge changed rows or left unmatched keys")

    completed = merged.loc[
        merged["order_status"].astype("string").str.strip().str.lower().eq("completed")
    ].drop(columns="_order_merge").copy()
    completed_rows = len(completed)
    if completed_rows == 0:
        raise ValueError("no completed order items")

    enriched = completed.merge(
        products[["product_id", "category"]],
        on="product_id",
        how="left",
        validate="many_to_one",
        indicator="_product_merge",
    )
    product_unmatched = int(enriched["_product_merge"].ne("both").sum())
    category_missing = int(enriched["category"].isna().sum())
    if len(enriched) != completed_rows or product_unmatched or category_missing:
        raise ValueError("product merge changed rows or left unmatched categories")
    enriched = enriched.drop(columns="_product_merge")

    category_sales = (
        enriched.groupby("category", as_index=False, dropna=False)
        .agg(total_quantity=("quantity", "sum"), total_sales=("line_total", "sum"))
        .sort_values("total_sales", ascending=False)
        .reset_index(drop=True)
    )
    category_total = float(category_sales["total_sales"].sum())
    category_sales["sales_ratio"] = (
        category_sales["total_sales"].div(category_total).mul(100).round(2)
        if category_total
        else 0.0
    )

    enriched["order_date"] = pd.to_datetime(enriched["order_date"], errors="coerce")
    date_failures = int(enriched["order_date"].isna().sum())
    if date_failures:
        raise ValueError("completed order_date conversion failed")
    enriched["order_month"] = enriched["order_date"].dt.to_period("M").astype("string")
    monthly_sales = (
        enriched.groupby("order_month", as_index=False, dropna=False)
        .agg(total_sales=("line_total", "sum"), order_count=("order_id", "nunique"))
        .sort_values("order_month")
        .reset_index(drop=True)
    )
    monthly_sales["avg_order_value"] = (
        monthly_sales["total_sales"].div(monthly_sales["order_count"]).round(0)
    )

    source_total = float(enriched["line_total"].sum())
    monthly_total = float(monthly_sales["total_sales"].sum())
    if abs(source_total - category_total) > TOLERANCE or abs(source_total - monthly_total) > TOLERANCE:
        raise ValueError("source, category, and monthly totals do not match")

    validation = pd.DataFrame(
        [
            {"check": "input_item_rows", "value": item_rows, "status": "PASS"},
            {"check": "order_merge_unmatched", "value": order_unmatched, "status": "PASS"},
            {"check": "completed_detail_rows", "value": completed_rows, "status": "PASS"},
            {"check": "product_merge_unmatched", "value": product_unmatched, "status": "PASS"},
            {"check": "category_missing", "value": category_missing, "status": "PASS"},
            {"check": "order_date_failures", "value": date_failures, "status": "PASS"},
            {"check": "completed_source_total", "value": source_total, "status": "PASS"},
            {"check": "category_grouped_total", "value": category_total, "status": "PASS"},
            {"check": "monthly_grouped_total", "value": monthly_total, "status": "PASS"},
        ]
    )
    return category_sales, monthly_sales, validation
