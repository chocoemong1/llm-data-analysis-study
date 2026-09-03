# Chapter 01 제출 답안. AI와 함께하는 데이터 분석의 시작

> 강사 저장소의 원본은 수정하지 않고, 공개 가능한 가상 쇼핑몰 데이터와 비식별 집계값만 사용했습니다.

---

## 0. 제출 정보

- 이름: `chocoemong1` (GitHub ID 기준)
- GitHub ID: `chocoemong1`
- 개인 저장소명: `llm-data-analysis-study`
- 작성일: 2026-09-03
- 사용한 LLM: OpenAI Codex

### 최종 제출 URL

```text
https://github.com/chocoemong1/llm-data-analysis-study/blob/main/chapter01/chapter01.md
```

---

## 1. 원래 업무 질문

### 내가 선택한 막연한 질문

```text
요즘 매출이 줄어든 것 같은데 왜 그런가요?
```

### 왜 이 질문이 모호하다고 생각했는가?

- 대상: 매출이 주문금액인지 상품금액인지, 어떤 주문 상태를 포함하는지 정의되지 않았다.
- 기간: “요즘”의 시작일과 종료일이 없다.
- 기준: 월별·주별 등 집계 단위와 할인·배송비·세금·환불의 반영 여부가 없다.
- 비교 방법: 전월 대비인지 전년 동기 대비인지 정해지지 않았다.
- 분석 목적: 감소 사실 확인, 감소 구성 요인 탐색, 원인 규명 중 무엇이 목적인지 불분명하다.

### 분석 가능한 질문으로 다시 작성

```text
2026년 1월부터 6월까지 completed 주문의 월별 상품금액
(quantity × unit_price), 완료 주문 수, 주문당 평균금액은 어떻게 변했는가?
5월 대비 6월의 상품금액 감소는 어떤 카테고리에서 발생했는가?
```

### 결과 관찰

대상은 `completed` 주문, 기간은 완전한 6개 월인 2026년 1~6월, 금액은 `quantity × unit_price`의 합, 비교 단위는 월별과 카테고리별로 구체화했다. 원본 데이터의 마지막 날짜가 2026-07-08이므로 7월은 불완전한 월로 판단해 제외했다.

### 나의 해석과 판단

수정한 질문은 필요한 필터·계산식·그룹 기준을 코드로 옮길 수 있다. “왜”라는 표현은 현재 데이터에 없는 마케팅, 트래픽, 경쟁사 변화까지 원인으로 단정하게 만들 수 있으므로, 우선 관찰 가능한 주문 수·주문당 평균금액·카테고리 기여를 확인하도록 바꿨다.

### 업무·분석적 의미

금액 감소를 주문 수 변화와 주문당 평균금액 변화로 나누고 카테고리별 기여를 확인하면, 다음 단계에서 유입·전환·재고·프로모션 중 어떤 추가 데이터를 우선 조사할지 정할 수 있다.

### 한계와 추가 확인 사항

여기서 계산한 상품금액은 할인·쿠폰·배송비·세금·부분 환불·정산 시점을 반영한 회계상 순매출이 아니다. 샘플 데이터만으로 마케팅 실패, 고객 이탈, 계절성 같은 원인을 확정할 수 없다.

### Evidence

![STEP 1 질문 구체화 결과](images/step01_question.svg)

---

## 2. 질문과 필요한 데이터 연결

### 필요한 데이터 파일

- [x] `customers.csv` — 역할과 키는 검토했지만 선택 질문의 계산에는 사용하지 않음
- [x] `products.csv`
- [x] `orders.csv`
- [x] `order_items.csv`

### 필요한 컬럼 후보

