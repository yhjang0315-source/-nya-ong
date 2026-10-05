"""연습용 가짜 데이터 생성 (실제 데이터 아님).

데이터정의서의 컬럼 구조를 그대로 따른 임의 데이터로, 센터 방문 전에 코드가
끝까지 돌아가는지 확인하는 용도다. 결과 수치에는 의미가 없다.
"""
import os
import numpy as np
import pandas as pd
import config

rng = np.random.default_rng(42)
os.makedirs(config.DATA_DIR, exist_ok=True)

SGG = [("서울특별시", "강서구", "11500"), ("서울특별시", "노원구", "11350"), ("서울특별시", "강남구", "11680"),
       ("경기도", "화성시", "41590"), ("경기도", "파주시", "41480"), ("경기도", "평택시", "41220"),
       ("충청남도", "아산시", "44200"), ("전라북도", "익산시", "52140"), ("경상북도", "구미시", "47190"),
       ("강원특별자치도", "원주시", "51130"), ("전라남도", "순천시", "46150"), ("경상남도", "김해시", "48250")]
SUPPLY = ["국민임대", "행복주택", "영구임대", "공공임대(5년)", "공공임대(10년)"]
BLDG = ["아파트", "아파트", "아파트", "연립주택", "다세대주택"]
HEAT = ["개별난방", "중앙난방", "지역난방"]


def ym(idx):
    idx = int(idx)
    return "%04d%02d" % (idx // 12, idx % 12 + 1)


rows, units = [], []
end_idx = 2026 * 12 + 6
# 단지 만들기: 단지마다 법정동·준공·공급유형·주택유형·난방이 같다
complexes = []
for c in range(220):
    sido, sgg, code = SGG[rng.integers(len(SGG))]
    complexes.append({"id": c, "sido": sido, "sgg": sgg, "dong": code + "%05d" % rng.integers(10100, 12000),
                      "sp": SUPPLY[rng.integers(len(SUPPLY))], "bldg": BLDG[rng.integers(len(BLDG))],
                      "heat": HEAT[rng.integers(len(HEAT))], "built": int(rng.integers(2000 * 12, 2024 * 12)),
                      "n": int(rng.integers(15, 60))})
u = 0
for cx in complexes:
    for k in range(cx["n"]):
        sido, sgg, sp, built = cx["sido"], cx["sgg"], cx["sp"], cx["built"]
        area = float(np.clip(rng.normal(42 if sp in ("행복주택", "영구임대") else 55, 10), 16, 84))
        rooms = 1 if area < 30 else (2 if area < 50 else 3)
        deposit = int(area * rng.uniform(40, 120) * 10000)
        rent = int(area * rng.uniform(3000, 9000))
        ho = "H%07d" % u; u += 1
        base_gap = 1 + (3 if sido not in ("서울특별시", "경기도") else 0) + (4 if area < 35 else 0) + (3 if cx["id"] % 17 == 0 else 0)
        t = built + int(rng.exponential(base_gap))
        first = True
        while t < end_idx:
            term = int(rng.choice([24, 24, 24, 12, 36]))
            start, end = t, t + term - 1
            cancel = start + int(rng.integers(3, term)) if rng.random() < 0.15 else None
            rows.append({
                "CNP_NM": sido, "SGG_NM": sgg, "LGDN_CD": cx["dong"],
                "HO_ADM_NO": ho, "SPL_TP_NM": sp, "LS_BLD_DS_NM": cx["bldg"],
                "HTN_FMLA_DS_NM": cx["heat"], "CCW_DT": ym(built), "DDO_AR": round(area, 2),
                "RM_CNT": rooms, "FST_CTRT_DT": ym(start - 1), "MVIN_DT": ym(start), "LS_ST_DT": ym(start),
                "LS_ED_DT": ym(end), "CNCT_DT": ym(cancel) if cancel else "", "LS_GMY": deposit, "RFE": rent,
            })
            stop = cancel if cancel else end
            renew = rng.random() < (0.55 if cancel is None else 0.0)
            t = stop + 1 if renew else stop + 1 + int(rng.exponential(base_gap * (2 if first else 1)))
            first = False
# ③ 공개 LH 임대단지 정보(가짜): 단지명·주소코드·준공·공급유형·세대수 (실제는 공공데이터포털/마이홈포털)
pub = [{"단지명": "%s%s %d단지" % (cx["sgg"][:-1], ["행복", "푸른", "햇살", "새봄"][cx["id"] % 4], cx["id"] % 9 + 1),
        "법정동코드": cx["dong"], "준공년월": ym(cx["built"] + int(rng.integers(-1, 2))), "공급유형": cx["sp"],
        "세대수": cx["n"] + int(rng.integers(0, 5)), "위도": round(36 + rng.uniform(-1.5, 1.5), 5),
        "경도": round(127.5 + rng.uniform(-1.2, 1.2), 5)} for cx in complexes]
pd.DataFrame(pub).to_csv(os.path.join(config.DATA_DIR, "LH_임대단지정보_공공.csv"), index=False, encoding="utf-8")
pd.DataFrame(rows).to_csv(os.path.join(config.DATA_DIR, config.FILES["contract"]), index=False, encoding="utf-8")

# 관리비(2023.01~2026.07): 호별 월 관리비
fee = []
hos = pd.DataFrame(rows)[["HO_ADM_NO", "DDO_AR"]].drop_duplicates("HO_ADM_NO").sample(1500, random_state=1)
for ho, area in hos.itertuples(index=False):
    for i in range(2023 * 12, end_idx + 1):
        elec = int(rng.uniform(5000, 40000))
        fee.append({"HO_ADM_NO": ho, "STND_YM": ym(i), "TMM_ADM_XPS": int(float(area) * rng.uniform(1500, 3000)),
                    "HTN_XPS": int(rng.uniform(0, 80000)), "GAS_UFE": int(rng.uniform(0, 30000)),
                    "ELEC_CHRG": elec, "WRA_CHRG": int(rng.uniform(5000, 30000))})
pd.DataFrame(fee).to_csv(os.path.join(config.DATA_DIR, config.FILES["fee"]), index=False, encoding="utf-8")

# KCB 행정동 소득 분포(분기)
kcb = []
for _, _, code in SGG:
    for d in range(3):
        emd = code + "%05d" % (51000 + d * 10)
        for q in ["20231231"]:
            for sex in "12":
                for age in ["20", "30", "40", "50", "60"]:
                    r = {"BS_YR_QT": q, "RES_COM_CD": "1", "EMD_CD": emd, "SEX_CD": sex, "AGE_CD": age}
                    w = rng.dirichlet(np.linspace(3, 0.3, 22))
                    for k in range(22):
                        r["C%d_CNT" % (k + 1)] = int(w[k] * rng.integers(300, 3000))
                    kcb.append(r)
pd.DataFrame(kcb).to_csv(os.path.join(config.DATA_DIR, config.FILES["kcb"]), index=False, encoding="utf-8")
print("(공개 단지정보 포함) 가짜 데이터 생성 완료:", config.DATA_DIR, "계약", len(rows), "관리비", len(fee), "KCB", len(kcb))
