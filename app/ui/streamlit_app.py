import os
import sys
from pathlib import Path

# Pastikan root repo ada di sys.path agar 'import src' bekerja di mana pun dijalankan
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import requests
import streamlit as st

from src.predictor import load_model, predict_rul

st.set_page_config(page_title="Prediksi RUL Motor", page_icon="⚙️")

# API_URL kosong  -> Mode A (model dimuat langsung, cocok untuk Streamlit Cloud)
# API_URL terisi  -> Mode B (UI memanggil FastAPI, mis. http://127.0.0.1:8000)
API_URL = os.environ.get("API_URL", "").rstrip("/")


@st.cache_resource
def get_model():
    return load_model()


def prediksi(payload: dict) -> dict:
    if API_URL:
        r = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        if r.status_code == 422:
            raise ValueError(f"Input ditolak validasi: {r.json().get('detail')}")
        r.raise_for_status()
        return r.json()
    return predict_rul(get_model(), payload)


st.title("⚙️ Prediksi Sisa Umur Pakai Motor Induksi")
st.caption(
    "Mode B: UI → FastAPI → model" if API_URL else "Mode A: UI → predictor → model (tanpa API)"
)

with st.form("form_sensor"):
    st.subheader("Data Sensor")
    arus = st.number_input("Arus (Ampere)", 0.0, 100.0, 12.5)
    getaran = st.number_input("Getaran (mm/s)", 0.0, 50.0, 2.1)
    suhu = st.number_input("Suhu Body (°C)", 0.0, 200.0, 45.0)
    tegangan = st.number_input("Tegangan (Volt)", 0.0, 500.0, 220.0)
    submitted = st.form_submit_button("Prediksi Sisa Umur")

if submitted:
    payload = {
        "arus_ampere": arus,
        "getaran_mm_s": getaran,
        "suhu_body_c": suhu,
        "tegangan_volt": tegangan,
    }
    try:
        hasil = prediksi(payload)
        rul = hasil["remaining_useful_life_hours"]
        st.divider()
        if rul > 500:
            st.success(f"✅ **Kondisi Prima!** Estimasi sisa umur **{rul} jam**.")
        elif rul > 100:
            st.info(f"🆗 **Kondisi Normal.** Sisa umur operasional: **{rul} jam**.")
        elif rul > 24:
            st.warning(f"⚠️ **Perhatian.** Sisa umur: **{rul} jam**. Siapkan servis.")
        else:
            st.error(f"🚨 **KRITIS!** Hentikan operasi. Estimasi gagal dalam **{rul} jam**.")
        with st.expander("Lihat JSON"):
            st.json({"input": payload, "output": hasil})
    except requests.exceptions.ConnectionError:
        st.error("API belum berjalan. Jalankan uvicorn di terminal terpisah, atau kosongkan API_URL (Mode A).")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

st.divider()
st.subheader("Prediksi Batch (CSV)")
st.caption("Kolom wajib: " + ", ".join(["arus_ampere", "getaran_mm_s", "suhu_body_c", "tegangan_volt"]))
up = st.file_uploader("Unggah CSV", type="csv")
if up is not None:
    import pandas as pd

    df = pd.read_csv(up)
    kurang = [c for c in ["arus_ampere", "getaran_mm_s", "suhu_body_c", "tegangan_volt"] if c not in df.columns]
    if kurang:
        st.error(f"Kolom tidak ada: {kurang}")
    else:
        m = get_model()
        from src.features import FITUR_INPUT

        df["prediksi_rul_jam"] = m.predict(df[FITUR_INPUT]).clip(min=0).round(2)
        st.dataframe(df)