| 파일 | 필요한 컬럼 | 필요한 이유 |
| --- | --- | --- |
| `orders.csv` | `order_id`, `order_date`, `order_status` | 주문 상세 연결, 기간 필터, completed 주문 필터 |
| `order_items.csv` | `order_item_id`, `order_id`, `product_id`, `quantity`, `unit_price` | 상품금액 계산과 주문·상품 연결 |
| `products.csv` | `product_id`, `category` | 카테고리별 감소액 계산 |
| `customers.csv` | `customer_id`, `age`, `city` | 후속 고객군 분석 후보이며 현재 질문에는 미사용 |

### 데이터 연결 관계

```text
customers.customer_id 1 ── N orders.customer_id
orders.order_id       1 ── N order_items.order_id
products.product_id   1 ── N order_items.product_id
```

선택 질문은 `orders → order_items → products`를 연결한다. 한 주문에 여러 주문 상세 행이 있을 수 있으므로 주문 수는 행 수가 아니라 `order_id.nunique()`로 계산한다.

### 결과 관찰

- `customers`: 150행 × 6열
- `products`: 100행 × 4열
- `orders`: 300행 × 5열
- `order_items`: 764행 × 5열
- 네 기본 키 후보의 중복은 각각 0건이었다.
- 세 외래 키 관계의 미매칭은 각각 0건이었다.
- 선택 질문에 필요한 결합 결과 컬럼의 결측은 0건이었다.
- 주문 상태는 `completed` 184건, `cancelled` 64건, `refunded` 52건이었다.

### 나의 해석과 판단

현재 파일과 컬럼으로 선택 질문의 대리지표는 계산할 수 있다. 다만 키가 연결된다는 사실은 데이터의 모든 값이 정확하거나 업무상 매출 정의가 충족된다는 뜻은 아니다.

### 업무·분석적 의미

질문과 데이터 구조를 먼저 연결하면 존재하지 않는 컬럼을 가정하거나 주문 상세 행 수를 주문 수로 잘못 세는 집계 오류를 줄일 수 있다.

### 한계와 추가 확인 사항

Chapter 03에서는 자료형, 결측, 중복, 날짜 범위, 값 분포를 더 체계적으로 확인해야 한다. 고객군 분석을 추가할 경우 최소 집계 단위와 재식별 위험도 검토해야 한다.

### Evidence

![STEP 2 데이터 구조 확인](images/step02_data_structure.svg)

---

## 3. LLM에게 분석 질문 후보 요청

### 사용 목적

막연한 매출 감소 질문을 현재 네 데이터 파일로 검증 가능한 하위 질문으로 나누고, 누락한 분석 관점이 있는지 점검하기 위해 사용했다.

### 사용한 Prompt

```text
온라인 쇼핑몰 데이터 분석을 준비하고 있습니다.

데이터는 다음 4개 파일로 구성됩니다.
- customers: 고객 정보
- products: 상품 정보
- orders: 주문 정보
- order_items: 주문 상세 정보

목적은 completed 주문 기준 상품금액과 구매 패턴을 이해하는 것입니다.
초보 데이터 분석자가 먼저 확인할 분석 질문 5개를 제안해 주세요.
각 질문마다 필요한 데이터 파일과 확인할 컬럼 후보도 적어 주세요.
원인을 단정하지 말고, 현재 데이터로 확인 가능한 질문만 제안해 주세요.
실제 고객 행이나 개인정보는 제공되지 않았습니다.
```

### LLM 답변 요약

1. 월별 `completed` 주문 상품금액은 어떻게 변하는가? — `orders`, `order_items`; `order_date`, `order_status`, `quantity`, `unit_price`.
2. 월별 완료 주문 수와 주문당 평균금액 중 어느 지표가 금액 변화를 설명하는가? — `orders`, `order_items`; `order_id`와 금액 계산 컬럼.
3. 카테고리별 `completed` 주문 상품금액의 차이와 월별 기여는 어떠한가? — `orders`, `order_items`, `products`; `product_id`, `category` 추가.
4. 연령대·도시별 완료 주문 상품금액 분포는 어떠한가? — 네 파일; `customer_id`, `age`, `city` 추가.
5. 월별 `cancelled`·`refunded` 주문 비중은 어떻게 변하는가? — `orders`; `order_date`, `order_status`, `order_id`.

