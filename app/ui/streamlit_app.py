"""Antarmuka Streamlit: Prediksi Sisa Umur Pakai (RUL) Motor Induksi.

Mode A (API_URL kosong)  : UI -> predictor -> model   
Mode B (API_URL terisi)  : UI -> FastAPI -> predictor -> model
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))  

import altair as alt
import numpy as np
import pandas as pd
import requests
import streamlit as st

from src.features import FITUR_INPUT
from src.predictor import load_model, predict_rul, status_dari_rul

# ----------------------------------------------------------------------------
# Konfigurasi
# ----------------------------------------------------------------------------
NAMA_PENGEMBANG = "Iqbal Imanudin & Muhammad Haikal"
NIM = "2403141 & 2407942" 
API_URL = os.environ.get("API_URL", "").rstrip("/")
HORIZON_JAM = 2500 

SENSOR = {
    "arus_ampere": dict(
        label="Arus", satuan="A", ikon="", min=0.0, max=100.0, default=12.5, step=0.1,
        plot=(8.0, 22.0), judul="Beban listrik motor",
        info="",
    ),
    "getaran_mm_s": dict(
        label="Getaran", satuan="mm/s", ikon="", min=0.0, max=50.0, default=2.1, step=0.1,
        plot=(0.5, 12.0), judul="Getaran mekanis",
        info="",
    ),
    "suhu_body_c": dict(
        label="Suhu body", satuan="°C", ikon="", min=0.0, max=200.0, default=45.0, step=0.5,
        plot=(30.0, 100.0), judul="Suhu badan motor",
        info="Suhu tinggi mempercepat penuaan isolasi gulungan",
    ),
    "tegangan_volt": dict(
        label="Tegangan", satuan="V", ikon="", min=0.0, max=500.0, default=220.0, step=0.5,
        plot=(200.0, 240.0), judul="Tegangan suplai",
        info="Tegangan yang jauh menyimpang dari nominal membebani motor dan memperpendek umur.",
    ),
}

STATUS = {
    "PRIMA": dict(ikon="", judul="Kondisi Prima", warna="#16a34a", rentang="> 500 jam",
                  saran="Operasi normal. Lanjutkan inspeksi rutin sesuai jadwal.",
                  tindakan=["Lanjutkan operasi normal", "Inspeksi rutin sesuai jadwal", "Catat data sensor berkala"]),
    "NORMAL": dict(ikon="", judul="Kondisi Normal", warna="#2563eb", rentang="> 100 – 500 jam",
                   saran="Motor layak beroperasi",
                   tindakan=["Pantau sensor lebih sering", "Rencanakan jadwal servis berikutnya",
                             "Periksa tren getaran dan suhu"]),
    "PERHATIAN": dict(ikon="", judul="Perlu Perhatian", warna="#d97706", rentang="> 24 – 100 jam",
                      saran="Sisa umur menipis, Siapkan servis dan suku cadang.",
                      tindakan=["Jadwalkan servis dalam waktu dekat", "Siapkan bearing / suku cadang",
                                "Kurangi beban jika memungkinkan", "Pantau sensor setiap hari"]),
    "KRITIS": dict(ikon="", judul="KRITIS", warna="#dc2626", rentang="≤ 24 jam",
                   saran="Risiko gagal sangat dekat. Hentikan operasi dan segera lakukan servis.",
                   tindakan=["Hentikan operasi motor", "Lakukan inspeksi dan servis segera",
                             "Pastikan motor cadangan / rencana darurat siap", "Investigasi penyebab sebelum dihidupkan lagi"]),
}
URUTAN_STATUS = ["KRITIS", "PERHATIAN", "NORMAL", "PRIMA"]

PRESET = {
    "🟢 Motor sehat": dict(arus_ampere=11.0, getaran_mm_s=1.5, suhu_body_c=43.0, tegangan_volt=220.0),
    "🟡 Performa Mulai Menurun": dict(arus_ampere=14.0, getaran_mm_s=3.8, suhu_body_c=58.0, tegangan_volt=219.0),
    "🟠 Beban cukup tinggi": dict(arus_ampere=17.0, getaran_mm_s=7.5, suhu_body_c=72.0, tegangan_volt=218.0),
    "🔴 Ekstrem (uji batas)": dict(arus_ampere=20.0, getaran_mm_s=12.0, suhu_body_c=95.0, tegangan_volt=200.0),
}

st.set_page_config(page_title="Prediksi RUL Motor Induksi", page_icon="⚙️", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown(
    """
