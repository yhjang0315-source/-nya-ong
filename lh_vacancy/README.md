# LH 임대주택 장기 공실 분석 (2026 데이터안심구역 경진대회)

## 폴더 구조
- `code/` 센터에서 실행할 분석 코드
  - `00_make_fake_data.py` 연습용 가짜 데이터 생성 (실제 데이터 아님)
  - `01_profile.py` [1차 방문] 데이터 요약표 + 분석 PC 환경 정보
  - `02_build_vacancy.py` 호별 계약 이력으로 공실 구간 계산
  - `03_aggregate_export.py` 반출용 집계표·그래프 (소수 칸 자동 가림)
  - `04_context_model.py` KCB 소득·관리비 결합 + 장기공실 위험 모델
  - `config.py` 경로·컬럼명·가림 기준 설정, `common.py` 공통 함수
  - `run_all.py` 전체 실행
- `docs/LH공실_분석설계서.pdf` 문제 정의, 가설, 분석 설계, 일정, 역할, 신청서 문구, 기획서 목차

## 집에서 연습 (가짜 데이터)
```
cd code
pip install pandas numpy matplotlib scikit-learn
python run_all.py --fake
```
결과는 `output/export/`(반출용)와 `output/work/`(호 단위, 반출 금지)에 생긴다.

## 센터에서 실행
1. 코드 파일을 센터 반입 절차에 따라 반입한다.
2. 데이터 폴더 경로를 지정한다: `set LH_DATA_DIR=D:\data` (Windows) 또는 `config.py`의 `DATA_DIR` 수정
3. 1차 방문: `python 01_profile.py` → `output/export/01_*` 반출 신청
4. 2차 이후: `python 02_build_vacancy.py` → `03_aggregate_export.py` → `04_context_model.py`
5. **`output/export/` 만 반출 신청한다. `output/work/` 는 호 단위 자료라 반출하지 않는다.**

## 주의
- 실제 파일 컬럼명이 정의서와 다르면 `config.py`의 컬럼 매핑을 고친다.
- 반출 가림 기준(`MIN_CELL`, 기본 10)은 센터 기준에 맞춘다.
- 센터에 sklearn이 없으면 04단계는 건너뛰고 01~03만으로 기획서를 쓸 수 있다.