### 결과 관찰

LLM은 시간, 주문 구성, 카테고리, 고객군, 주문 상태라는 다섯 관점을 제안했다. 제안은 분석 방향을 넓혀 주었지만 기간 경계, 상품금액 정의, 불완전한 월 처리와 주문 상세의 집계 단위는 정하지 않았다.

### 나의 해석과 판단

1~3번을 결합하면 원래 질문을 관찰 가능한 요소로 나눌 수 있어 채택 가치가 높다고 판단했다. 4번은 실제 컬럼이 있지만 개인 단위 결과를 공개하지 않고 집계 수준을 정해야 한다. 5번은 금액 감소와 별개의 상태 비중 질문이므로 후속 분석으로 보류했다.

### 업무·분석적 의미

LLM은 분석 초기에 가능한 관점을 빠르게 펼치는 데 유용하다. 사람은 그중 현재 데이터와 의사결정 목적에 맞는 질문을 선택하고 우선순위를 정해야 한다.

### 한계와 추가 확인 사항

각 제안의 실제 컬럼 존재, 날짜 범위, 키 관계, 결측, 집계식과 업무상 금액 정의를 데이터로 검증해야 한다. 제안만으로 감소 원인을 말할 수 없다.

### Evidence

![STEP 3 LLM Prompt와 응답](images/step03_llm_response.svg)

---

## 4. LLM 제안 검증

| 검증 항목 | 확인 내용 |
| --- | --- |
| 선택한 LLM 제안 | 월별 상품금액을 주문 수·주문당 평균금액으로 나누고 카테고리별 기여 확인 |
| 필요한 파일 | `orders.csv`, `order_items.csv`, `products.csv` 모두 존재 |
| 필요한 컬럼 | `order_id`, `order_date`, `order_status`, `product_id`, `category`, `quantity`, `unit_price` 모두 존재 |
| 계산 범위 | 2026-01-01~2026-06-30, `completed` 주문, `quantity × unit_price` 합계 |
| 실제 데이터 확인 필요 여부 | 확인 완료: 날짜 범위, 상태값, 키 중복·미매칭, 필수 컬럼 결측 확인 |
| 원인 단정 여부 | 하지 않음. 관찰 가능한 구성 지표와 다음 검증 항목만 제시 |
| 최종 판단 | **수정 후 사용** |

### 검증에 사용한 코드

```python
from pathlib import Path
import pandas as pd

data_dir = Path('../llm-data-analysis-course/data/raw')
orders = pd.read_csv(data_dir / 'orders.csv', parse_dates=['order_date'])
items = pd.read_csv(data_dir / 'order_items.csv')
products = pd.read_csv(data_dir / 'products.csv')

analysis = (
    items
    .merge(
        orders[['order_id', 'order_date', 'order_status']],
        on='order_id',
        validate='many_to_one',
    )
    .merge(
        products[['product_id', 'category']],
        on='product_id',
        validate='many_to_one',
    )
)
analysis['line_amount'] = analysis['quantity'] * analysis['unit_price']

completed = analysis[
    analysis['order_status'].eq('completed')
    & analysis['order_date'].between('2026-01-01', '2026-06-30')
].copy()
completed['month'] = completed['order_date'].dt.to_period('M').astype(str)

monthly = completed.groupby('month').agg(
    completed_amount=('line_amount', 'sum'),
    completed_orders=('order_id', 'nunique'),
)
monthly['avg_order_amount'] = (
    monthly['completed_amount'] / monthly['completed_orders']
)
```

### 내가 수정한 내용

