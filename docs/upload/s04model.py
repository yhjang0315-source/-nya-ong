"""[본 분석 3] 지역 소득(KCB)·관리비 결합 + 장기공실 위험 모델.

- KCB 행정동 소득분포 -> 시군구(코드 앞 5자리) 단위로 합쳐 '저소득 비율', '20·30대 비율' 계산
- 관리비(2023.01~) -> 호별 ㎡당 평균 관리비
- 목표: 현재 12개월 이상 공실이거나 과거 12개월 이상 공실 경험이 있는 호(장기공실 호)
- 모델: 로지스틱 회귀 + 그래디언트 부스팅. 반출은 성능·변수중요도(집계)만.
"""
import numpy as np
import pandas as pd
import common
import config

work = config.OUT_DIR + "/work"
unit = pd.read_csv(work + "/호특성.csv", dtype={"법정동코드": str})
unit["시군구코드"] = unit["법정동코드"].str[:5]

# KCB: 시군구 단위 소득 지표
try:
    kcb = common.rename(common.read_csv("kcb"), config.KCB_COLS)
    cnt = [c for c in kcb.columns if c.startswith("C") and c.endswith("_CNT")]
    kcb[cnt] = kcb[cnt].apply(pd.to_numeric, errors="coerce").fillna(0)
    kcb = kcb[kcb["기준시점"] == kcb["기준시점"].max()]
    kcb["시군구코드"] = kcb["행정동코드"].str[:5]
    kcb["전체"] = kcb[cnt].sum(axis=1)
    kcb["저소득"] = kcb[["C1_CNT", "C2_CNT"]].sum(axis=1)  # 월 150만원 이하
    kcb["청년"] = np.where(kcb["연령"].isin(["20", "30"]), kcb["전체"], 0)
    reg = kcb.groupby("시군구코드")[["전체", "저소득", "청년"]].sum()
    reg["저소득비율"] = reg["저소득"] / reg["전체"]
    reg["2030비율"] = reg["청년"] / reg["전체"]
    unit = unit.merge(reg[["저소득비율", "2030비율"]], left_on="시군구코드", right_index=True, how="left")
    common.save(reg.reset_index()[["시군구코드", "저소득비율", "2030비율"]].round(4), "04_시군구_소득지표.csv")
except FileNotFoundError:
    print("KCB 없음 - 건너뜀")

# 관리비: 호별 ㎡당 월평균 관리비 (큰 파일이라 나눠 읽기)
try:
    parts = []
    for ch in common.read_csv("fee", chunksize=500000):
        ch = common.rename(ch, config.FEE_COLS)
        ch["당월관리비"] = pd.to_numeric(ch["당월관리비"], errors="coerce")
        parts.append(ch.groupby("호관리번호")["당월관리비"].agg(["sum", "count"]))
    fee = pd.concat(parts).groupby(level=0).sum()
    unit = unit.merge((fee["sum"] / fee["count"]).rename("월평균관리비"), left_on="호관리번호", right_index=True, how="left")
    unit["㎡당관리비"] = unit["월평균관리비"] / unit["전용면적"]
except FileNotFoundError:
    print("관리비 없음 - 건너뜀")

unit["장기공실호"] = ((unit["최장공실개월"] >= 12) | (unit["현재공실개월"] >= 12)).astype(int)
num = [c for c in ["전용면적", "방수", "준공연차", "임대보증금", "임대료", "㎡당임대료", "초기미임대개월",
                   "중도해약수", "저소득비율", "2030비율", "㎡당관리비"] if c in unit.columns]
cat = ["시도", "공급유형", "주택유형", "난방방식"]
X = pd.get_dummies(unit[num + cat], columns=cat, dummy_na=True).astype(float)
X = X.fillna(X.median())
y = unit["장기공실호"]
print("장기공실 호 비율: %.1f%%" % (100 * y.mean()))

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.inspection import permutation_importance

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
res = []
lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(Xtr, ytr)
res.append({"모델": "로지스틱회귀", "AUC": roc_auc_score(yte, lr.predict_proba(Xte)[:, 1])})
gb = GradientBoostingClassifier(random_state=0).fit(Xtr, ytr)
res.append({"모델": "그래디언트부스팅", "AUC": roc_auc_score(yte, gb.predict_proba(Xte)[:, 1])})
common.save(pd.DataFrame(res).round(3), "04_모델성능.csv")

pi = permutation_importance(gb, Xte, yte, n_repeats=5, random_state=0, scoring="roc_auc")
imp = pd.DataFrame({"변수": X.columns, "중요도": pi.importances_mean}).sort_values("중요도", ascending=False)
common.save(imp.round(4), "04_변수중요도.csv")
coef = pd.DataFrame({"변수": X.columns, "계수(표준화)": lr[-1].coef_[0]}).sort_values("계수(표준화)")
common.save(coef.round(4), "04_로지스틱_계수.csv")

# 시군구별 예측 위험(평균) - 집계만 반출
unit["예측위험"] = gb.predict_proba(X)[:, 1]
r = unit.groupby(["시도", "시군구"]).agg(호수=("호관리번호", "size"), 평균예측위험=("예측위험", "mean"),
                                       실제장기공실비율=("장기공실호", "mean")).reset_index()
common.save(common.mask_small(r.round(3)), "04_시군구_예측위험.csv")

print(pd.DataFrame(res))
