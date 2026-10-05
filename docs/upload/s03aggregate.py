"""[본 분석 2] 반출용 집계표와 그래프.

모두 지역·유형 단위로 집계하고, 호수가 MIN_CELL 미만인 칸은 가린다.
결과: output/export/03_*.csv (반출은 CSV만 가능 → 그래프는 s05charts.py로 집에서 생성)
"""
import pandas as pd
import common
import config

work = config.OUT_DIR + "/work"
unit = pd.read_csv(work + "/호특성.csv", dtype={"법정동코드": str})
ep = pd.read_csv(work + "/공실구간.csv", dtype={"법정동코드": str})
L6, L12, L24 = config.LONG_VACANCY


def summarize(group_cols, name):
    u = unit.groupby(group_cols, observed=True).agg(
        호수=("호관리번호", "size"),
        현재공실호수=("현재공실", "sum"),
        공실경험호비율=("공실횟수", lambda s: round(100 * (s > 0).mean(), 1)),
        평균누적공실개월=("누적공실개월", "mean"),
        초기미임대_중위개월=("초기미임대개월", "median"),
        중도해약_호당평균=("중도해약수", "mean"),
    )
    cur = unit[unit["현재공실"]].groupby(group_cols, observed=True)["현재공실개월"]
    u["현재공실_중위개월"] = cur.median()
    u["현재공실_%d개월이상" % L12] = unit[unit["현재공실개월"] >= L12].groupby(group_cols, observed=True).size()
    e = ep.groupby(group_cols, observed=True)["공실개월"]
    u["공실구간수"] = e.size()
    u["공실_중위개월"] = e.median()
    for k in (L6, L12, L24):
        u["공실_%d개월이상비율" % k] = ep.assign(f=ep["공실개월"] >= k).groupby(group_cols, observed=True)["f"].mean() * 100
    u["현재공실률(%)"] = 100 * u["현재공실호수"] / u["호수"]
    u = u.round(2).reset_index().sort_values("호수", ascending=False)
    common.save(common.mask_small(u), "03_%s.csv" % name)
    return u


ep = ep.merge(unit[["호관리번호", "면적구간", "임대료분위_시군구내"]], on="호관리번호", how="left")
unit["준공연차구간"] = pd.cut(unit["준공연차"], [0, 5, 10, 15, 20, 100], labels=["5년미만", "5~10", "10~15", "15~20", "20년이상"])
ep = ep.merge(unit[["호관리번호", "준공연차구간"]], on="호관리번호", how="left")

summarize(["시도"], "시도별")
sgg = summarize(["시도", "시군구"], "시군구별")
summarize(["공급유형"], "공급유형별")
summarize(["면적구간"], "면적구간별")
summarize(["공급유형", "면적구간"], "공급유형x면적")
summarize(["방수"], "방수별")
summarize(["준공연차구간"], "준공연차별")
summarize(["임대료분위_시군구내"], "임대료분위별")
summarize(["주택유형"], "주택유형별")

# 연도별 공실 발생 추이
t = ep.groupby("공실시작연도").agg(호수=("호관리번호", "size"), 공실_중위개월=("공실개월", "median")).reset_index()
common.save(common.mask_small(t), "03_연도별_공실발생.csv")

print("집계표 저장 완료 (그래프는 집에서 s05charts.py 로 생성)")
