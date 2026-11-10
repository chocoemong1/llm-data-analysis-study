"""Chapter 6 EDA 실행 스크립트.

실행 방법:
    python scripts/run_eda.py

전제 조건:
    python scripts/preprocess_data.py

입력:
    data/processed/customers_clean.csv
    data/processed/products_clean.csv
    data/processed/orders_clean.csv
    data/processed/order_items_clean.csv

출력:
    reports/ch06_category_sales.csv
    reports/ch06_monthly_sales.csv
    reports/ch06_customer_sales.csv
    reports/ch06_eda_questions.csv
    reports/ch06_customer_city.csv
    reports/ch06_product_category.csv
    reports/ch06_payment_sales.csv
    reports/ch06_eda_summary.md
"""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.eda import (
    build_eda_report,
    load_processed_sales_data,
    run_basic_eda,
    save_eda_outputs,
)
from src.output_validation import validate_saved_csv_tables, validate_saved_files
from src.preprocessing import validate_saved_processed_data


PROCESSED_DIR = PROJECT_ROOT / "data/processed"
REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_PATH = REPORT_DIR / "ch06_eda_summary.md"
INPUT_RELOAD_PATH = REPORT_DIR / "ch06_input_reload_validation.csv"
OUTPUT_RELOAD_PATH = REPORT_DIR / "ch06_output_reload_validation.csv"
FILE_VALIDATION_PATH = REPORT_DIR / "ch06_file_validation.csv"


def main() -> None:
    """전처리된 데이터를 불러와 6장 기본 EDA 결과와 요약 보고서를 저장합니다."""
    REPORT_DIR.mkdir(exist_ok=True)

    data = load_processed_sales_data(PROCESSED_DIR)
    input_reload_validation = validate_saved_processed_data(data, PROCESSED_DIR)
    input_reload_validation.to_csv(
        INPUT_RELOAD_PATH, index=False, encoding="utf-8-sig"
    )
    if not input_reload_validation["status"].eq("PASS").all():
        raise ValueError("Chapter 06 입력 CSV 재로딩 검증 실패")

    results = run_basic_eda(data)
    saved_paths = save_eda_outputs(results, REPORT_DIR)

    output_keys = {
        "ch06_category_sales.csv": "category_sales",
        "ch06_monthly_sales.csv": "monthly_sales",
        "ch06_customer_sales.csv": "customer_sales",
        "ch06_eda_questions.csv": "eda_result_summary",
        "ch06_customer_city.csv": "customer_city",
        "ch06_product_category.csv": "product_category",
        "ch06_payment_sales.csv": "payment_sales",
        "ch06_merge_checks.csv": "merge_checks",
        "ch06_total_validation.csv": "total_validation",
    }
    output_reload_validation = validate_saved_csv_tables(
        {
            filename: (results[key], REPORT_DIR / filename)
            for filename, key in output_keys.items()
        }
    )
    output_reload_validation.to_csv(
        OUTPUT_RELOAD_PATH, index=False, encoding="utf-8-sig"
    )
    if not output_reload_validation["status"].eq("PASS").all():
        raise ValueError("Chapter 06 저장 산출물 재로딩 검증 실패")

    report_text = build_eda_report(results)
    REPORT_PATH.write_text(report_text, encoding="utf-8")
    file_validation = validate_saved_files([REPORT_PATH])
    file_validation.to_csv(
        FILE_VALIDATION_PATH, index=False, encoding="utf-8-sig"
    )
    if not file_validation["status"].eq("PASS").all():
        raise ValueError("Chapter 06 요약 보고서 파일 검증 실패")

    print("6장 EDA 완료")
    completed_items = results["completed_items"]
    print("\n[completed 주문 Gate]")
    print(f"completed 상세 행: {len(completed_items)}")
    print(f"completed 고유 주문 수: {completed_items['order_id'].nunique()}")
    print(f"completed 주문 기준 금액: {completed_items['line_total'].sum():.0f}")
    print("\n[병합 검증]")
    print(results["merge_checks"].to_string(index=False))
    print("\n[카테고리별 매출 상위 5개]")
    print(results["category_sales"].head().to_string(index=False))
    print("\n[월별 매출]")
    print(results["monthly_sales"].to_string(index=False))
    print("\n[고객별 구매 금액 상위 5명]")
    print(results["customer_sales"].head().to_string(index=False))
    print("\n[결제수단별 completed 주문]")
    print(results["payment_sales"].to_string(index=False))
    print("\n[집계 총합 검증]")
    print(results["total_validation"].to_string(index=False))
    print("\n[입력 CSV 재로딩 검증]")
    print(input_reload_validation.to_string(index=False))
    print("\n[저장 산출물 재로딩 검증]")
    print(output_reload_validation.to_string(index=False))
    print("\n[요약 보고서 파일 검증]")
    print(file_validation.to_string(index=False))
    print("\n[저장된 CSV 파일]")
    for path in saved_paths:
        print(f"- {path}")
    print(f"\n[요약 보고서] {REPORT_PATH}")


if __name__ == "__main__":
    main()
