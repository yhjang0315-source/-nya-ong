"""[본 분석 2] 반출용 집계표와 그래프.

모두 지역·유형 단위로 집계하고, 호수가 MIN_CELL 미만인 칸은 가린다.
결과: output/export/03_*.csv, output/export/fig_*.png
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

# 그래프
plt = common.setup_korean_font()
out = common.ensure_out("export")
for col, fname in [("면적구간", "면적"), ("공급유형", "공급유형"), ("준공연차구간", "준공연차")]:
    d = unit.groupby(col, observed=True).agg(n=("호관리번호", "size"), r=("현재공실", "mean"))
    d = d[d["n"] >= config.MIN_CELL]
    ax = (d["r"] * 100).plot(kind="bar", figsize=(7, 4), color="#4b3a9a")
    ax.set_ylabel("현재 공실률(%)"); ax.set_xlabel(col); ax.set_title("%s별 현재 공실률" % col)
    plt.tight_layout(); plt.savefig(out + "/fig_%s별_공실률.png" % fname, dpi=150); plt.close()
top = sgg[sgg["호수"] >= config.MIN_CELL].nlargest(15, "현재공실률(%)")
ax = top.set_index("시군구")["현재공실률(%)"].plot(kind="barh", figsize=(7, 5), color="#e8612c")
ax.invert_yaxis(); ax.set_xlabel("현재 공실률(%)"); ax.set_title("현재 공실률 상위 시군구")
plt.tight_layout(); plt.savefig(out + "/fig_시군구_공실률_상위.png", dpi=150); plt.close()
ax = t[t["호수"] >= config.MIN_CELL].set_index("공실시작연도")["공실_중위개월"].plot(figsize=(7, 4), marker="o")
ax.set_ylabel("공실 기간 중위값(개월)"); ax.set_title("연도별 공실 기간 추이")
plt.tight_layout(); plt.savefig(out + "/fig_연도별_공실기간.png", dpi=150); plt.close()
print("그래프 저장 완료")
