"""전체 실행: python run_all.py  (가짜 데이터로 연습할 때는 python run_all.py --fake)"""
import runpy
import sys

steps = ["01_profile.py", "02_build_vacancy.py", "03_aggregate_export.py", "04_context_model.py"]
if "--fake" in sys.argv:
    steps = ["00_make_fake_data.py"] + steps
for s in steps:
    print("\n==========", s, "==========")
    runpy.run_path(s, run_name="__main__")