```text
1. “매출”을 quantity × unit_price의 합인 상품금액 대리지표로 한정했다.
2. 2026년 7월은 8일까지밖에 없어 완전한 월인 1~6월만 비교했다.
3. 금액만 보지 않고 완료 주문 수와 주문당 평균금액을 함께 계산했다.
4. 5월 대비 6월 감소액을 카테고리별로 분해했다.
5. 마케팅 실패나 고객 이탈처럼 데이터에 없는 원인은 결론에서 제외했다.
```

### 실행 결과

| 월 | completed 상품금액 | 완료 주문 수 | 주문당 평균금액 |
| --- | ---: | ---: | ---: |
| 2026-01 | 17,423,000 | 22 | 791,954.55 |
| 2026-02 | 9,749,000 | 17 | 573,470.59 |
| 2026-03 | 13,429,000 | 14 | 959,214.29 |
| 2026-04 | 17,553,000 | 23 | 763,173.91 |
| 2026-05 | 8,063,000 | 11 | 733,000.00 |
| 2026-06 | 2,826,000 | 4 | 706,500.00 |

5월에서 6월로 상품금액은 5,237,000 감소했다. 카테고리별 감소액은 도서 1,313,000, 뷰티 1,082,000, 스포츠 841,000, 패션 777,000, 전자기기 563,000, 생활용품 527,000, 식품 134,000이며 합계는 전체 감소액과 일치했다.

### 결과 관찰

5월 대비 6월의 완료 주문 수는 11건에서 4건으로 감소했고 주문당 평균금액은 733,000에서 706,500으로 소폭 감소했다. 모든 카테고리 상품금액이 감소했으며 도서와 뷰티의 감소액이 상대적으로 컸다.

### 나의 해석과 판단

이 샘플에서는 5→6월 상품금액 감소가 주문당 평균금액의 큰 하락보다 완료 주문 수 감소와 함께 나타났다. 그러나 6월 주문이 4건뿐이므로 일반적인 추세나 원인으로 확대 해석하지 않고, 후속 데이터에서 주문 유입·전환·취소·재고 여부를 확인해야 한다.

### 업무·분석적 의미

평균 구매금액 개선만 논의하기 전에 주문 건수가 왜 적었는지 확인하는 것이 우선이다. 카테고리별 감소는 재고·노출·프로모션 데이터를 요청할 우선순위를 정하는 참고 정보로 사용할 수 있다.

### 한계와 추가 확인 사항

가상 샘플 데이터이고 월별 표본이 작다. 방문·장바구니·광고·프로모션·재고·취소 사유와 회계상 순매출 컬럼이 없으므로 인과관계와 실제 사업 성과를 판단할 수 없다.

### Evidence

![STEP 4 LLM 제안 검증](images/step04_validation.svg)

---

## 5. Prompt Log

- 사용 목적: 원래 질문을 현재 데이터로 확인 가능한 하위 질문으로 나누기
- 입력 Prompt 요약: 네 파일의 역할과 `completed` 상품금액 분석 목적을 제공하고 질문 5개, 파일·컬럼 후보, 원인 단정 금지를 요청
- LLM 답변 요약: 월별 금액, 주문 수·평균금액, 카테고리, 고객군, 주문 상태 분석 제안
- 실제 반영 여부: 1~3번을 결합해 수정 후 반영, 4~5번은 후속 분석으로 보류
- 사람이 검증한 항목: 실제 컬럼, 데이터 기간, 주문 상태, 키 관계, 결측, 계산식, 월 완전성
- 사람이 수정한 내용: 금액 정의, 2026년 1~6월 범위, 7월 제외, 주문 수 계산 단위, 원인 단정 제거
- 남은 확인 사항: 할인·배송비·세금·환불 정산, 트래픽·전환·재고·프로모션 정보

### 결과 관찰

Prompt Log를 통해 LLM이 질문 후보를 넓힌 부분과 사람이 데이터 조건을 추가하고 최종 질문을 좁힌 부분이 구분된다.

### 나의 해석과 판단

