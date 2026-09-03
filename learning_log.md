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