<style>
.block-container {padding-top: 3.6rem; max-width: 1280px;}
.hero {background: linear-gradient(135deg,#1e3a8a 0%,#2563eb 55%,#0ea5e9 100%); color:#fff;
       padding:1.5rem 1.8rem; border-radius:16px; margin-bottom:1.1rem;}
.hero-judul {font-size:1.9rem; font-weight:800; line-height:1.2; color:#fff;}
.hero-sub {margin-top:.35rem; opacity:.93; font-size:1.02rem; color:#fff;}
.chips {margin-top:.8rem;}
.chip {display:inline-block; padding:.18rem .65rem; margin:0 .35rem .3rem 0; border-radius:999px;
       font-size:.78rem; background:rgba(255,255,255,.18); color:#fff; border:1px solid rgba(255,255,255,.28);}
.chip-kecil {display:inline-block; padding:.12rem .55rem; margin:0 .3rem .3rem 0; border-radius:999px;
       font-size:.74rem; color:#fff;}
.kartu {border:1px solid rgba(128,128,128,.25); border-radius:14px;
        padding:1rem 1.3rem; background:rgba(128,128,128,.07); margin-bottom:.8rem;}
.kartu-label {font-size:.85rem; opacity:.75; text-transform:uppercase; letter-spacing:.04em;}
.kartu-angka {font-size:2.9rem; font-weight:800; line-height:1.1; margin:.15rem 0;}
.kartu-angka span {font-size:1.2rem; font-weight:600; opacity:.7;}
.kartu-status {font-size:1.25rem; font-weight:700;}
.kartu-saran {margin-top:.25rem; opacity:.85;}
.kartu-kosong {border:2px dashed rgba(128,128,128,.35); border-radius:14px; padding:1.6rem 1.4rem;
        background:rgba(128,128,128,.05);}
.zona-row {display:flex; gap:6px; margin:.2rem 0 .9rem 0;}
.zona {flex:1; text-align:center; padding:.5rem .2rem; border-radius:10px; font-size:.82rem;
       color:#fff; opacity:.3;}
.zona small {opacity:.9;}
.zona.aktif {opacity:1; font-weight:700; box-shadow:0 0 0 3px rgba(128,128,128,.4);}
.metrik-row {display:flex; gap:.6rem; margin:.2rem 0 .7rem 0;}
.metrik {flex:1; min-width:0; border:1px solid rgba(128,128,128,.25); border-radius:12px; padding:.55rem .75rem; background:rgba(128,128,128,.06);}
.metrik-l {font-size:.78rem; opacity:.75;}
.metrik-v {font-size:1.5rem; font-weight:700; white-space:nowrap;}
.alur {display:flex; flex-wrap:wrap; align-items:center; gap:.4rem; margin:.4rem 0 .8rem 0;}
.alur .langkah {padding:.35rem .8rem; border-radius:10px; background:rgba(37,99,235,.14);
        border:1px solid rgba(37,99,235,.35); font-size:.9rem;}
.alur .panah {opacity:.55;}
</style>
""",
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Utilitas
# ----------------------------------------------------------------------------
def fmt(x, d=1):
    """Format angka gaya Indonesia: 1.234,5"""
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


@st.cache_resource(show_spinner="Memuat model...")
def get_model():
    return load_model()


@st.cache_data(show_spinner=False)
def baca_metadata():
    try:
        return json.loads((ROOT / "artifacts" / "metadata.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


@st.cache_data(show_spinner=False)
def baca_data():
    """Data referensi."""
    try:
        df = pd.read_csv(ROOT / "data" / "dataset_motor_induksi_rul_dummy.csv")
    except Exception:
        return None
    if any(c not in df.columns for c in FITUR_INPUT) or len(df) < 30:
        return None
    kolom = FITUR_INPUT + (["sisa_umur_jam"] if "sisa_umur_jam" in df.columns else [])
    ref = df[kolom].copy()
    for c in ("arus_ampere", "getaran_mm_s"):
        ref.loc[ref[c] < 0, c] = np.nan
    return ref


def prediksi(payload: dict) -> dict:
    if API_URL:
        r = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        if r.status_code == 422:
            raise ValueError(f"Input ditolak validasi: {r.json().get('detail')}")
        r.raise_for_status()
        return r.json()
    return predict_rul(get_model(), payload)


def terapkan_preset(nama):
    for k, v in PRESET[nama].items():
        st.session_state[f"in_{k}"] = v


def html_hasil(rul, kode):
    s = STATUS[kode]
    return (
        f'<div class="kartu" style="border-left:7px solid {s["warna"]}">'
        f'<div class="kartu-label">Estimasi sisa umur pakai</div>'
        f'<div class="kartu-angka" style="color:{s["warna"]}">{fmt(rul, 1)} <span>jam</span></div>'
        f'<div class="kartu-status">{s["ikon"]} {s["judul"]}</div>'
        f'<div class="kartu-saran">{s["saran"]}</div></div>'
    )


def html_metrik(item):
    """item: daftar (label, nilai, bantuan)."""
    isi = "".join(
        f'<div class="metrik" title="{h}"><div class="metrik-l">{l}</div><div class="metrik-v">{v}</div></div>'
        for l, v, h in item
    )
    return f'<div class="metrik-row">{isi}</div>'


def html_zona(aktif=None):
    isi = []
    for kode in URUTAN_STATUS:
        s = STATUS[kode]
        cls = "zona aktif" if kode == aktif else "zona"
        isi.append(f'<div class="{cls}" style="background:{s["warna"]}">{s["ikon"]} {kode.title()}<br><small>{s["rentang"]}</small></div>')
    return '<div class="zona-row">' + "".join(isi) + "</div>"


def posisi_persentil(ref, kolom, nilai):
    if ref is None:
        return None
    s = ref[kolom].dropna()
    if s.empty:
        return None
    return float((s < nilai).mean() * 100), float(s.min()), float(s.max())


def label_posisi(info, nilai):
    if info is None:
        return "–"
    p, lo, hi = info
    if nilai < lo:
        return " di bawah rentang data"
    if nilai > hi:
        return " di atas rentang data"
    if p >= 90:
        return f" tinggi (persentil {p:.0f})"
    if p <= 10:
        return f" rendah (persentil {p:.0f})"
    return f" kisaran umum (persentil {p:.0f})"


def kurva_sensitivitas(model, payload, kolom, n=60):
    lo, hi = SENSOR[kolom]["plot"]
    v = payload[kolom]
    xs = np.linspace(min(lo, v), max(hi, v), n)
    df = pd.DataFrame([{**payload, kolom: float(x)} for x in xs])
    y = np.asarray(model.predict(df[FITUR_INPUT])).clip(min=0)
    return pd.DataFrame({"x": xs, "RUL": y})


def grafik_sensitivitas(model, payload, rul, kolom):
    s = SENSOR[kolom]
    d = kurva_sensitivitas(model, payload, kolom)
    v = payload[kolom]
    garis = alt.Chart(d).mark_line(strokeWidth=3).encode(
        x=alt.X("x:Q", title=f"{s['label']} ({s['satuan']})"), y=alt.Y("RUL:Q", title="RUL (jam)"))
    ambang = alt.Chart(pd.DataFrame({"y": [24, 100, 500]})).mark_rule(opacity=0.35, strokeDash=[2, 3]).encode(y="y:Q")
    vertikal = alt.Chart(pd.DataFrame({"x": [v]})).mark_rule(color="#dc2626", strokeDash=[6, 4]).encode(x="x:Q")
    titik = alt.Chart(pd.DataFrame({"x": [v], "RUL": [rul]})).mark_point(
        size=130, filled=True, color="#dc2626").encode(x="x:Q", y="RUL:Q")
    return (garis + ambang + vertikal + titik).properties(height=230, title=f"{s['ikon']} {s['judul']}")


# ----------------------------------------------------------------------------
# State
# ----------------------------------------------------------------------------
for _k, _s in SENSOR.items():
    st.session_state.setdefault(f"in_{_k}", _s["default"])
st.session_state.setdefault("riwayat", [])
st.session_state.setdefault("hasil", None)

meta = baca_metadata()
ref = baca_data()

# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Prediksi RUL Motor")
    if API_URL:
        st.info(f"**Mode B**: UI → FastAPI → model\n\n`{API_URL}`")
    else:
        st.success("**Mode A**: UI → predictor → model\n\nTanpa API, satu proses.")

    st.markdown("####  Contoh skenario")
    st.caption("Klik untuk mengisi form otomatis, lalu tekan **Prediksi**.")
    for _nama in PRESET:
        st.button(_nama, use_container_width=True, on_click=terapkan_preset, args=(_nama,))

    st.markdown("####  Ambang status")
    st.markdown(
        "".join(
            f'<span class="chip-kecil" style="background:{STATUS[k]["warna"]}">{STATUS[k]["ikon"]} {k.title()} · {STATUS[k]["rentang"]}</span><br>'
            for k in ["PRIMA", "NORMAL", "PERHATIAN", "KRITIS"]
        ),
        unsafe_allow_html=True,
    )

    st.markdown("####  Tentang model")
    st.caption(
        "XGBoost Regressor dalam pipeline *pembersihan → imputasi median → XGBoost*. "
        "Input: arus, getaran, suhu, tegangan. Output: sisa umur (jam)."
    )
    if ref is not None:
        st.caption(f"Data referensi: **{len(ref):,}** baris".replace(",", "."))
    st.divider()
    st.caption("Mekatronika dan Kecerdasan Buatan")
    if NAMA_PENGEMBANG:
        st.caption(f" {NAMA_PENGEMBANG}" + (f" · {NIM}" if NIM else ""))

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.markdown(
    '<div class="hero">'
    '<div class="hero-judul">⚙️ Prediksi Sisa Umur Pakai Motor Induksi</div>'
    '<div class="hero-sub">Predictive maintenance: empat sensor operasional → estimasi '
    '<i>Remaining Useful Life</i> (jam) dan status perawatan.</div>',
    unsafe_allow_html=True,
)

tab_prediksi, tab_batch, tab_info = st.tabs(["🔮 Prediksi", "📦 Prediksi Batch (CSV)", "📖 Tentang"])

# ----------------------------------------------------------------------------
# Tab 1: Prediksi tunggal
# ----------------------------------------------------------------------------
with tab_prediksi:
    kol_input, kol_hasil = st.columns([1, 1.25], gap="large")

    with kol_input:
        with st.container(border=True):
            st.subheader(" Data sensor")
            with st.form("form_sensor"):
                c1, c2 = st.columns(2)
                nilai = {}
                for i, (k, s) in enumerate(SENSOR.items()):
                    with (c1 if i % 2 == 0 else c2):
                        nilai[k] = st.number_input(
                            f"{s['ikon']} {s['label']} ({s['satuan']})",
                            min_value=s["min"], max_value=s["max"], step=s["step"], key=f"in_{k}",
                            help=f"{s['info']} Rentang input: {s['min']:g}–{s['max']:g} {s['satuan']}.",
                        )
                kirim = st.form_submit_button(" Prediksi sisa umur", type="primary", use_container_width=True)
            st.caption("Nilai negatif dari sensor yang rusak otomatis dibersihkan, dan data kosong diisi median.")

    if kirim:
        payload = {k: float(v) for k, v in nilai.items()}
        try:
            with st.spinner("Menghitung prediksi..."):
                hasil = prediksi(payload)
            rul = float(hasil["remaining_useful_life_hours"])
            kode = status_dari_rul(rul)
            st.session_state["hasil"] = dict(payload=payload, hasil=hasil, rul=rul, kode=kode)
            st.session_state["riwayat"] = (st.session_state["riwayat"] + [
                dict(waktu=datetime.now().strftime("%H:%M:%S"), **payload, rul_jam=round(rul, 2), status=kode.title())
            ])[-20:]
        except requests.exceptions.ConnectionError:
            st.session_state["hasil"] = None
            kol_hasil.error("API belum berjalan. Jalankan uvicorn di terminal terpisah, atau kosongkan API_URL (Mode A).")
        except Exception as e:
            st.session_state["hasil"] = None
            kol_hasil.error(f"Terjadi kesalahan: {e}")

    H = st.session_state["hasil"]

    with kol_hasil:
        if H is None:
            st.markdown(
                '<div class="kartu-kosong"><b>Belum ada prediksi.</b><br>'
                'Isi nilai sensor di sebelah kiri (atau pilih <b>Contoh skenario</b> di sidebar), '
                'lalu klik <b>Prediksi sisa umur</b>.<br><br>'
                'Anda akan mendapat: estimasi sisa umur, status perawatan, rincian tiap sensor, '
                'analisis sensitivitas, dan rekomendasi tindakan.</div>',
                unsafe_allow_html=True,
            )
        else:
            rul, kode = H["rul"], H["kode"]
            st.markdown(html_hasil(rul, kode), unsafe_allow_html=True)
            st.markdown(html_zona(kode), unsafe_allow_html=True)
            st.markdown(html_metrik([
                ("Sisa umur (jam)", fmt(rul, 1), "Estimasi sisa umur pakai (jam)."),
                ("≈ Hari", fmt(rul / 24, 1), "Jika motor beroperasi 24 jam per hari."),
                ("≈ Hari kerja", fmt(rul / 8, 1), "Jika motor beroperasi 8 jam per hari."),
                ("Proses (ms)", fmt(float(H["hasil"].get("latency_ms", 0)), 1), "Waktu menghitung prediksi."),
            ]), unsafe_allow_html=True)
            st.progress(min(rul / HORIZON_JAM, 1.0),
                        text=f"Indikator relatif: {min(rul / HORIZON_JAM, 1.0) * 100:.0f}% dari {fmt(HORIZON_JAM, 0)} jam")
            if {k: float(st.session_state[f'in_{k}']) for k in SENSOR} != H["payload"]:
                st.warning("Nilai input berubah sejak prediksi terakhir. Klik **Prediksi** untuk menghitung ulang.")

    
    if H is not None:
        payload, rul, kode = H["payload"], H["rul"], H["kode"]
        st.divider()

        di_luar = [SENSOR[k]["label"] for k in SENSOR
                   if (p := posisi_persentil(ref, k, payload[k])) is not None and not (p[1] <= payload[k] <= p[2])]
        if di_luar:
            st.warning(f" Input **{', '.join(di_luar)}** berada di luar rentang data referensi. "
                       "Prediksi untuk kondisi seperti ini kurang bagus.")

        t_sensor, t_rek, t_riw, t_json = st.tabs(
            [" Rincian sensor", " Rekomendasi", " Riwayat sesi", " JSON"])

        with t_sensor:
            baris = []
            for k, s in SENSOR.items():
                info = posisi_persentil(ref, k, payload[k])
                baris.append({"Sensor": f"{s['ikon']} {s['label']}", "Nilai": f"{payload[k]:g} {s['satuan']}",
                              "Peran": s["judul"], "Posisi vs data": label_posisi(info, payload[k])})
            st.dataframe(pd.DataFrame(baris), hide_index=True, use_container_width=True)
            for k, s in SENSOR.items():
                st.markdown(f"**{s['ikon']} {s['label']}**: {s['info']}")

        with t_rek:
            s = STATUS[kode]
            st.markdown(f"#### {s['ikon']} {s['judul']}: tindakan yang disarankan")
            for t in s["tindakan"]:
                st.markdown(f"- {t}")
            st.caption("Saran umum untuk membantu keputusan, bukan pengganti penilaian teknisi.")
            st.markdown("#### Panduan semua status")
            st.dataframe(pd.DataFrame([
                {"Status": f"{STATUS[k]['ikon']} {k.title()}", "Sisa umur": STATUS[k]["rentang"],
                 "Tindakan": "; ".join(STATUS[k]["tindakan"][:2])} for k in ["PRIMA", "NORMAL", "PERHATIAN", "KRITIS"]]),
                hide_index=True, use_container_width=True)

        with t_riw:
            rw = pd.DataFrame(st.session_state["riwayat"])
            st.caption(f"{len(rw)} prediksi terakhir pada sesi ini (maks. 20).")
            st.dataframe(rw.rename(columns={"waktu": "Waktu", "rul_jam": "RUL (jam)", "status": "Status"}),
                         hide_index=True, use_container_width=True)
            if len(rw) >= 2:
                st.line_chart(rw.reset_index().rename(columns={"index": "Prediksi ke-", "rul_jam": "RUL (jam)"}),
                              x="Prediksi ke-", y="RUL (jam)", height=220)
            cA, cB = st.columns(2)
            cA.download_button(" Unduh riwayat (CSV)", rw.to_csv(index=False).encode("utf-8"),
                               "riwayat_prediksi.csv", "text/csv", use_container_width=True)
            if cB.button(" Hapus riwayat", use_container_width=True):
                st.session_state["riwayat"] = []
                st.rerun()

        with t_json:
            st.json({"input": payload, "output": H["hasil"]})

# ----------------------------------------------------------------------------
# Tab 2: Batch
# ----------------------------------------------------------------------------
with tab_batch:
    st.subheader(" Prediksi banyak motor sekaligus")
    st.caption("Kolom wajib: " + ", ".join(f"`{c}`" for c in FITUR_INPUT) +
               ". Kolom `sisa_umur_jam` (opsional) dipakai untuk menghitung akurasi.")
    contoh = pd.DataFrame({
        "arus_ampere": [11.0, 14.0, 20.0], "getaran_mm_s": [1.5, 3.8, 12.0],
        "suhu_body_c": [43.0, 58.0, 95.0], "tegangan_volt": [220.0, 219.0, 200.0]})
    st.download_button(" Unduh template CSV", contoh.to_csv(index=False).encode("utf-8"),
                       "template_batch.csv", "text/csv")
    up = st.file_uploader("Unggah CSV", type="csv")
    if up is not None:
        try:
            df = pd.read_csv(up)
        except Exception as e:
            st.error(f"File tidak bisa dibaca: {e}")
            df = None
        if df is not None:
            kurang = [c for c in FITUR_INPUT if c not in df.columns]
            if kurang:
                st.error(f"Kolom tidak ada: {kurang}")
            elif df.empty:
                st.error("File kosong.")
            else:
                for c in FITUR_INPUT:
                    df[c] = pd.to_numeric(df[c], errors="coerce")
                n_nan = int(df[FITUR_INPUT].isna().sum().sum())
                n_neg = int((df[["arus_ampere", "getaran_mm_s"]] < 0).sum().sum())
                try:
                    mdl = get_model()
                    df["prediksi_rul_jam"] = np.asarray(mdl.predict(df[FITUR_INPUT])).clip(min=0).round(2)
                except Exception as e:
                    st.error(f"Gagal memprediksi: {e}")
                    st.stop()
                kodes = df["prediksi_rul_jam"].map(status_dari_rul)
                df["status"] = kodes.map(lambda k: f"{STATUS[k]['ikon']} {k.title()}")
                hitung = kodes.value_counts().reindex(URUTAN_STATUS, fill_value=0)

                st.success(f"Berhasil memprediksi **{len(df):,}** baris.".replace(",", "."))
                if n_nan or n_neg:
                    st.info(f"Kualitas data: {n_nan} nilai kosong/tidak valid dan {n_neg} nilai negatif pada arus/getaran. "
                            "Nilai-nilai ini otomatis dibersihkan (diisi median).")

                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Jumlah motor", f"{len(df):,}".replace(",", "."))
                k2.metric("Rata-rata RUL (jam)", fmt(df['prediksi_rul_jam'].mean(), 1))
                k3.metric(" Kritis", int(hitung["KRITIS"]))
                k4.metric(" Perhatian", int(hitung["PERHATIAN"]))

                g1, g2 = st.columns(2)
                dstat = pd.DataFrame({"Status": [k.title() for k in URUTAN_STATUS], "Jumlah": hitung.values})
                g1.altair_chart(alt.Chart(dstat).mark_bar().encode(
                    x=alt.X("Status:N", sort=[k.title() for k in URUTAN_STATUS], title=None),
                    y=alt.Y("Jumlah:Q"),
                    color=alt.Color("Status:N", legend=None, scale=alt.Scale(
                        domain=[k.title() for k in URUTAN_STATUS], range=[STATUS[k]["warna"] for k in URUTAN_STATUS])),
                ).properties(height=260, title="Sebaran status"), use_container_width=True)
                g2.altair_chart(alt.Chart(df).mark_bar().encode(
                    x=alt.X("prediksi_rul_jam:Q", bin=alt.Bin(maxbins=30), title="RUL prediksi (jam)"),
                    y=alt.Y("count():Q", title="Jumlah"),
                ).properties(height=260, title="Distribusi RUL"), use_container_width=True)

                if "sisa_umur_jam" in df.columns:
                    aktual = pd.to_numeric(df["sisa_umur_jam"], errors="coerce")
                    ok = aktual.notna()
                    if ok.sum() >= 2:
                        e = aktual[ok] - df.loc[ok, "prediksi_rul_jam"]
                        ss_tot = float(((aktual[ok] - aktual[ok].mean()) ** 2).sum())
                        r2 = 1 - float((e ** 2).sum()) / ss_tot if ss_tot > 0 else float("nan")
                        st.markdown("####  Akurasi terhadap kolom `sisa_umur_jam`")
                        a1, a2, a3 = st.columns(3)
                        a1.metric("MAE (jam)", fmt(float(e.abs().mean()), 1))
                        a2.metric("RMSE (jam)", fmt(float(np.sqrt((e ** 2).mean())), 1))
                        a3.metric("R²", f"{r2:.3f}")
                        st.caption("")
                        sc = pd.DataFrame({"Aktual": aktual[ok], "Prediksi": df.loc[ok, "prediksi_rul_jam"]})
                        lim = float(max(sc.max()))
                        st.altair_chart(
                            alt.Chart(sc).mark_circle(size=40, opacity=0.5).encode(
                                x=alt.X("Aktual:Q", title="RUL aktual (jam)"), y=alt.Y("Prediksi:Q", title="RUL prediksi (jam)"))
                            + alt.Chart(pd.DataFrame({"x": [0, lim], "y": [0, lim]})).mark_line(
                                color="#dc2626", strokeDash=[6, 4]).encode(x="x:Q", y="y:Q"),
                            use_container_width=True)

                st.markdown("####  Hasil lengkap")
                urut = st.checkbox("Tampilkan yang paling kritis di atas", value=True)
                tampil = df.sort_values("prediksi_rul_jam") if urut else df
                st.dataframe(
                    tampil, hide_index=True, use_container_width=True,
                    column_config={"prediksi_rul_jam": st.column_config.ProgressColumn(
                        "RUL prediksi (jam)", min_value=0.0,
                        max_value=float(max(HORIZON_JAM, df["prediksi_rul_jam"].max())), format="%.1f")})
                st.download_button(" Unduh hasil (CSV)", df.to_csv(index=False).encode("utf-8"),
                                   "hasil_prediksi_rul.csv", "text/csv", type="primary")
    else:
        st.info("Belum ada file. Unduh template di atas, isi data motor Anda, lalu unggah di sini.")

# ----------------------------------------------------------------------------
# Tab 3: Panduan & tentang
# ----------------------------------------------------------------------------
with tab_info:
    a, b = st.columns([1.1, 1], gap="medium")
    with a:
        st.subheader(" Status perawatan")
        for k in ["PRIMA", "NORMAL", "PERHATIAN", "KRITIS"]:
            s = STATUS[k]
            st.markdown(
                f'<div class="kartu" style="border-left:7px solid {s["warna"]}"><b>{s["ikon"]} {k.title()}</b> · {s["rentang"]}<br>{s["saran"]}</div>',
                unsafe_allow_html=True)
        st.subheader(" Informasi model")
        info_model = {
            "Algoritma": meta.get("algoritma", "XGBoost Regressor"),
            "Versi model": meta.get("versi_model", "-"),
            "Fitur input": ", ".join(meta.get("fitur_input", FITUR_INPUT)),
            "Target": meta.get("target", "sisa_umur_jam"),
        }
        for k_, v_ in info_model.items():
            st.markdown(f"**{k_}:** {v_}")
        met = meta.get("metrik_test")
        if met:
            st.markdown("**Metrik evaluasi (test set):**")
            tabel = {"MAE model (jam)": met.get("mae_model"), "RMSE model (jam)": met.get("rmse_model"),
                     "R² model": met.get("r2_model"), "MAE baseline (jam)": met.get("mae_baseline")}
            st.dataframe(pd.DataFrame({"Metrik": list(tabel), "Nilai": [("-" if v is None else round(v, 3)) for v in tabel.values()]}),
                         hide_index=True, use_container_width=True)
        else:
            st.caption("Metrik evaluasi dalam pengembangan.")
        lib = meta.get("library")
        if lib:
            st.caption("Library saat training: " + ", ".join(f"{k} {v}" for k, v in lib.items()))

    st.divider()
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.subheader(" Keterbatasan")
        st.markdown(
            "- Prediksi hanya **estimasi** dan bukan jaminan umur sebenarnya.\n"
            "- Model hanya andal pada rentang kondisi yang ada di data latih. Input ekstrem bisa menghasilkan estimasi yang terlalu optimis.\n"
            "- Data yang dipakai berukuran terbatas dan/atau sintetis, jadi belum divalidasi pada motor nyata.\n"
            "- Ambang status (500 / 100 / 24 jam) belum dikalibrasi dengan data perawatan lapangan.\n"
            "- Jangan dijadikan satu-satunya dasar keputusan keselamatan. Gabungkan dengan inspeksi teknisi."
        )

