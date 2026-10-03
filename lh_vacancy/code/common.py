"""공통 함수: 읽기, 날짜 변환, 반출용 마스킹/저장."""
import os
import numpy as np
import pandas as pd
import config


def ensure_out(sub=""):
    path = os.path.join(config.OUT_DIR, sub)
    os.makedirs(path, exist_ok=True)
    return path


def read_csv(key, usecols=None, sep=",", chunksize=None):
    """정의서 기준 utf-8. 깨지면 cp949로 다시 시도."""
    path = os.path.join(config.DATA_DIR, config.FILES[key])
    for enc in ("utf-8", "utf-8-sig", "cp949"):
        try:
            return pd.read_csv(path, sep=sep, encoding=enc, dtype=str, usecols=usecols,
                               chunksize=chunksize, low_memory=False)
        except UnicodeDecodeError:
            continue
    raise ValueError("인코딩을 확인하세요: " + path)


def rename(df, mapping):
    return df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})


def ym_to_idx(s):
    """'YYYYMM' 문자열 -> 월 번호(년*12+월-1). 비었거나 이상하면 NaN."""
    s = pd.Series(s).astype(str).str.replace(r"\D", "", regex=True).str[:6]
    y = pd.to_numeric(s.str[:4], errors="coerce")
    m = pd.to_numeric(s.str[4:6], errors="coerce")
    idx = y * 12 + (m - 1)
    idx[(m < 1) | (m > 12) | (y < 1950) | (y > 2100)] = np.nan
    return idx


def idx_to_year(idx):
    return (idx // 12).astype("Int64")


def mask_small(df, count_col="호수", min_cell=None):
    """건수가 기준 미만인 행의 값은 가린다(반출 심의 대비)."""
    min_cell = min_cell or config.MIN_CELL
    out = df.copy()
    small = out[count_col] < min_cell
    for c in out.columns:
        if c != count_col and pd.api.types.is_numeric_dtype(out[c]):
            out[c] = out[c].astype(float)
            out.loc[small, c] = np.nan
    out[count_col] = out[count_col].astype(object)
    out.loc[small, count_col] = "<%d" % min_cell
    return out


def save(df, name, sub="export"):
    path = os.path.join(ensure_out(sub), name)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print("저장:", path, df.shape)
    return path


def setup_korean_font():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    for name in ["Malgun Gothic", "NanumGothic", "AppleGothic", "Noto Sans CJK KR"]:
        if any(name in f.name for f in font_manager.fontManager.ttflist):
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False
    return plt
