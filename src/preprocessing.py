"""Chapter 5 데이터 전처리 공통 함수 모음.

이 모듈은 5장 노트북과 스크립트에서 함께 사용할 수 있는 전처리 함수를 제공합니다.
원본 DataFrame을 직접 수정하지 않고 항상 복사본을 반환하도록 작성했습니다.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


STATUS_MAP = {
    "complete": "completed",
    "Complete": "completed",
    "COMPLETED": "completed",
    "완료": "completed",
    "cancel": "cancelled",
    "Cancel": "cancelled",
    "CANCELLED": "cancelled",
    "취소": "cancelled",
    "refund": "refunded",
    "Refund": "refunded",
    "REFUNDED": "refunded",
    "환불": "refunded",
}


def check_missing_values(df: pd.DataFrame) -> pd.Series:
    """각 컬럼의 결측치 개수를 확인합니다."""
    return df.isna().sum()


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """중복 행을 제거한 새 DataFrame을 반환합니다."""
    return df.drop_duplicates().reset_index(drop=True)


def convert_date_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """문자열 날짜 컬럼을 datetime 형식으로 변환합니다."""
    result = df.copy()
    result[column] = pd.to_datetime(result[column], errors="coerce")
    return result


def missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """컬럼별 결측치 개수와 비율을 반환합니다."""
    summary = pd.DataFrame(
        {
            "missing_count": df.isna().sum(),
            "missing_ratio": (df.isna().mean() * 100).round(2),
        }
    )
    return summary.sort_values("missing_count", ascending=False)


def shape_summary(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """여러 DataFrame의 행/열 개수를 요약합니다."""
    rows = []
    for name, df in data.items():
        rows.append({"dataset": name, "rows": df.shape[0], "columns": df.shape[1]})
    return pd.DataFrame(rows)


def compare_shapes(
    raw_data: dict[str, pd.DataFrame],
    processed_data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """전처리 전후 데이터 크기를 비교합니다."""
    raw_shapes = shape_summary(raw_data).rename(
        columns={"rows": "rows_raw", "columns": "columns_raw"}
    )
    processed_shapes = shape_summary(processed_data).rename(
        columns={"rows": "rows_processed", "columns": "columns_processed"}
    )
    return raw_shapes.merge(processed_shapes, on="dataset", how="outer")


def duplicate_summary(
    data: dict[str, pd.DataFrame],
    key_columns: dict[str, str] | None = None,
) -> pd.DataFrame:
    """전체 행 중복과 주요 키 컬럼 중복을 요약합니다."""
    key_columns = key_columns or {}
    rows = []

    for name, df in data.items():
        key_col = key_columns.get(name)
        key_duplicate_count = None
        if key_col and key_col in df.columns:
            key_duplicate_count = int(df[key_col].duplicated().sum())

        rows.append(
            {
                "dataset": name,
                "row_duplicate_count": int(df.duplicated().sum()),
                "key_column": key_col,
                "key_duplicate_count": key_duplicate_count,
            }
        )

    return pd.DataFrame(rows)


def strip_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    """문자열 컬럼의 앞뒤 공백을 제거합니다.

    결측치를 문자열 'nan'으로 바꾸지 않기 위해 결측치는 그대로 유지합니다.
    """
    result = df.copy()
    string_columns = result.select_dtypes(include=["object", "string"]).columns

    for col in string_columns:
        result[col] = result[col].where(
            result[col].isna(),
            result[col].astype(str).str.strip(),
        )

    return result


def to_number(series: pd.Series) -> pd.Series:
    """쉼표가 포함된 문자열 숫자를 숫자형으로 변환합니다."""
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )


def normalize_order_status(series: pd.Series) -> pd.Series:
    """주문 상태값의 대표 표기를 통일합니다."""
    return series.replace(STATUS_MAP)


def preprocess_customers(df: pd.DataFrame) -> pd.DataFrame:
    """고객 데이터 전처리.

    처리 내용:
    - 문자열 앞뒤 공백 제거
    - age 숫자형 변환 및 중앙값 대체
    - city 결측치 Unknown 처리
    - signup_date 날짜형 변환
    - 완전 중복 행 제거
    """
    result = strip_string_columns(df)

    if "age" in result.columns:
        result["age"] = pd.to_numeric(result["age"], errors="coerce")
        if result["age"].notna().any():
            result["age"] = result["age"].fillna(result["age"].median())

    if "city" in result.columns:
        result["city"] = result["city"].fillna("Unknown")

    if "signup_date" in result.columns:
        result["signup_date"] = pd.to_datetime(result["signup_date"], errors="coerce")

    return result.drop_duplicates()


def preprocess_products(df: pd.DataFrame) -> pd.DataFrame:
    """상품 데이터 전처리.

    처리 내용:
    - 문자열 앞뒤 공백 제거
    - price 숫자형 변환
    - 변환 실패·0 이하 price는 검토 대상으로 표시하고 결측 처리
    - 상품 행은 유지하여 order_items와의 참조 관계를 보존
    - 완전 중복 행 제거
    """
    result = strip_string_columns(df)

    if "price" in result.columns:
        converted_price = to_number(result["price"])
        conversion_failed = result["price"].notna() & converted_price.isna()
        nonpositive = converted_price.notna() & converted_price.le(0)

        result["price"] = converted_price
        price_issue = conversion_failed | nonpositive
        if price_issue.any():
            result["price_quality_status"] = "valid"
            result.loc[conversion_failed, "price_quality_status"] = "conversion_failed"
            result.loc[nonpositive, "price_quality_status"] = "nonpositive_review"
            result.loc[price_issue, "price"] = float("nan")

    return result.drop_duplicates()


def preprocess_orders(df: pd.DataFrame) -> pd.DataFrame:
    """주문 데이터 전처리.

    처리 내용:
    - 문자열 앞뒤 공백 제거
    - order_status 대표 표기 통일
    - order_date 날짜형 변환
    - order_month, order_dayofweek 파생 컬럼 생성
    - 완전 중복 행 제거
    """
    result = strip_string_columns(df)

    if "order_status" in result.columns:
        result["order_status"] = normalize_order_status(result["order_status"])

    if "order_date" in result.columns:
        result["order_date"] = pd.to_datetime(result["order_date"], errors="coerce")
        result["order_month"] = result["order_date"].dt.to_period("M").astype(str)
        result["order_dayofweek"] = result["order_date"].dt.day_name()

    return result.drop_duplicates()


def preprocess_order_items(df: pd.DataFrame) -> pd.DataFrame:
    """주문 상세 데이터 전처리.

    처리 내용:
    - 문자열 앞뒤 공백 제거
    - quantity, unit_price 숫자형 변환
    - quantity와 unit_price가 0 이하인 행 제외
    - line_total 파생 컬럼 생성
    - 완전 중복 행 제거
    """
    result = strip_string_columns(df)

    if "quantity" in result.columns:
        result["quantity"] = to_number(result["quantity"])
        result = result[result["quantity"] > 0]

    if "unit_price" in result.columns:
        result["unit_price"] = to_number(result["unit_price"])
        result = result[result["unit_price"] > 0]

    if {"quantity", "unit_price"}.issubset(result.columns):
        result["line_total"] = result["quantity"] * result["unit_price"]

    return result.drop_duplicates()


def preprocess_sales_data_with_audit(
    data: dict[str, pd.DataFrame],
) -> tuple[
    dict[str, pd.DataFrame],
    dict[str, pd.DataFrame],
    pd.DataFrame,
]:
    """데이터를 전처리하고 관계 불일치 행을 별도 보류합니다.

    원본에 이미 존재하는 FK 불일치를 임의 값으로 채우지 않습니다. 분석용 clean
    테이블에서는 제외하되, 원인 확인이 가능하도록 quarantine DataFrame과 건수
    Evidence를 함께 반환합니다.
    """
    raw_items_for_audit = strip_string_columns(data["order_items"]).drop_duplicates()
    audit_quantity = to_number(raw_items_for_audit["quantity"])
    audit_unit_price = to_number(raw_items_for_audit["unit_price"])
    invalid_item_value = (
        audit_quantity.isna()
        | audit_unit_price.isna()
        | audit_quantity.le(0)
        | audit_unit_price.le(0)
    )
    value_quarantine = raw_items_for_audit.loc[invalid_item_value].copy()
    value_quarantine["quantity"] = audit_quantity.loc[invalid_item_value]
    value_quarantine["unit_price"] = audit_unit_price.loc[invalid_item_value]
    value_quarantine["quarantine_reason"] = "invalid_quantity_or_unit_price"

    processed = {
        "customers": preprocess_customers(data["customers"]),
        "products": preprocess_products(data["products"]),
        "orders": preprocess_orders(data["orders"]),
        "order_items": preprocess_order_items(data["order_items"]),
    }

    invalid_customer = ~processed["orders"]["customer_id"].isin(
        processed["customers"]["customer_id"]
    )
    orders_quarantine = processed["orders"].loc[invalid_customer].copy()
    orders_quarantine["quarantine_reason"] = "customer_id_not_found"
    processed["orders"] = processed["orders"].loc[~invalid_customer].copy()

    invalid_order = ~processed["order_items"]["order_id"].isin(
        processed["orders"]["order_id"]
    )
    invalid_product = ~processed["order_items"]["product_id"].isin(
        processed["products"]["product_id"]
    )
    item_quarantine_mask = invalid_order | invalid_product
    order_items_quarantine = processed["order_items"].loc[
        item_quarantine_mask
    ].copy()
    order_items_quarantine["quarantine_reason"] = [
        ";".join(
            reason
            for condition, reason in [
                (order_bad, "order_id_not_found"),
                (product_bad, "product_id_not_found"),
            ]
            if condition
        )
        for order_bad, product_bad in zip(
            invalid_order.loc[item_quarantine_mask],
            invalid_product.loc[item_quarantine_mask],
        )
    ]
    processed["order_items"] = processed["order_items"].loc[
        ~item_quarantine_mask
    ].copy()

    order_items_quarantine = pd.concat(
        [value_quarantine, order_items_quarantine],
        ignore_index=True,
        sort=False,
    ).drop_duplicates(subset=["order_item_id"], keep="first")

    quarantine = {
        "orders": orders_quarantine,
        "order_items": order_items_quarantine,
    }
    quarantine_summary = pd.DataFrame(
        [
            {
                "reason": "orders.customer_id_not_found",
                "quarantined_rows": int(invalid_customer.sum()),
            },
            {
                "reason": "order_items.invalid_quantity_or_unit_price",
                "quarantined_rows": int(invalid_item_value.sum()),
            },
            {
                "reason": "order_items.order_id_not_found",
                "quarantined_rows": int(invalid_order.sum()),
            },
            {
                "reason": "order_items.product_id_not_found",
                "quarantined_rows": int(invalid_product.sum()),
            },
            {
                "reason": "unique_order_items_quarantined_total",
                "quarantined_rows": len(order_items_quarantine),
            },
        ]
    )
    return processed, quarantine, quarantine_summary


def preprocess_sales_data(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """쇼핑몰 실습 데이터 4종을 전처리하고 FK 일관성을 확보합니다."""
    processed, _, _ = preprocess_sales_data_with_audit(data)
    return processed


def validate_relationships(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """전처리 후 파일 간 키 관계가 유지되는지 확인합니다."""
    customers = data["customers"]
    products = data["products"]
    orders = data["orders"]
    order_items = data["order_items"]

    checks = []

    if {"customer_id"}.issubset(customers.columns) and {"customer_id"}.issubset(orders.columns):
        invalid_customers = orders[~orders["customer_id"].isin(customers["customer_id"])]
        checks.append(
            {
                "check": "orders.customer_id exists in customers.customer_id",
                "invalid_count": len(invalid_customers),
            }
        )

    if {"order_id"}.issubset(orders.columns) and {"order_id"}.issubset(order_items.columns):
        invalid_orders = order_items[~order_items["order_id"].isin(orders["order_id"])]
        checks.append(
            {
                "check": "order_items.order_id exists in orders.order_id",
                "invalid_count": len(invalid_orders),
            }
        )

    if {"product_id"}.issubset(products.columns) and {"product_id"}.issubset(order_items.columns):
        invalid_products = order_items[
            ~order_items["product_id"].isin(products["product_id"])
        ]
        checks.append(
            {
                "check": "order_items.product_id exists in products.product_id",
                "invalid_count": len(invalid_products),
            }
        )

    return pd.DataFrame(checks)


def save_processed_data(
    data: dict[str, pd.DataFrame],
    output_dir: str | Path = "data/processed",
    encoding: str = "utf-8-sig",
) -> list[Path]:
    """전처리 결과를 CSV 파일로 저장하고 저장 경로 목록을 반환합니다."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    file_map = {
        "customers": "customers_clean.csv",
        "products": "products_clean.csv",
        "orders": "orders_clean.csv",
        "order_items": "order_items_clean.csv",
    }

    saved_paths: list[Path] = []
    for name, filename in file_map.items():
        path = output_path / filename
        data[name].to_csv(path, index=False, encoding=encoding)
        saved_paths.append(path)

    return saved_paths


