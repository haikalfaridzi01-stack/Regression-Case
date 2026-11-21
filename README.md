# Predictive Maintenance - Remaining Useful Life (RUL) Motor Induksi

> Prototipe sistem *predictive maintenance* berbasis Machine Learning untuk memperkirakan sisa umur operasional (*Remaining Useful Life/RUL*) motor induksi dari parameter kondisi motor.

<p align="center">
  <strong>Python · XGBoost · Scikit-learn · FastAPI · Streamlit</strong>
</p>

---

## Daftar Isi
- [Ringkasan](#ringkasan)
- [Fitur](#fitur)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Parameter Model](#parameter-model)
- [Teknologi](#teknologi)
- [Struktur Repository](#struktur-repository)
- [Persyaratan](#persyaratan)
- [Instalasi](#instalasi)
- [Menjalankan Aplikasi](#menjalankan-aplikasi)
- [REST API](#rest-api)
- [Pelatihan dan Evaluasi Model](#pelatihan-dan-evaluasi-model)
- [Pengujian](#pengujian)
- [Keterbatasan](#keterbatasan)
- [Pengembang](#pengembang)

## Ringkasan

Predictive maintenance memanfaatkan data kondisi peralatan untuk membantu memperkirakan kebutuhan pemeliharaan sebelum terjadi kegagalan. Repository ini mengimplementasikan prototipe prediksi RUL motor induksi menggunakan algoritma **XGBoost Regressor**.

Model menerima empat parameter sebagai fitur masukan:

1. Arus listrik
2. Getaran
3. Suhu body motor
4. Tegangan

Keluaran aplikasi berupa estimasi RUL dalam jam, kategori kondisi motor, dan waktu pemrosesan prediksi. Aplikasi menyediakan antarmuka Streamlit serta REST API menggunakan FastAPI.

**Catatan:** RUL yang dihasilkan merupakan estimasi model berdasarkan data pelatihan. Hasilnya bukan jaminan waktu kerusakan aktual dan tidak menggantikan inspeksi teknis.

## Fitur

- Prediksi RUL untuk satu set data masukan.
- Prediksi batch melalui unggah file CSV.
- Kategori kondisi motor berdasarkan ambang RUL yang ditetapkan aplikasi.
- Dua mode deployment: Streamlit langsung atau Streamlit dengan FastAPI.
- REST API untuk pemeriksaan kesehatan layanan dan prediksi.
- Validasi masukan API menggunakan Pydantic.
- Penyimpanan dan pemuatan artefak model.
- Smoke test untuk skenario normal, ekstrem, dan input tidak valid.

## Arsitektur Sistem

### Mode A = Streamlit langsung

```text
Pengguna
   |
   v
Streamlit UI
   |
   v
Predictor
   |
   v
Preprocessing
   |
   v
XGBoost Regressor
   |
   v
Estimasi RUL + Status
```

### Mode B = Streamlit + FastAPI

```text
Pengguna
   |
   v
Streamlit UI
   |
   v
HTTP POST /predict
   |
   v
FastAPI
   |
   v
Predictor + Preprocessing
   |
   v
XGBoost Regressor
   |
   v
Respons prediksi
```

Mode A memanggil modul prediksi secara lokal dari aplikasi Streamlit. Mode B memisahkan antarmuka dan backend; Streamlit mengirimkan data ke FastAPI melalui HTTP.

## Parameter Model

### Fitur masukan

| No. | Parameter | Nama kolom | Satuan |
|---:|---|---|---|
| 1 | Arus listrik | `arus_ampere` | Ampere (A) |
| 2 | Getaran | `getaran_mm_s` | mm/s |
| 3 | Suhu body motor | `suhu_body_c` | °C |
| 4 | Tegangan | `tegangan_volt` | Volt (V) |

### Keluaran

| Nama keluaran | Deskripsi |
|---|---|
| `remaining_useful_life_hours` | Estimasi sisa umur operasional motor dalam jam |
| `status` | Kategori kondisi berdasarkan aturan aplikasi |
| `latency_ms` | Waktu pemrosesan prediksi dalam milidetik |

### Kategori kondisi

| Estimasi RUL | Status | Interpretasi |
|---:|---|---|
| > 500 jam | `PRIMA` | Kondisi diperkirakan prima |
| > 100 hingga 500 jam | `NORMAL` | Kondisi diperkirakan normal |
| > 24 hingga 100 jam | `PERHATIAN` | Perlu menyiapkan pemeriksaan/perawatan |
| ≤ 24 jam | `KRITIS` | Perlu pemeriksaan segera |

Ambang kategori di atas merupakan aturan operasional yang ditetapkan di dalam aplikasi, **bukan standar universal** untuk seluruh motor induksi.

## Teknologi

| Teknologi | Peran |
|---|---|
| Python | Bahasa pemrograman |
| XGBoost Regressor | Model regresi untuk estimasi RUL |
| Scikit-learn | Preprocessing dan imputasi |
| Pandas, NumPy | Pengolahan data dan operasi numerik |
| FastAPI, Uvicorn | Backend REST API |
| Streamlit | Antarmuka aplikasi |
| Pydantic | Validasi skema input API |
| Joblib | Penyimpanan/pemuatan objek model |
| Requests, HTTPX | Komunikasi HTTP dan pengujian API |

## Struktur Repository

```text
Regression-Case/
├── app/
│   ├── api/
│   │   └── main.py
│   └── ui/
│       └── streamlit_app.py
├── artifacts/
│   ├── model_rul.joblib
│   ├── xgb_rul.json
│   ├── imputer_rul.joblib
│   └── metadata.json
├── data/
├── src/
│   ├── features.py
│   └── predictor.py
├── tests/
│   └── smoke_test.py
├── train_rul_model(2).ipynb
├── requirements.txt
└── README.md
```

**Ringkasan komponen:**

- `app/api/main.py` : endpoint FastAPI, validasi input, dan pemanggilan prediksi.
- `app/ui/streamlit_app.py` : antarmuka prediksi satuan dan batch CSV.
- `src/features.py` : pengelolaan fitur dan pembersihan nilai yang tidak valid.
- `src/predictor.py` : pemuatan artefak, preprocessing, prediksi, penentuan status, dan pengukuran latency.
- `artifacts/` — model, imputer, dan metadata.
- `tests/smoke_test.py` : pengujian dasar endpoint.
- `train_rul_model.ipynb` : notebook pelatihan dan pengembangan model.

Nama atau keberadaan artefak pada folder `artifacts/` dapat berbeda mengikuti hasil training. Pastikan berkas yang dibutuhkan oleh loader tersedia sebelum menjalankan aplikasi.

## Persyaratan

- Python 3.11-3.13 (sesuaikan dengan versi yang kompatibel dengan seluruh dependency).
- Git.
- Editor seperti Visual Studio Code atau Jupyter Notebook.
- Seluruh file artefak model yang dibutuhkan aplikasi.

## Instalasi

### 1. Clone repository

```bash
git clone https://github.com/haikalfaridzi01-stack/Regression-Case.git
cd Regression-Case
```

### 2. Buat virtual environment

**Windows PowerShell**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows CMD**
```bat
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instal dependensi

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Pastikan artefak model yang diperlukan tersedia di direktori `artifacts/`.

## Menjalankan Aplikasi

### Mode A : Streamlit langsung

```bash
python -m streamlit run app/ui/streamlit_app.py
```

Buka alamat berikut di browser:

- Streamlit: http://localhost:8501

### Mode B : Streamlit dengan FastAPI

Jalankan backend pada **Terminal 1**:

```bash
python -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000
```

Jalankan frontend pada **Terminal 2**.

**Windows PowerShell**
```powershell
$env:API_URL="http://127.0.0.1:8000"
python -m streamlit run app/ui/streamlit_app.py
```

**Windows CMD**
```bat
set API_URL=http://127.0.0.1:8000
python -m streamlit run app/ui/streamlit_app.py
```

**Linux / macOS**
```bash
export API_URL="http://127.0.0.1:8000"
python -m streamlit run app/ui/streamlit_app.py
```

Akses layanan:

| Layanan | URL |
|---|---|
| Streamlit | http://localhost:8501 |
| FastAPI | http://127.0.0.1:8000 |
| Swagger UI | http://127.0.0.1:8000/docs |
| Health check | http://127.0.0.1:8000/health |

Jika `API_URL` tidak diatur, aplikasi menggunakan pemanggilan model lokal (Mode A). Jika `API_URL` diatur, aplikasi menggunakan backend FastAPI (Mode B).

## REST API

### Health check

```http
GET /health
```

Endpoint ini digunakan untuk memeriksa status layanan dan status pemuatan model.

Contoh bentuk respons:

```json
{
  "status": "ok",
  "model_loaded": true
}
```

### Prediksi RUL

```http
POST /predict
Content-Type: application/json
```

Contoh request:

```json
{
  "arus_ampere": 12.5,
  "getaran_mm_s": 2.1,
  "suhu_body_c": 45,
  "tegangan_volt": 220
}
```

Batas validasi input yang didokumentasikan:

| Parameter | Minimum | Maksimum |
|---|---:|---:|
| Arus | 0 A | 100 A |
| Getaran | 0 mm/s | 50 mm/s |
| Suhu body | 0 °C | 200 °C |
| Tegangan | 0 V | 500 V |

Contoh struktur respons (nilai hanya ilustrasi):

```json
{
  "status": "success",
  "remaining_useful_life_hours": 350.25,
  "condition": "NORMAL",
  "latency_ms": 12.5
}
```

Nama field respons aktual mengikuti implementasi endpoint. Input yang gagal validasi FastAPI akan menghasilkan HTTP 422.

## Pelatihan dan Evaluasi Model

Notebook pelatihan tersedia pada:

```text
train_rul_model.ipynb
```

Konfigurasi yang tercantum pada metadata repository:

| Parameter | Nilai |
|---|---:|
| Algoritma | XGBRegressor |
| `n_estimators` | 300 |
| `learning_rate` | 0.05 |
| `max_depth` | 5 |
| Imputasi | Median |
| Versi metadata | 1.0.0 |

Alur umum:

1. Memuat dan memeriksa dataset.
2. Membersihkan data dan menyiapkan fitur.
3. Membagi data training dan testing.
4. Melakukan imputasi nilai hilang.
5. Melatih XGBoost Regressor.
6. Mengevaluasi hasil prediksi.
7. Menyimpan model dan artefak preprocessing.

## Pengujian

Jalankan smoke test dari direktori utama repository:

```bash
python -m tests.smoke_test
```

Skenario yang didokumentasikan:

| Skenario | Tujuan |
|---|---|
| Input normal | Memeriksa prediksi untuk input valid |
| Input ekstrem | Memeriksa penanganan nilai tinggi yang masih dalam rentang validasi |
| Input tidak valid | Memastikan input yang tidak memenuhi validasi ditolak |

Pengujian menggunakan `TestClient` dari FastAPI untuk memeriksa endpoint `/health` dan `/predict`.

## Keterbatasan

- RUL merupakan estimasi model dan tidak menjamin waktu kerusakan aktual.
- Kinerja model bergantung pada kualitas, jumlah, dan representativitas dataset.
- Ambang kategori kondisi merupakan aturan aplikasi, bukan standar industri universal.
- Prediksi belum dapat dianggap tervalidasi untuk penggunaan industri sebelum diuji pada data motor nyata dan kondisi operasi yang relevan.
- Metrik evaluasi harus dilaporkan berdasarkan hasil pengujian aktual; jangan mengisi nilai perkiraan.
- Aplikasi memerlukan artefak model dan preprocessing yang sesuai dengan versi kode.

## Pengembang

| Nama | NIM |
|---|---|
| Iqbal Imanudin | 2403141 |
| Muhammad Haikal Alfaridzi | 2407942 |

**Proyek:** Predictive Maintenance — Remaining Useful Life Prediction  
**Mata kuliah:** MKB

---

<p align="center">
  <sub>Developed with Python, XGBoost, FastAPI, and Streamlit.</sub>
</p>
