"""[집에서 실행] 반출 CSV를 묶어 대시보드 HTML 한 파일 생성.

사용: python s06dashboard.py   → ../app/dashboard.html
반출 CSV가 output/export/ 에 있어야 한다. 실제 데이터로 바꾸면 다시 실행만 하면 된다.
"""
import json
import os
import pandas as pd
import config

EXP = os.path.join(config.OUT_DIR, "export")
APP = os.path.join(os.path.dirname(__file__), "..", "app")
FILES = {"sido": "03_시도별.csv", "sgg": "03_시군구별.csv", "area": "03_면적구간별.csv",
         "supply": "03_공급유형별.csv", "sxa": "03_공급유형x면적.csv", "built": "03_준공연차별.csv",
         "rent": "03_임대료분위별.csv", "rooms": "03_방수별.csv", "year": "03_연도별_공실발생.csv",
         "imp": "04_변수중요도.csv", "perf": "04_모델성능.csv", "risk": "04_시군구_예측위험.csv"}
data = {}
for k, f in FILES.items():
    p = os.path.join(EXP, f)
    if os.path.exists(p):
        df = pd.read_csv(p, encoding="utf-8-sig")
        data[k] = json.loads(df.to_json(orient="records", force_ascii=False))
    else:
        data[k] = []
        print("없음:", f)
is_fake = os.path.abspath(config.DATA_DIR).endswith("fake_data")
meta = {"fake": is_fake, "built": pd.Timestamp.now().strftime("%Y-%m-%d"), "min_cell": config.MIN_CELL}
_tp = os.path.join(APP, "template.html")
if not os.path.exists(_tp):  # 센터 반입본은 확장자 제한으로 template.txt
    _tp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.txt")
tpl = open(_tp, encoding="utf-8").read()
os.makedirs(APP, exist_ok=True)
html = tpl.replace("/*__DATA__*/", "const DATA=" + json.dumps(data, ensure_ascii=False) + ";const META=" + json.dumps(meta, ensure_ascii=False) + ";")
out = os.path.join(APP, "dashboard.html")
open(out, "w", encoding="utf-8").write(html)
print("생성:", out, "(%.1f KB)" % (len(html.encode()) / 1024), "연습데이터" if is_fake else "실데이터")
