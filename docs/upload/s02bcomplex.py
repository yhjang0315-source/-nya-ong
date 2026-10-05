"""[본 분석 1-b] '같은 단지로 보이는 집' 묶기 → 단지 단위 공실 집계.

LH 데이터에는 단지명이 없다. 대신 같은 법정동 + 같은 준공년월 + 같은 공급유형 + 같은 주택유형인
호들은 거의 같은 단지이므로 이를 '추정 단지'로 묶는다.
- 법정동코드가 시군구(5자리)까지만 들어 있으면 단지 구분이 거칠어지므로 경고를 출력한다.
결과
- output/work/추정단지.csv (센터 내부용)
- output/export/02b_추정단지별_공실.csv (반출용: 단지 키는 법정동코드·준공년월·유형만, 호 정보 없음, 소수 단지 가림)
"""
import pandas as pd
import common
import config

work = config.OUT_DIR + "/work"
unit = pd.read_csv(work + "/호특성.csv", dtype={"법정동코드": str})

code = unit["법정동코드"].fillna("").str.replace(r"\D", "", regex=True)
digits = code.str.rstrip("0").str.len().median()
n_dong = code.nunique()
print("법정동코드 고유값 %d개, 유효 자리수 중앙값 %.0f" % (n_dong, digits))
if digits <= 5:
    print("⚠ 법정동코드가 시군구 수준으로 보임 → 추정 단지 정확도 낮음. 조건 묶음(03) 분석을 우선 사용")

unit["준공년월"] = (unit["준공년월_i"] // 12).astype("Int64").astype(str) + \
                  ((unit["준공년월_i"] % 12 + 1).astype("Int64").astype(str).str.zfill(2))
key = ["시도", "시군구", "법정동코드", "준공년월", "공급유형", "주택유형"]
cx = unit.groupby(key, dropna=False).agg(
    호수=("호관리번호", "size"),
    현재공실호수=("현재공실", "sum"),
    현재공실_중위개월=("현재공실개월", "median"),
    평균누적공실개월=("누적공실개월", "mean"),
    최장공실_중위개월=("최장공실개월", "median"),
    평균전용면적=("전용면적", "mean"),
    소형비율=("전용면적", lambda s: (s < 40).mean()),
    중도해약_호당평균=("중도해약수", "mean"),
    초기미임대_중위개월=("초기미임대개월", "median"),
).reset_index()
cx["현재공실률(%)"] = 100 * cx["현재공실호수"] / cx["호수"]
cx["장기공실호비율(%)"] = unit.assign(L=(unit["최장공실개월"] >= 12) | (unit["현재공실개월"] >= 12)) \
    .groupby(key, dropna=False)["L"].mean().values * 100
cx = cx.round(2).sort_values("현재공실률(%)", ascending=False)
cx.insert(0, "추정단지ID", range(1, len(cx) + 1))
cx.to_csv(work + "/추정단지.csv", index=False, encoding="utf-8-sig")
print("추정 단지 수:", len(cx), "/ 단지당 평균 호수: %.1f" % cx["호수"].mean())
common.save(common.mask_small(cx), "02b_추정단지별_공실.csv")
