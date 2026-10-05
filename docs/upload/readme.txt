# LH 임대주택 장기 공실 분석 (2026 데이터안심구역 경진대회)

## 폴더 구조
- `code/` 센터에서 실행할 분석 코드
  - `s00fake.py` 연습용 가짜 데이터 생성 (실제 데이터 아님)
  - `s01profile.py` [1차 방문] 데이터 요약표 + 분석 PC 환경 정보
  - `s02vacancy.py` 호별 계약 이력으로 공실 구간 계산
  - `s03aggregate.py` 반출용 집계표·그래프 (소수 칸 자동 가림)
  - `s04model.py` KCB 소득·관리비 결합 + 장기공실 위험 모델
  - `s05charts.py` [집에서] 반출한 CSV로 기획서용 그래프 12종 생성
  - `s06dashboard.py` [집에서] 반출 CSV를 묶어 `app/dashboard.html` 생성 (인터넷 없이 열림)
- `app/` 웹 대시보드 '빈집 레이더' (`template.html` 원본, `dashboard.html` 생성물)
  - `config.py` 경로·컬럼명·가림 기준 설정, `common.py` 공통 함수
  - `runall.py` 전체 실행
- `docs/LH공실_분석설계서.pdf` 문제 정의, 가설, 분석 설계, 일정, 역할, 신청서 문구, 기획서 목차

## 집에서 연습 (가짜 데이터)
```
cd code
pip install pandas numpy matplotlib scikit-learn
python runall.py --fake
```
결과는 `output/export/`(반출용 CSV), `output/work/`(호 단위, 반출 금지), `output/charts/`(그래프)에 생긴다.

## 센터에서 실행
1. 코드 파일을 센터 반입 절차에 따라 반입한다.
2. 데이터 폴더 경로를 지정한다: `set LH_DATA_DIR=D:\data` (Windows) 또는 `config.py`의 `DATA_DIR` 수정
3. 1차 방문: `python s01profile.py` → `output/export/01_*` 반출 신청
4. 2차 이후: `python s02vacancy.py` → `s03aggregate.py` → `s04model.py`
5. **`output/export/`의 CSV만 반출 신청한다. `output/work/` 는 호 단위 자료라 반출하지 않는다.**
6. 집에서: 반출받은 CSV를 `output/export/`에 넣고 `python s05charts.py` → `output/charts/`에 그래프 생성

## 주의
- 반출은 CSV만 가능한 것으로 보고 센터 코드는 그래프를 만들지 않는다.
- 실제 파일 컬럼명이 정의서와 다르면 `config.py`의 컬럼 매핑을 고친다.
- 반출 가림 기준(`MIN_CELL`, 기본 10)은 센터 기준에 맞춘다.
- 센터에 sklearn이 없으면 04단계는 건너뛰고 01~03만으로 기획서를 쓸 수 있다.

## 단지 단위 분석 (02b, 07)
1. `s02bcomplex.py`: 법정동+준공년월+공급유형+주택유형이 같은 호를 하나의 **추정단지**로 묶어 단지별 공실률·장기공실 비율 산출 → `export/02b_추정단지별_공실.csv` (반출 대상)
2. `s07match.py [공공단지정보.csv]`: 반출한 추정단지를 공공 LH 단지정보(단지명·법정동·준공·세대수·좌표)와 점수 매칭 → `export/07_단지매칭.csv` (확실/불확실/후보없음)
3. 연습데이터는 같은 규칙으로 만들어 매칭이 100% 나오지만, 실제 데이터는 '불확실'이 생길 수 있으니 상위 단지는 직접 확인
