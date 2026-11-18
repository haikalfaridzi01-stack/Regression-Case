"""Fungsi pembersihan fitur. Dipakai oleh training, API, dan Streamlit."""
import numpy as np

FITUR_INPUT = ["arus_ampere", "getaran_mm_s", "suhu_body_c", "tegangan_volt"]


def bersihkan_data(df):
    """Nilai negatif pada arus/getaran dianggap sensor error -> NaN (diimputasi median)."""
    df_bersih = df.copy()
    df_bersih.loc[df_bersih["getaran_mm_s"] < 0, "getaran_mm_s"] = np.nan
    df_bersih.loc[df_bersih["arus_ampere"] < 0, "arus_ampere"] = np.nan
    return df_bersih
