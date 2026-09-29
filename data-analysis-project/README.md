# 데이터분석 프로젝트

**주제:** 온라인 쇼핑몰의 상품별 거래금액 집중도와 취소 거래의 영향 분석

**현재 상태:** 1차 기획서 작성 및 실제 데이터 확보·기초 점검 완료. LMS 제출과 발표는 별도로 진행한다.

## 단계별 결과

| 단계 | 결과물·진행 상태 |
| --- | --- |
| 1차 기획 | [01_proposal.md](01_proposal/01_proposal.md) — 제출 파일 |
| 2차 데이터·EDA | 예정: 전처리 기준, 처리 결과, 핵심 그래프 |
| 3차 분석·검증 | 예정: 세 질문 분석 및 처리 기준별 비교 |
| 4차 최종 | 예정: 피드백 반영, 결론·한계·재현 방법 |

## 데이터와 재현

- 출처: Chen, D. (2015). [Online Retail, UCI](https://archive.ics.uci.edu/dataset/352/online-retail). [DOI: 10.24432/C5BW33](https://doi.org/10.24432/C5BW33). CC BY 4.0.
- [확보·품질 확인 기록](docs/data_check.json): 원본 해시, 규모, 기간, 결측·중복 후보 및 분석 범위. 1차 단계의 원본 점검이며, 전처리는 아직 적용하지 않았다.
- [재현 스크립트](docs/check_data.py): 최초 실행 시 공식 ZIP을 내려받고 전체 Excel을 읽어 확인 기록을 생성한다. 원본은 `data/raw/`에 보관하고 Git에서 제외한다. 다운로드와 압축 해제를 합쳐 약 50 MB가 필요하다.
- Python 3.12.3, openpyxl 3.1.5로 실행했다. 의존성은 [docs/requirements.txt](docs/requirements.txt)에 기록했다.

저장소 루트에서 해당 의존성이 준비된 Python으로 실행한다.

```bash
python data-analysis-project/docs/check_data.py
```

## 변경·피드백 기록

- 2026-09-29: 1차 기획서 작성. 공식 데이터 541,909행 × 8개 컬럼 로딩과 2011년 1~11월 영국 범위 431,427행을 확인했다. 원본의 고객 ID 결측과 중복 후보는 2차 전처리 검토 항목에 반영했다.
- 교수자 피드백: 아직 수신 전.

LMS에는 [1차 기획서 파일 URL](https://github.com/chocoemong1/llm-data-analysis-study/blob/main/data-analysis-project/01_proposal/01_proposal.md)을 제출한다.
