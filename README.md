# ⚙️ Predictive Maintenance: Prediksi Remaining Useful Life (RUL) Motor Induksi

Aplikasi **Predictive Maintenance** berbasis Machine Learning untuk memperkirakan *Remaining Useful Life* (RUL) atau estimasi sisa umur operasional motor induksi dalam satuan jam.

Proyek ini menggunakan algoritma **XGBoost Regressor** dengan memanfaatkan empat parameter sensor sebagai input prediksi, yaitu arus listrik, getaran, suhu body, dan tegangan.

Sistem dikembangkan dengan integrasi **Machine Learning, FastAPI, dan Streamlit** sehingga model dapat digunakan melalui antarmuka aplikasi maupun REST API.

---

## 🎯 Tujuan Proyek

Mengembangkan sistem prediksi pemeliharaan motor induksi yang dapat membantu memperkirakan sisa umur operasional motor berdasarkan kondisi parameter sensor.

Dengan pendekatan Predictive Maintenance, sistem diharapkan dapat membantu proses pemantauan kondisi motor dan mendukung pengambilan keputusan terkait perawatan sebelum terjadi kerusakan.

## 🧠 Teknologi yang Digunakan

| Teknologi | Fungsi |
|---|---|
| Python | Bahasa pemrograman utama |
| XGBoost Regressor | Algoritma Machine Learning untuk prediksi RUL |
| Scikit-learn | Pipeline preprocessing dan evaluasi model |
| Pandas & NumPy | Pengolahan dan manipulasi data |
| FastAPI | Backend REST API |
| Streamlit | Antarmuka aplikasi interaktif |
| Joblib | Penyimpanan dan pemuatan model |

## 📊 Parameter Input Prediksi

Model menggunakan empat parameter sensor sebagai variabel input:

| No. | Parameter Sensor | Satuan |
|---|---|---|
| 1 | Arus listrik | Ampere (A) |
| 2 | Getaran | mm/s |
| 3 | Suhu body motor | °C |
| 4 | Tegangan | Volt (V) |

**Output:** Estimasi Remaining Useful Life (RUL) dalam satuan jam.

## 🏗️ Arsitektur dan Struktur Proyek

```text
Predictive-Maintenance/
│
├── app/
│   ├── api/
│   │   └── main.py
│   │
│   └── ui/
│       └── streamlit_app.py
│
├── src/
│   ├── features.py
│   └── predictor.py
│
├── artifacts/
│   ├── model_rul.joblib
│   └── metadata.json
│
├── tests/
│   └── smoke_test.py
│
├── train_model.py
├── requirements.txt
└── README.md
```

### Penjelasan Komponen

| File / Folder | Deskripsi |
|---|---|
| `app/api/main.py` | Backend FastAPI dengan endpoint `/health`, `/predict`, dan `/docs`. |
| `app/ui/streamlit_app.py` | Antarmuka pengguna berbasis Streamlit dengan Mode A dan Mode B. |
| `src/features.py` | Proses pembersihan data dan pengelolaan fitur input model. |
| `src/predictor.py` | Memuat model XGBoost dan menjalankan proses prediksi. |
| `artifacts/` | Menyimpan model hasil training dan metadata model. |
| `tests/smoke_test.py` | Pengujian awal untuk input normal, ekstrem, dan tidak valid. |
| `train_model.py` | Script untuk melakukan pelatihan ulang model menggunakan dataset CSV. |

## 🚀 Instalasi dan Menjalankan Program

### 1. Persiapan Environment

Pastikan Python versi **3.11–3.13** sudah terinstal.

Clone repository:

```bash
git clone URL_REPOSITORY_KAMU
cd NAMA_FOLDER_PROJECT
```

Buat virtual environment:

```bash
python -m venv .venv
```

Aktifkan virtual environment.

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

**Mac / Linux:**

```bash
source .venv/bin/activate
```

Instal seluruh dependency:

```bash
pip install -r requirements.txt
```

### 2. Menjalankan Aplikasi

Tersedia dua mode untuk menjalankan aplikasi.

#### Mode A — Streamlit Langsung

Mode ini menjalankan aplikasi Streamlit dengan pemanggilan model secara langsung tanpa menjalankan server API terpisah.

```bash
python -m streamlit run app/ui/streamlit_app.py
```

#### Mode B — Streamlit dengan FastAPI

Mode ini menjalankan backend FastAPI dan frontend Streamlit secara terpisah.

**Terminal 1 — Menjalankan FastAPI:**

```bash
python -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — Menjalankan Streamlit:**

Windows PowerShell:

```powershell
$env:API_URL="http://127.0.0.1:8000"
python -m streamlit run app/ui/streamlit_app.py
```

Mac / Linux:

```bash
export API_URL="http://127.0.0.1:8000"
python -m streamlit run app/ui/streamlit_app.py
```

### 3. Mengakses Aplikasi

Setelah aplikasi berjalan, akses melalui browser:

| Layanan | URL |
|---|---|
| Streamlit | http://localhost:8501 |
| FastAPI | http://127.0.0.1:8000 |
| API Documentation (Swagger) | http://127.0.0.1:8000/docs |
| API Health Check | http://127.0.0.1:8000/health |

## 🧪 Pengujian Program

Untuk menjalankan pengujian awal, gunakan perintah:

```bash
python -m tests.smoke_test
```

Pengujian mencakup beberapa kondisi:

- Input sensor dalam kondisi normal.
- Input sensor dengan nilai ekstrem.
- Input tidak valid.
- Pemeriksaan awal proses pemuatan dan prediksi model.

## 🔄 Training Ulang Model

Apabila ingin melakukan pelatihan ulang model menggunakan dataset CSV, jalankan:

```bash
python train_model.py
```

Script tersebut digunakan untuk melatih model berdasarkan dataset yang disediakan dan menghasilkan artefak model untuk digunakan dalam proses prediksi.

Pastikan dataset dan konfigurasi pelatihan sudah sesuai sebelum melakukan training ulang.

## 📌 Catatan

- Model yang digunakan adalah XGBoost Regressor.
- Output prediksi dinyatakan dalam satuan jam.
- Aplikasi mendukung penggunaan model melalui Streamlit secara langsung maupun melalui FastAPI.
- Hasil prediksi merupakan estimasi berdasarkan pola data yang digunakan dalam pelatihan model, bukan jaminan umur aktual motor.
- Akurasi model bergantung pada kualitas, jumlah, dan representativitas dataset.

---

## 👨‍💻 Pengembang

**Nama:** Iqbal Ianudin  
**NIM:** [Isi NIM]  
**Mata Kuliah:** MKB  
**Proyek:** Predictive Maintenance – Prediksi RUL Motor Induksi

---

<p align="center">
  <b>Predictive Maintenance | Machine Learning Project</b>
  <br>
  Developed with Python, XGBoost, FastAPI, and Streamlit.
</p>
