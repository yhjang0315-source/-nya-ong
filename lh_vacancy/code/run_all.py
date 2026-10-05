"""센터: python run_all.py (CSV만 생성) / 집 연습: python run_all.py --fake (가짜 데이터 + 그래프)
집에서 반출 CSV로 그래프만: python 05_make_charts.py"""
import runpy
import sys

steps = ["01_profile.py", "02_build_vacancy.py", "02b_complex.py", "03_aggregate_export.py", "04_context_model.py"]
if "--charts" in sys.argv or "--fake" in sys.argv:
    steps = steps + ["05_make_charts.py", "07_match_complex.py", "06_build_dashboard.py"]
if "--fake" in sys.argv:
    steps = ["00_make_fake_data.py"] + steps
for s in steps:
    print("\n==========", s, "==========")
    runpy.run_path(s, run_name="__main__")
