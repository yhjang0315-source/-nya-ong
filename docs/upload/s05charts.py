"""[집에서 실행] 반출한 CSV로 기획서용 그래프 만들기.

센터 반출이 CSV만 가능하므로 그래프는 밖에서 그린다.
사용: 반출받은 CSV를 output/export/ 에 넣고 python s05charts.py
결과: output/charts/*.png
"""
import os
import pandas as pd
import common
import config

EXP = os.path.join(config.OUT_DIR, "export")
CH = common.ensure_out("charts")
plt = common.setup_korean_font()
PURPLE, ORANGE = "#4b3a9a", "#e8612c"


def load(name):
    path = os.path.join(EXP, name)
    if not os.path.exists(path):
        print("없음(건너뜀):", name)
        return None
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["호수"] = pd.to_numeric(df["호수"], errors="coerce") if "호수" in df.columns else None
    return df


def bar(df, x, y, title, fname, horizontal=False, color=PURPLE, top=None):
    d = df.dropna(subset=[y])
    if top:
        d = d.nlargest(top, y)
    fig, ax = plt.subplots(figsize=(7, 4.5 if horizontal else 4))
    if horizontal:
        ax.barh(d[x].astype(str), d[y], color=color); ax.invert_yaxis(); ax.set_xlabel(y)
    else:
        ax.bar(d[x].astype(str), d[y], color=color); ax.set_ylabel(y); plt.xticks(rotation=30, ha="right")
    ax.set_title(title)
    plt.tight_layout(); plt.savefig(os.path.join(CH, fname), dpi=200); plt.close()
    print("그래프:", fname)


sgg = load("03_시군구별.csv")
if sgg is not None:
    sgg["지역"] = sgg["시도"].str[:2] + " " + sgg["시군구"]
    bar(sgg, "지역", "현재공실률(%)", "현재 공실률 상위 시군구", "01_시군구_공실률_상위.png", True, ORANGE, top=15)
    bar(sgg, "지역", "공실_12개월이상비율", "12개월 이상 장기공실 비율 상위 시군구", "02_시군구_장기공실_상위.png", True, ORANGE, top=15)
for f, col, title, out in [
    ("03_시도별.csv", "시도", "시도별 현재 공실률", "03_시도별_공실률.png"),
    ("03_면적구간별.csv", "면적구간", "면적별 현재 공실률", "04_면적별_공실률.png"),
    ("03_공급유형별.csv", "공급유형", "공급유형별 현재 공실률", "05_공급유형별_공실률.png"),
    ("03_준공연차별.csv", "준공연차구간", "준공연차별 현재 공실률", "06_준공연차별_공실률.png"),
    ("03_임대료분위별.csv", "임대료분위_시군구내", "시군구 내 임대료 수준별 현재 공실률", "07_임대료분위별_공실률.png"),
    ("03_방수별.csv", "방수", "방 수별 현재 공실률", "08_방수별_공실률.png"),
]:
    d = load(f)
    if d is not None:
        bar(d.sort_values(col), col, "현재공실률(%)", title, out)

d = load("03_공급유형x면적.csv")
if d is not None:
    p = d.pivot_table(index="공급유형", columns="면적구간", values="현재공실률(%)")
    p = p[[c for c in config.AREA_LABELS if c in p.columns]]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    im = ax.imshow(p.values, cmap="Oranges", aspect="auto")
    ax.set_xticks(range(len(p.columns))); ax.set_xticklabels(p.columns)
    ax.set_yticks(range(len(p.index))); ax.set_yticklabels(p.index)
    for i in range(p.shape[0]):
        for j in range(p.shape[1]):
            v = p.values[i, j]
            ax.text(j, i, "" if pd.isna(v) else "%.1f" % v, ha="center", va="center", fontsize=8)
    fig.colorbar(im, label="현재 공실률(%)"); ax.set_title("공급유형 × 면적 현재 공실률")
    plt.tight_layout(); plt.savefig(os.path.join(CH, "09_공급유형x면적_히트맵.png"), dpi=200); plt.close()
    print("그래프: 09_공급유형x면적_히트맵.png")

d = load("03_연도별_공실발생.csv")
if d is not None:
    d = d.dropna(subset=["공실_중위개월"])
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(d["공실시작연도"], d["공실_중위개월"], marker="o", color=PURPLE)
    ax.set_ylabel("공실 기간 중위값(개월)"); ax.set_title("공실 시작 연도별 공실 기간 추이")
    plt.tight_layout(); plt.savefig(os.path.join(CH, "10_연도별_공실기간.png"), dpi=200); plt.close()
    print("그래프: 10_연도별_공실기간.png")

d = load("04_변수중요도.csv")
if d is not None:
    bar(d.head(15), "변수", "중요도", "장기공실 예측 변수 중요도 (상위 15)", "11_변수중요도.png", True, PURPLE)
d = load("04_시군구_예측위험.csv")
if d is not None:
    d["지역"] = d["시도"].str[:2] + " " + d["시군구"]
    bar(d, "지역", "평균예측위험", "장기공실 예측 위험 상위 시군구", "12_시군구_예측위험_상위.png", True, ORANGE, top=15)
print("완료:", CH)