def save_quarantine_data(
    quarantine: dict[str, pd.DataFrame],
    output_dir: str | Path = "data/processed/quarantine",
    encoding: str = "utf-8-sig",
) -> list[Path]:
    """clean에서 제외한 값·관계 검토 행을 별도 CSV로 저장합니다."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    file_map = {
        "orders": "orders_quarantine.csv",
        "order_items": "order_items_quarantine.csv",
    }
    saved_paths = []
    for name, filename in file_map.items():
        path = output_path / filename
        quarantine[name].to_csv(path, index=False, encoding=encoding)
        saved_paths.append(path)
    return saved_paths


def load_saved_processed_data(
    output_dir: str | Path = "data/processed",
) -> dict[str, pd.DataFrame]:
    """저장된 clean CSV 4개를 새 DataFrame으로 다시 읽습니다."""
    output_path = Path(output_dir)
    file_map = {
        "customers": "customers_clean.csv",
        "products": "products_clean.csv",
        "orders": "orders_clean.csv",
        "order_items": "order_items_clean.csv",
    }
    return {
        name: pd.read_csv(output_path / filename)
        for name, filename in file_map.items()
    }


def validate_saved_processed_data(
    expected_data: dict[str, pd.DataFrame],
    output_dir: str | Path = "data/processed",
) -> pd.DataFrame:
    """CSV 재로딩 후 구조·키·날짜·계산·FK를 검증합니다."""
    reloaded = load_saved_processed_data(output_dir)
    rows: list[dict[str, object]] = []

    key_columns = {
        "customers": "customer_id",
        "products": "product_id",
        "orders": "order_id",
        "order_items": "order_item_id",
    }
    for name, expected in expected_data.items():
        actual = reloaded[name]
        rows.extend(
            [
                {
                    "check": f"{name}.shape",
                    "value": str(actual.shape),
                    "status": "PASS" if actual.shape == expected.shape else "FAIL",
                },
                {
                    "check": f"{name}.columns",
                    "value": len(actual.columns),
                    "status": "PASS"
                    if list(actual.columns) == list(expected.columns)
                    else "FAIL",
                },
                {
                    "check": f"{name}.{key_columns[name]}_unique_nonnull",
                    "value": int(
                        actual[key_columns[name]].duplicated().sum()
                        + actual[key_columns[name]].isna().sum()
                    ),
                    "status": "PASS"
                    if actual[key_columns[name]].is_unique
                    and actual[key_columns[name]].notna().all()
                    else "FAIL",
                },
            ]
        )

    for name, column in [
        ("customers", "signup_date"),
        ("orders", "order_date"),
    ]:
        source = reloaded[name][column]
        new_failures = int(
            (source.notna() & pd.to_datetime(source, errors="coerce").isna()).sum()
        )
        rows.append(
            {
                "check": f"{name}.{column}_reload_parse",
                "value": new_failures,
                "status": "PASS" if new_failures == 0 else "FAIL",
            }
        )

    formula_mismatch = int(
        (
            reloaded["order_items"]["line_total"]
            != reloaded["order_items"]["quantity"]
            * reloaded["order_items"]["unit_price"]
        ).sum()
    )
    rows.append(
        {
            "check": "order_items.line_total_formula",
            "value": formula_mismatch,
            "status": "PASS" if formula_mismatch == 0 else "FAIL",
        }
    )

    for row in validate_relationships(reloaded).to_dict("records"):
        rows.append(
            {
                "check": "reload_fk:" + str(row["check"]),
                "value": int(row["invalid_count"]),
                "status": "PASS" if int(row["invalid_count"]) == 0 else "FAIL",
            }
        )
    return pd.DataFrame(rows)


def build_preprocessing_report(
    raw_data: dict[str, pd.DataFrame],
    processed_data: dict[str, pd.DataFrame],
    relationship_checks: pd.DataFrame,
    quarantine_summary: pd.DataFrame | None = None,
    reload_validation: pd.DataFrame | None = None,
) -> str:
    """전처리 결과 요약 Markdown 문자열을 생성합니다."""
    comparison = compare_shapes(raw_data, processed_data)
    duplicate_checks = duplicate_summary(
        processed_data,
        key_columns={
            "customers": "customer_id",
            "products": "product_id",
            "orders": "order_id",
            "order_items": "order_item_id",
        },
    )

    quarantine_text = (
        quarantine_summary.to_string(index=False)
        if quarantine_summary is not None
        else "기록 없음"
    )
    reload_text = (
        reload_validation.to_string(index=False)
        if reload_validation is not None
        else "기록 없음"
    )

    return f"""# Chapter 5 데이터 전처리 요약

