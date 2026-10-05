"""LH 임대주택 공실 분석 - 공통 설정.

센터에서는 DATA_DIR 만 실제 데이터 폴더로 바꾸면 된다.
"""
import os

# 데이터 위치: 환경변수 LH_DATA_DIR 가 있으면 그것을, 없으면 ../fake_data 를 쓴다.
DATA_DIR = os.environ.get("LH_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "fake_data"))
OUT_DIR = os.environ.get("LH_OUT_DIR", os.path.join(os.path.dirname(__file__), "..", "output"))

FILES = {
    "contract": "전국 건설임대주택 계약 기초데이터(계약).csv",
    "fee": "전국 건설임대주택 계약 기초데이터(관리비).csv",
    "kcb": "TB_KCB_INCOME_STAT_DATASET.csv",
    "skt_age": "seoul_flow_age.csv",
}

# 데이터 마지막 시점 (정의서 기준). 이 시점까지 다음 계약이 없으면 '공실 진행 중'으로 본다.
DATA_END_YM = 202607

# 반출 심의용: 이 건수 미만인 집계 칸은 가린다(센터 기준에 맞게 조정).
MIN_CELL = 10

# 장기 공실 기준(개월)
LONG_VACANCY = [6, 12, 24]

# 실제 파일 컬럼명(영문) -> 분석용 한글명. 파일이 이미 한글 컬럼이면 그대로 둔다.
CONTRACT_COLS = {
    "CNP_NM": "시도", "SGG_NM": "시군구", "LGDN_CD": "법정동코드", "HO_ADM_NO": "호관리번호",
    "SPL_TP_NM": "공급유형", "LS_BLD_DS_NM": "주택유형", "HTN_FMLA_DS_NM": "난방방식",
    "CCW_DT": "준공년월", "DDO_AR": "전용면적", "RM_CNT": "방수", "FST_CTRT_DT": "최초계약년월",
    "MVIN_DT": "입주년월", "LS_ST_DT": "임대시작년월", "LS_ED_DT": "임대종료년월",
    "CNCT_DT": "해약년월", "LS_GMY": "임대보증금", "RFE": "임대료",
}
FEE_COLS = {
    "HO_ADM_NO": "호관리번호", "STND_YM": "기준년월", "TMM_ADM_XPS": "당월관리비",
    "HTN_XPS": "난방비", "GAS_UFE": "가스사용료", "ELEC_CHRG": "전기요금", "WRA_CHRG": "수도료",
}
KCB_COLS = {"BS_YR_QT": "기준시점", "RES_COM_CD": "거주기준", "EMD_CD": "행정동코드",
            "SEX_CD": "성", "AGE_CD": "연령"}

# 면적 구간(㎡)
AREA_BINS = [0, 30, 40, 50, 60, 85, 1000]
AREA_LABELS = ["30미만", "30~40", "40~50", "50~60", "60~85", "85이상"]
