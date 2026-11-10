# Chapter 5 데이터 전처리 요약

## 전처리 결과 파일

- customers_clean.csv
- products_clean.csv
- orders_clean.csv
- order_items_clean.csv

## 전처리 전후 데이터 크기

```text
    dataset  rows_raw  columns_raw  rows_processed  columns_processed
  customers       152            6             150                  6
order_items       765            5             745                  6
     orders       302            5             298                  7
   products       102            4             100                  5
```

## 중복 점검 결과

```text
    dataset  row_duplicate_count    key_column  key_duplicate_count
  customers                    0   customer_id                    0
   products                    0    product_id                    0
     orders                    0      order_id                    0
order_items                    0 order_item_id                    0
```

## 파일 간 관계 점검 결과

```text
                                               check  invalid_count
  orders.customer_id exists in customers.customer_id              0
      order_items.order_id exists in orders.order_id              0
order_items.product_id exists in products.product_id              0
```

## 관계 불일치 보류 결과

```text
                                    reason  quarantined_rows
              orders.customer_id_not_found                 2
order_items.invalid_quantity_or_unit_price                11
            order_items.order_id_not_found                 6
          order_items.product_id_not_found                 2
      unique_order_items_quarantined_total                18
```

## 저장 후 CSV 재로딩 검증

```text
                                                         check    value status
                                               customers.shape (150, 6)   PASS
                                             customers.columns        6   PASS
                          customers.customer_id_unique_nonnull        0   PASS
                                                products.shape (100, 5)   PASS
                                              products.columns        5   PASS
                            products.product_id_unique_nonnull        0   PASS
                                                  orders.shape (298, 7)   PASS
                                                orders.columns        7   PASS
                                orders.order_id_unique_nonnull        0   PASS
                                             order_items.shape (745, 6)   PASS
                                           order_items.columns        6   PASS
                      order_items.order_item_id_unique_nonnull        0   PASS
                            customers.signup_date_reload_parse        0   PASS
                                orders.order_date_reload_parse        0   PASS
                                order_items.line_total_formula        0   PASS
  reload_fk:orders.customer_id exists in customers.customer_id        0   PASS
      reload_fk:order_items.order_id exists in orders.order_id        0   PASS
reload_fk:order_items.product_id exists in products.product_id        0   PASS
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