## 전처리 결과 파일

- customers_clean.csv
- products_clean.csv
- orders_clean.csv
- order_items_clean.csv

## 전처리 전후 데이터 크기

```text
{comparison.to_string(index=False)}
```

## 중복 점검 결과

```text
{duplicate_checks.to_string(index=False)}
```

## 파일 간 관계 점검 결과

```text
{relationship_checks.to_string(index=False)}
```

## 관계 불일치 보류 결과

```text
{quarantine_text}
```

## 저장 후 CSV 재로딩 검증

```text
{reload_text}
```

## 주요 처리 내용

- 원본 데이터는 직접 수정하지 않고 복사본을 사용했습니다.
- 문자열 컬럼의 앞뒤 공백을 제거했습니다.
- 고객 나이 결측치는 중앙값으로 대체했습니다.
- 고객 도시 결측치는 Unknown으로 처리했습니다.
- 주문 상태값 표기를 completed, cancelled, refunded 중심으로 통일했습니다.
- 날짜 컬럼을 날짜형으로 변환하고 주문 월/요일 파생 컬럼을 만들었습니다.
- 가격, 수량, 단가를 숫자형으로 변환했습니다.
- 변환 실패·0 이하 상품 가격은 상품 행을 삭제하지 않고 검토 상태로 남겼습니다.
- 관계 불일치 주문·주문상세는 clean 데이터에서 제외하고 quarantine에 보존했습니다.
- 저장된 CSV를 다시 읽어 구조·키·날짜·계산식·FK를 검증했습니다.
- 주문 상세 금액 line_total 파생 컬럼을 생성했습니다.
- 전처리 후 파일 간 키 관계를 다시 확인했습니다.

## 주의 사항

이 전처리 기준은 실습용 예시입니다. 실제 업무에서는 결측치와 이상값을 삭제하거나 대체하기 전에 원본 시스템, 수집 과정, 업무 담당자 확인이 필요합니다.
"""
