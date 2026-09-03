# 학습 기록

## Overview — 전체 학습 로드맵과 준비 상태 확인

### 학습 날짜

2026-09-03

### 오늘 공부한 내용

- 강사 Public 저장소는 원본 가이드·Notebook·샘플 데이터·실행 코드를 제공한다.
- 개인 저장소는 내가 수행한 답안·Evidence·관찰·해석·판단을 누적하는 공간이다.
- Chapter 01~02는 Markdown, Chapter 03~15는 실행 완료 Notebook이 기본 제출 파일이다.
- 제출물에는 수행 내용, 결과, 관찰, 해석과 판단, 업무적 의미, 한계가 함께 있어야 한다.
- 최종 제출 시 저장소 루트가 아니라 해당 Chapter의 최종 파일 URL을 사용한다.
- LLM 출력은 초안이며 실제 컬럼·계산식·결과와 대조한 뒤 사람이 최종 판단한다.
- 실제 개인정보와 API Key·Token·Password는 Prompt, Notebook, 이미지, Public GitHub에 포함하지 않는다.

### 실행한 코드

```bash
./llm-data-analysis-course/.venv/bin/python --version
git --version
./llm-data-analysis-course/.venv/bin/python -m pip check
```

샘플 CSV는 pandas로 읽어 shape, 컬럼, 키 연결의 미매칭 개수를 확인했다.

### 실행 결과

| 항목 | 확인 결과 |
| --- | --- |
| Python | 3.12.3 |
| Git | 2.43.0 |
| pandas | 3.0.5 |
| NumPy | 2.5.2 |
| Matplotlib | 3.11.1 |
| scikit-learn | 1.9.0 |
| 의존성 검사 | `No broken requirements found` |

| 데이터 | 행 × 열 | 주요 키 또는 연결 컬럼 |
| --- | ---: | --- |
| `customers.csv` | 150 × 6 | `customer_id` |
| `products.csv` | 100 × 4 | `product_id` |
| `orders.csv` | 300 × 5 | `order_id`, `customer_id` |
| `order_items.csv` | 764 × 5 | `order_item_id`, `order_id`, `product_id` |

세 FK 연결에서 미매칭 행은 모두 0건이었다. 이는 파일 간 참조 키가 현재 샘플 데이터 범위에서 연결된다는 뜻이며, 중복·결측·자료형 등 전체 품질이 검증됐다는 뜻은 아니다.

### 새롭게 이해한 개념

- 코드 실행 성공과 분석 타당성은 별개의 문제다.
- 데이터 한 행의 의미와 집계 단위를 먼저 정의해야 한다.
- 관찰된 사실, 해석, 가설, 추가 검증을 구분해서 기록해야 한다.
- 동일한 가상 쇼핑몰 데이터를 여러 장에서 정제·EDA·예측·자동화로 확장한다.

### 발생한 오류와 해결 방법

- 현재 환경은 Windows PowerShell이 아니라 Linux/bash이므로 PowerShell 전용 명령은 Linux 명령으로 바꿔야 한다.
- 패키지는 공식 저장소의 `.venv`에 이미 설치되어 있으며 `pip check`를 통과했다.
- VS Code 인터프리터와 Notebook 커널의 실제 선택 상태는 IDE 화면에서 별도 확인이 필요하다.

### 아직 이해되지 않거나 추가 확인할 부분

- Chapter 01에서 선택한 분석 질문이 실제 샘플 데이터의 기간·주문 상태·금액 정의로 계산 가능한지 검증해야 한다.
- Chapter 02에서 터미널 Python과 Notebook의 `sys.executable`이 동일한 `.venv`를 가리키는지 화면으로 확인해야 한다.

### 프로젝트에 적용한 내용

- 공식 저장소 `llm-data-analysis-course`는 원본 자료로 유지한다.
- 개인 저장소 `llm-data-analysis-study`에는 Chapter별 최종 답안과 Evidence만 기록한다.
- `.gitignore`로 `.env`, 가상환경, 캐시, 키 파일과 IDE 로컬 설정을 제외한다.

### 다음 학습 목표

Chapter 01에서 다음의 막연한 비즈니스 문제를 분석 가능한 질문으로 구체화한다.

```text
요즘 매출이 줄어든 것 같은데 왜 그런가요?
```

## Chapter 01 — 질문 정의와 LLM 제안 검증

### 학습 날짜

2026-09-03

### 수행한 내용

- 막연한 매출 감소 질문의 대상·기간·기준·비교·목적을 정의했다.
- LLM에서 질문 후보 5개를 얻고 월별 금액·주문 수·주문당 평균·카테고리 관점을 결합했다.
- 실제 CSV의 스키마, 날짜 범위, 주문 상태, PK 중복, FK 미매칭과 필수 컬럼 결측을 검증했다.
- 공식 Chapter 01 Notebook을 메모리에서 실행하고 코드 셀 오류가 0건임을 확인했다.
- Prompt Log와 실제 반영·수정·보류 이유를 기록했다.

### 핵심 결과

- 비교 기간: 2026-01-01~2026-06-30
- 계산 범위: `completed` 주문의 `quantity × unit_price`
- 5월 상품금액: 8,063,000, 완료 주문 11건, 주문당 평균 733,000
- 6월 상품금액: 2,826,000, 완료 주문 4건, 주문당 평균 706,500
- 상품금액 변화: -5,237,000

### 나의 판단

LLM 제안은 기간과 금액 정의가 없어 그대로 사용하지 않았다. 7월은 8일까지의 불완전한 월이라 제외하고, 상품금액이 회계상 순매출이 아니라는 한계를 명시한 뒤 수정 후 사용했다. 5→6월 감소는 완료 주문 수 감소와 함께 나타났지만, 원인을 확정할 추가 데이터는 없다.

### 오류와 주의점

Notebook 셀은 정상 실행됐지만 자동 실행 종료 과정에서 heartbeat 포트 경고가 한 번 발생했다. Chapter 02에서 VS Code의 인터프리터와 Notebook 커널이 같은 `.venv`를 사용하는지 화면으로 재확인한다.

### 다음 학습 목표

Chapter 02에서 Python·Git·가상환경·Jupyter 경로를 재현 가능한 Evidence로 확인한다.
