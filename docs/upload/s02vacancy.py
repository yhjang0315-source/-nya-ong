"""[본 분석 1] 호별 계약 이력으로 공실 구간 만들기.

공실 정의
- 같은 호에서 한 계약이 끝난 뒤(해약년월이 있으면 해약년월, 없으면 임대종료년월)
  다음 계약 임대시작년월까지의 빈 기간(개월).
- 다음 계약이 없고 끝난 시점이 데이터 마지막 시점(2026.07) 이전이면 '공실 진행 중'(관측 중단).
- 준공 후 첫 임대시작까지 = '초기 미임대 기간'.
결과(센터 안에서만 사용, 반출 금지): output/work/공실구간.parquet|csv, 호특성.csv
"""
import numpy as np
import pandas as pd
import common
import config

con = common.rename(common.read_csv("contract"), config.CONTRACT_COLS)
for c in ["준공년월", "임대시작년월", "임대종료년월", "해약년월", "최초계약년월", "입주년월"]:
    con[c + "_i"] = common.ym_to_idx(con[c])
for c in ["전용면적", "방수", "임대보증금", "임대료"]:
    con[c] = pd.to_numeric(con[c], errors="coerce")
end_data = common.ym_to_idx([str(config.DATA_END_YM)])[0]

con = con.dropna(subset=["호관리번호", "임대시작년월_i"]).sort_values(["호관리번호", "임대시작년월_i"])
con["종료_i"] = con["해약년월_i"].fillna(con["임대종료년월_i"])
con["중도해약"] = con["해약년월_i"].notna() & (con["해약년월_i"] < con["임대종료년월_i"])
con["다음시작_i"] = con.groupby("호관리번호")["임대시작년월_i"].shift(-1)

# 공실 구간: 계약 종료 다음 달부터 다음 계약 시작 전 달까지
gap = con["다음시작_i"] - con["종료_i"] - 1
ongoing = con["다음시작_i"].isna() & (con["종료_i"] < end_data)
ep = con.loc[(gap > 0) | ongoing].copy()
ep["공실개월"] = np.where(ep["다음시작_i"].notna(), ep["다음시작_i"] - ep["종료_i"] - 1, end_data - ep["종료_i"])
ep["진행중"] = ep["다음시작_i"].isna()
ep["공실시작연도"] = ((ep["종료_i"] + 1) // 12).astype(int)
ep["직전계약_중도해약"] = ep["중도해약"]
keep = ["호관리번호", "시도", "시군구", "법정동코드", "공급유형", "주택유형", "난방방식", "전용면적", "방수",
        "준공년월_i", "임대보증금", "임대료", "공실시작연도", "공실개월", "진행중", "직전계약_중도해약"]
ep = ep[keep]

# 호 특성(가장 최근 계약 기준) + 공실 경험 요약
last = con.groupby("호관리번호").tail(1).set_index("호관리번호")
unit = last[["시도", "시군구", "법정동코드", "공급유형", "주택유형", "난방방식", "전용면적", "방수",
             "준공년월_i", "임대보증금", "임대료"]].copy()
first_start = con.groupby("호관리번호")["임대시작년월_i"].min()
unit["초기미임대개월"] = (first_start - unit["준공년월_i"]).clip(lower=0)
unit["계약수"] = con.groupby("호관리번호").size()
unit["중도해약수"] = con.groupby("호관리번호")["중도해약"].sum()
g = ep.groupby("호관리번호")["공실개월"]
unit["공실횟수"] = g.size()
unit["누적공실개월"] = g.sum()
unit["최장공실개월"] = g.max()
unit = unit.fillna({"공실횟수": 0, "누적공실개월": 0, "최장공실개월": 0})
unit["현재공실"] = ep.groupby("호관리번호")["진행중"].any().reindex(unit.index).fillna(False)
unit["현재공실개월"] = ep[ep["진행중"]].set_index("호관리번호")["공실개월"].reindex(unit.index)
unit["준공연차"] = ((end_data - unit["준공년월_i"]) / 12).round(1)
unit["면적구간"] = pd.cut(unit["전용면적"], config.AREA_BINS, labels=config.AREA_LABELS, right=False)
# 지역 내 임대료 상대수준(시군구 내 ㎡당 임대료 분위)
unit["㎡당임대료"] = unit["임대료"] / unit["전용면적"]
unit["임대료분위_시군구내"] = unit.groupby("시군구")["㎡당임대료"].transform(
    lambda s: pd.qcut(s.rank(method="first"), 4, labels=["하", "중하", "중상", "상"]) if len(s) >= 4 else np.nan)

work = common.ensure_out("work")
ep.to_csv(work + "/공실구간.csv", index=False, encoding="utf-8-sig")
unit.reset_index().to_csv(work + "/호특성.csv", index=False, encoding="utf-8-sig")
print("공실 구간:", len(ep), "/ 호:", len(unit), "/ 현재 공실 호:", int(unit["현재공실"].sum()))
print("※ output/work 는 호 단위 자료라 반출하지 말 것")
