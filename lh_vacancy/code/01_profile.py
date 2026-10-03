"""[1차 방문] 데이터 요약표 만들기 → 반출 신청용.

개인/호 단위 값은 내보내지 않고 컬럼별 통계만 만든다.
결과: output/export/01_컬럼요약_*.csv, 01_분포_*.csv, 01_환경정보.txt
"""
import platform
import sys
import pandas as pd
import common
import config


def profile(df, name):
    rows = []
    for c in df.columns:
        s = df[c]
        num = pd.to_numeric(s, errors="coerce")
        is_num = num.notna().mean() > 0.9
        rows.append({
            "컬럼": c, "행수": len(s), "결측률(%)": round(100 * (s.isna() | (s.astype(str).str.strip() == "")).mean(), 2),
            "고유값수": s.nunique(dropna=True),
            "최소": num.min() if is_num else "", "최대": num.max() if is_num else "",
            "중앙값": num.median() if is_num else "",
        })
    out = pd.DataFrame(rows)
    # 식별자 컬럼은 최소/최대값을 지운다
    out[["최소", "최대", "중앙값"]] = out[["최소", "최대", "중앙값"]].astype(object)
    out.loc[out["컬럼"].isin(["호관리번호", "법정동코드", "행정동코드"]), ["최소", "최대", "중앙값"]] = ""
    common.save(out, "01_컬럼요약_%s.csv" % name)


def dist(df, cols, name):
    for c in cols:
        if c in df.columns:
            t = df[c].fillna("(결측)").value_counts().rename_axis(c).reset_index(name="호수")
            common.save(common.mask_small(t), "01_분포_%s_%s.csv" % (name, c))


con = common.rename(common.read_csv("contract"), config.CONTRACT_COLS)
profile(con, "계약")
dist(con, ["시도", "공급유형", "주택유형", "난방방식", "방수"], "계약")
# 연도별 계약 시작 건수
y = (common.ym_to_idx(con["임대시작년월"]) // 12).value_counts().sort_index()
common.save(common.mask_small(y.rename_axis("임대시작연도").reset_index(name="호수")), "01_분포_계약_임대시작연도.csv")
print("호 수:", con["호관리번호"].nunique(), "/ 호당 평균 계약 수:", round(len(con) / con["호관리번호"].nunique(), 2))

try:
    fee = common.rename(common.read_csv("fee", chunksize=None), config.FEE_COLS)
    profile(fee, "관리비")
except FileNotFoundError:
    print("관리비 파일 없음 - 건너뜀")
try:
    kcb = common.rename(common.read_csv("kcb"), config.KCB_COLS)
    profile(kcb, "KCB")
except FileNotFoundError:
    print("KCB 파일 없음 - 건너뜀")

# 분석 PC 환경 정보
lines = ["python " + sys.version, "platform " + platform.platform()]
for m in ["pandas", "numpy", "matplotlib", "sklearn", "scipy", "statsmodels", "lifelines", "geopandas"]:
    try:
        mod = __import__(m)
        lines.append("%s %s" % (m, getattr(mod, "__version__", "?")))
    except ImportError:
        lines.append("%s (없음)" % m)
path = common.ensure_out("export") + "/01_환경정보.txt"
open(path, "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))