Prompt Log는 결과를 다시 검토할 때 어떤 전제가 AI 제안에서 왔고 무엇을 사람이 검증·수정했는지 추적하게 한다. 특히 질문과 계산 정의가 바뀐 이유를 남기면 같은 분석을 재현하거나 오류를 수정하기 쉽다.

### Evidence

![STEP 5 Prompt Log](images/step05_prompt_log.svg)

---

## 6. 개인정보와 Secret 보호 확인

- [x] 실제 이름·이메일·전화번호 등 고객 개인정보를 Prompt에 사용하지 않았습니다.
- [x] API Key를 코드나 Notebook에 직접 작성하지 않았습니다.
- [x] `.env` 실제 내용을 캡처하거나 업로드하지 않았습니다.
- [x] GitHub Token, 비밀번호, 내부 URL이 Evidence에 보이지 않습니다.
- [x] 제출 전 SVG를 포함해 다시 확인했습니다.

### 나의 판단

실제 고객의 이름·연락처·주소·결제정보·내부 식별값과 API Key·Token·Password·내부 URL은 승인되지 않은 LLM이나 Public GitHub에 올리면 안 된다. 유출되면 개인정보 침해나 계정·서비스의 무단 사용으로 이어질 수 있다. 이 답안에는 공개 샘플의 스키마, 행 수, 집계값만 사용했고 고객 개별 행은 제시하지 않았다.

---

## 7. Chapter 01 Notebook 확인

Notebook:

```text
notebooks/ch01_ai_data_analysis_intro.ipynb
```

### 내 환경 상태

- [ ] 아직 환경설정 전이라 Notebook 위치만 확인했습니다.
- [x] 환경설정이 완료되어 Notebook을 직접 실행했습니다.

### 실행한 코드

```python
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

DATA_DIR = Path('../data/raw')
sns.set_theme(style='whitegrid')

customers = pd.read_csv(DATA_DIR / 'customers.csv')
customers.head()
```

### 실행 결과

```text
Python: 3.12.3
Python 실행 파일: llm-data-analysis-course/.venv/bin/python
Notebook code cells: 2
Execution counts: [1, 2]
Notebook cell errors: 0
customers.shape: (150, 6)
customers.columns: customer_id, name, gender, age, city, signup_date
상태: PASS
```

### 결과 관찰

공식 `.venv` 커널에서 import 셀과 기존 코드 셀 두 개가 순서대로 실행됐고 Notebook 셀 오류는 없었다. `DATA_DIR`는 Notebook 폴더를 기준으로 상위 `data/raw`를 가리키며 `customers.csv` 150행 × 6열을 읽을 수 있었다.

### 나의 해석과 판단

현재 Notebook은 분석 결론을 제공하는 완성본이 아니라 라이브러리와 상대경로를 준비한 starter scaffold다. import 성공은 환경의 기본 연결을 보여 주지만 데이터 품질이나 분석 질문의 타당성을 증명하지는 않는다.

### 한계와 추가 확인 사항

메모리 자동 실행에서는 셀 오류가 0건이었지만 종료 과정에서 ipykernel heartbeat 포트 경고가 한 번 발생했다. 결과를 숨기지 않고 기록하며, Chapter 02에서 VS Code가 같은 `.venv` 커널을 가리키는지 사용자 화면에서 재확인한다. 공식 Notebook에 셀 ID가 없는 형식 경고도 있어 향후 nbformat 호환성을 확인할 필요가 있다.

### Evidence

![STEP 7 Notebook 실행 결과](images/step07_notebook_result.svg)

---

## 8. Chapter 01 최종 해석

### 이번 장에서 가장 중요하다고 생각한 내용

분석은 코드를 먼저 만드는 일이 아니라 질문의 대상·기간·기준·비교·목적을 정의하는 일에서 시작한다. LLM은 질문과 코드의 초안을 빠르게 제안하지만 실제 데이터의 컬럼, 범위, 계산식과 업무 정의를 보장하지 않는다. 따라서 출력과 관찰을 먼저 확인하고, 해석·가설·최종 판단은 구분해서 기록해야 한다. 분석 결과가 재현 가능하도록 Prompt와 수정 이유, 한계도 함께 남겨야 한다.

