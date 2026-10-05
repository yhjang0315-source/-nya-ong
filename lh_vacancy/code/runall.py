"""센터: python runall.py (CSV만 생성) / 집 연습: python runall.py --fake (가짜 데이터 + 그래프)
집에서 반출 CSV로 그래프만: python s05charts.py"""
import runpy
import sys

steps = ["s01profile.py", "s02vacancy.py", "s02bcomplex.py", "s03aggregate.py", "s04model.py"]
if "--charts" in sys.argv or "--fake" in sys.argv:
    steps = steps + ["s05charts.py", "s06dashboard.py"]
if "--fake" in sys.argv:
    steps = ["s00fake.py"] + steps[:-1] + ["s07match.py", steps[-1]]  # 07은 외부 공공 단지정보 필요(센터 밖)
for s in steps:
    print("\n==========", s, "==========")
    runpy.run_path(s, run_name="__main__")
