"""[집에서 실행] 반출한 추정단지 집계 ↔ 공개 LH 임대단지 정보(③) 매칭 → 단지명·좌표 붙이기.

매칭 규칙(점수제)
- 법정동코드 일치 (필수)
- 공급유형 일치 +2
- 준공년월 차이 0개월 +3, 1~2개월 +2, 3~6개월 +1
- 세대수 비율(추정 호수/공개 세대수)이 0.7~1.1이면 +1
가장 점수가 높은 후보를 붙이고, 점수가 4 미만이면 '불확실'로 표시한다.
사용: python s07match.py [공개단지정보.csv]
결과: output/export/07_단지매칭.csv (대시보드 단지 탭에서 사용)
"""
import os
import sys
import pandas as pd
import config
import common

EXP = os.path.join(config.OUT_DIR, "export")
_args = [a for a in sys.argv[1:] if not a.startswith("--")]
pub_path = _args[0] if _args else os.path.join(config.DATA_DIR, "LH_임대단지정보_공공.csv")
cx = pd.read_csv(os.path.join(EXP, "02b_추정단지별_공실.csv"), dtype={"법정동코드": str, "준공년월": str}, encoding="utf-8-sig")
pub = pd.read_csv(pub_path, dtype={"법정동코드": str, "준공년월": str})


def ym_idx(s):
    s = str(s)[:6]
    return int(s[:4]) * 12 + int(s[4:6]) - 1 if s.isdigit() and len(s) == 6 else None


out = []
for _, r in cx.iterrows():
    cand = pub[pub["법정동코드"] == r["법정동코드"]]
    best, best_score = None, -1
    for _, p in cand.iterrows():
        sc = 0
        if p["공급유형"] == r["공급유형"]:
            sc += 2
        a, b = ym_idx(r["준공년월"]), ym_idx(p["준공년월"])
        if a is not None and b is not None:
            d = abs(a - b)
            sc += 3 if d == 0 else 2 if d <= 2 else 1 if d <= 6 else 0
        n = pd.to_numeric(r["호수"], errors="coerce")
        if pd.notna(n) and p["세대수"]:
            ratio = n / p["세대수"]
            sc += 1 if 0.7 <= ratio <= 1.1 else 0
        if sc > best_score:
            best, best_score = p, sc
    row = r.to_dict()
    row["매칭단지명"] = best["단지명"] if best is not None else ""
    row["매칭점수"] = best_score if best is not None else 0
    row["매칭상태"] = "확실" if best_score >= 4 else ("불확실" if best is not None else "후보없음")
    row["위도"] = best["위도"] if best is not None and "위도" in best else None
    row["경도"] = best["경도"] if best is not None and "경도" in best else None
    out.append(row)
res = pd.DataFrame(out)
common.save(res, "07_단지매칭.csv")
print(res["매칭상태"].value_counts().to_string())