### LLM을 데이터 분석에 사용할 때 가장 조심해야 할 점

자연스럽고 자신 있게 작성된 답변을 검증된 사실로 착각하지 않는 것이 가장 중요하다. 실행되는 코드라도 잘못된 기간, 집계 단위, 데이터 누수 또는 존재하지 않는 업무 전제를 사용할 수 있으므로 실제 데이터와 수작업 검증 기준을 통과한 결과만 채택해야 한다.

### 사람과 LLM의 역할 차이

| 항목 | LLM이 도울 수 있는 부분 | 사람이 책임져야 하는 부분 |
| --- | --- | --- |
| 질문 정의 | 질문 후보와 세분화 관점 제안 | 목적·기간·범위·우선순위 확정 |
| 데이터 확인 | 확인할 컬럼·품질 항목 제안 | 실제 스키마·타입·키·보안 검증 |
| 코드 작성 | pandas 코드와 검증 코드 초안 | 계산식·필터·집계 단위·실행 안전성 확인 |
| 결과 해석 | 관찰을 설명하는 문장 초안 | 실제 수치 대조, 과장·인과 단정 제거 |
| 최종 판단 | 대안과 추가 질문 제시 | 채택·수정·보류 결정과 결과 책임 |

### 다음 Chapter에서 확인하고 싶은 것

VS Code 터미널과 Notebook의 `sys.executable`이 모두 공식 `.venv`를 가리키는지 확인하고, 새 터미널에서도 같은 환경을 재현하고 싶다. Chapter 03에서는 네 CSV의 자료형·결측·중복·키 관계와 날짜 범위를 Notebook Evidence로 체계적으로 검증하고 싶다.

---

## 9. 최종 제출 체크리스트

- [x] 원래 업무 질문과 구체화한 분석 질문을 작성했습니다.
- [x] 질문에 필요한 데이터 파일과 컬럼 후보를 정리했습니다.
- [x] LLM Prompt와 답변 요약을 작성했습니다.
- [x] LLM 제안을 실제 데이터 관점에서 검증했습니다.
- [x] 각 핵심 STEP의 결과 관찰을 작성했습니다.
- [x] 각 핵심 STEP의 나의 해석과 판단을 작성했습니다.
- [x] 업무·분석적 의미를 작성했습니다.
- [x] 한계와 추가 확인 사항을 작성했습니다.
- [x] 핵심 실행 Evidence 이미지를 첨부했습니다.
- [x] 이미지 경로와 SVG 형식을 검증했습니다.
- [x] 개인정보가 없습니다.
- [x] API Key·Secret·Token이 없습니다.
- [x] 개인 GitHub 저장소에 업로드했습니다.
- [x] GitHub에서 Markdown과 이미지가 정상 표시됩니다.
- [x] 아래 최종 파일 URL이 정상적으로 열립니다.

### 최종 파일 URL

```text
https://github.com/chocoemong1/llm-data-analysis-study/blob/main/chapter01/chapter01.md
```

---

## 10. 교수자 확인용 요약

### 수행 상태

- [x] COMPLETE
- [ ] PARTIAL

### 내가 가장 중요하게 내린 판단 1개

```text
LLM의 월별 금액 질문을 그대로 사용하지 않고, 상품금액 대리지표와 완전한 월 범위를 정의한 뒤
주문 수·주문당 평균금액·카테고리 기여를 함께 확인하는 질문으로 수정 후 사용했다.
```

### 아직 확인이 필요한 내용 1개

```text
현재 상품금액 감소가 실제 사업 원인과 연결되는지 판단하려면 할인·배송비·세금·부분 환불,
트래픽·전환·재고·프로모션 데이터와 더 긴 기간의 관측값이 필요하다.
```
