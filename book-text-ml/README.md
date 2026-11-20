# 11강 교보문고 베스트셀러 텍스트 실습

공개 실습 가이드의 Chapter 01과 Chapter 02를 순서대로 실행한 결과이다.

- 과정 소개: <https://blog.naver.com/dev-dog/224415732221>
- Chapter 01: <https://blog.naver.com/dev-dog/224415736311>
- Chapter 02: <https://blog.naver.com/dev-dog/224415740859>

## 파일

- `교보문고_온라인_베스트셀러_상품리스트.xlsx`: 2026-11-20에 교보문고 온라인 베스트셀러에서 내려받은 원본 스냅샷
- `book_text_ml_ch01.ipynb`: 구조·결측·자료형·중복 점검과 기본 전처리
- `book_bestseller_clean.csv`: Chapter 01 전처리 결과
- `chapter02.ipynb`: Kiwi 품사 분석, 단어 빈도, 원제목 대조, Word Cloud
- `chapter02_top30_words.csv`: 최종 상위 30개 단어
- `chapter02_wordcloud.png`: 최종 Word Cloud

## 재현 순서

1. `book_text_ml_ch01.ipynb`를 처음부터 실행한다.
2. `chapter02.ipynb`를 처음부터 실행한다.
3. 두 Notebook의 마지막 검증표가 모두 `PASS`인지 확인한다.

실행 환경은 서버 공용 Python `/home/gem/research/프로그램 모음/venvs/llm-data-analysis` 을 사용한다.
