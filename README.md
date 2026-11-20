# ⚙️ Predictive Maintenance Prediksi Remaining Useful Life (RUL) Motor Induksi

Aplikasi **Predictive Maintenance** berbasis Machine Learning untuk memprediksi *Remaining Useful Life* (RUL) atau estimasi sisa umur operasional motor induksi dalam satuan jam.

Proyek ini menggunakan algoritma **XGBoost Regressor** dengan empat parameter sensor sebagai variabel input, yaitu arus listrik, getaran, suhu body motor, dan tegangan.

Sistem dikembangkan menggunakan Python dengan integrasi **XGBoost, Scikit-learn, FastAPI, dan Streamlit**. Aplikasi menyediakan prediksi secara langsung melalui antarmuka Streamlit maupun melalui REST API menggunakan FastAPI.

---

## 🎯 Tujuan Proyek

Mengembangkan sistem prediksi pemeliharaan motor induksi yang dapat memperkirakan sisa umur operasional berdasarkan kondisi parameter sensor.

Sistem ini bertujuan untuk:

- Memperkirakan sisa umur operasional motor induksi.
- Mengolah data dari empat parameter sensor motor.
- Mengklasifikasikan kondisi motor berdasarkan hasil prediksi RUL.
- Mendukung proses pemantauan kondisi motor melalui aplikasi interaktif.
- Menyediakan layanan prediksi melalui REST API.

## 🧠 Teknologi yang Digunakan

| Teknologi | Fungsi |
|---|---|
| Python | Bahasa pemrograman utama |
| XGBoost Regressor | Algoritma Machine Learning untuk prediksi RUL |
| Scikit-learn | Preprocessing dan imputasi data |
| Pandas | Pengolahan data |
| NumPy | Operasi numerik |
| FastAPI | Backend REST API |
| Streamlit | Antarmuka aplikasi |
| Joblib | Penyimpanan dan pemuatan model |
| Requests | Komunikasi antara Streamlit dan FastAPI |
| Pydantic | Validasi input API |

## 📊 Parameter Input dan Output

Model menggunakan empat parameter sensor sebagai input prediksi.

| No. | Parameter | Nama Kolom | Satuan |
|---|---|---|---|
| 1 | Arus listrik | `arus_ampere` | Ampere (A) |
| 2 | Getaran | `getaran_mm_s` | mm/s |
| 3 | Suhu body motor | `suhu_body_c` | °C |
| 4 | Tegangan | `tegangan_volt` | Volt (V) |

**Output prediksi:**

- `remaining_useful_life_hours`: estimasi sisa umur motor dalam jam.
- `status`: kategori kondisi motor.
- `latency_ms`: waktu pemrosesan prediksi dalam milidetik.

## 🚦 Klasifikasi Kondisi Motor

Hasil prediksi RUL dikategorikan menjadi empat kondisi berdasarkan aturan pada program:

| Estimasi RUL | Status | Keterangan |
|---|---|---|
| > 500 jam | 🟢 PRIMA | Kondisi motor prima |
| > 100–500 jam | 🔵 NORMAL | Kondisi motor normal |
| > 24–100 jam | 🟡 PERHATIAN | Siapkan perawatan atau servis |
| ≤ 24 jam | 🔴 KRITIS | Hentikan operasi dan lakukan pemeriksaan |

Klasifikasi tersebut merupakan ambang batas operasional yang ditentukan dalam program, bukan standar kerusakan universal untuk semua jenis motor induksi.

## 🏗️ Arsitektur Sistem

Sistem menyediakan dua jalur penggunaan:

### Mode A – Streamlit Langsung

Streamlit memanggil fungsi prediksi dari `src/predictor.py` dan memuat model secara langsung tanpa memerlukan server FastAPI terpisah.

```text
User
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
XGBoost Model
  |
  v
Hasil Prediksi RUL
```

### Mode B – Streamlit dengan FastAPI

Streamlit mengirimkan data sensor melalui HTTP Request menuju endpoint FastAPI. Backend kemudian melakukan prediksi menggunakan model yang sudah dimuat.

```text
User
  |
  v
Streamlit UI
  |
  v
HTTP POST Request
  |
  v
FastAPI (/predict)
  |
  v
Predictor
  |
  v
XGBoost Model
  |
  v
Hasil Prediksi RUL
```

## 📁 Struktur Proyek

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
│   ├── xgb_rul.json
│   ├── imputer_rul.joblib
│   └── metadata.json
│
├── tests/
│   └── smoke_test.py
│
├── train_rul_model.ipynb
├── requirements.txt
└── README.md
```

**Catatan:** File artefak model harus disesuaikan dengan hasil training yang tersedia. `model_rul.joblib` merupakan jalur pemuatan cadangan, sedangkan `xgb_rul.json` dan `imputer_rul.joblib` digunakan sebagai jalur pemuatan utama apabila keduanya tersedia.

## 📂 Penjelasan Komponen

| File / Folder | Fungsi |
|---|---|
| `app/api/main.py` | Menyediakan REST API menggunakan FastAPI, validasi input, dan endpoint prediksi. |
| `app/ui/streamlit_app.py` | Menyediakan antarmuka prediksi satuan dan batch CSV. |
| `src/features.py` | Mengelola fitur input dan membersihkan nilai negatif pada arus serta getaran menjadi NaN. |
| `src/predictor.py` | Memuat model, menjalankan preprocessing, prediksi RUL, klasifikasi kondisi, dan menghitung latency. |
| `artifacts/` | Menyimpan model, imputer, dan metadata model. |
| `tests/smoke_test.py` | Menguji endpoint API menggunakan skenario normal, ekstrem, dan input tidak valid. |
| `train_rul_model.ipynb` | Notebook untuk proses pelatihan dan pengembangan model. |
| `requirements.txt` | Daftar library dan dependensi yang dibutuhkan. |

## ⚙️ Konfigurasi Model

Berdasarkan metadata model, konfigurasi algoritma yang digunakan adalah:

| Parameter | Nilai |
|---|---|
| Algoritma | XGBRegressor |
| n_estimators | 300 |
| learning rate | 0.05 |
| max_depth | 5 |
| Imputasi | Median |
| Versi model | 1.0.0 |

Alur preprocessing model:

```text
Data Sensor
    |
    v
Pembersihan Data
    |
    v
Median Imputation
    |
    v
XGBoost Regressor
    |
    v
Prediksi RUL
```

Pembersihan data pada `features.py` mengubah nilai negatif pada arus dan getaran menjadi NaN. Nilai tersebut kemudian ditangani melalui median imputation pada jalur model.

## 🚀 Instalasi dan Menjalankan Program

### 1. Persyaratan Sistem

Pastikan perangkat sudah memiliki:

- Python 3.11–3.13.
- Visual Studio Code atau editor Python lainnya.
- Git (opsional, untuk cloning repository).

### 2. Clone Repository

```bash
git clone URL_REPOSITORY_KAMU
cd NAMA_FOLDER_PROJECT
```

### 3. Membuat Virtual Environment

```bash
python -m venv .venv
```

Aktifkan environment.

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows CMD:**

```cmd
.venv\Scripts\activate
```

**Mac / Linux:**

```bash
source .venv/bin/activate
```

### 4. Instalasi Dependencies

```bash
pip install -r requirements.txt
```

Pastikan file artefak model yang diperlukan tersedia di folder `artifacts/` sebelum menjalankan aplikasi.

## ▶️ Menjalankan Aplikasi

Terdapat dua pilihan untuk menjalankan aplikasi.

### Mode A – Streamlit Langsung

Mode ini menjalankan Streamlit dengan pemanggilan model secara langsung.

```bash
python -m streamlit run app/ui/streamlit_app.py
```

### Mode B – Streamlit dengan FastAPI

Mode ini memisahkan backend dan frontend menggunakan dua terminal.

**Terminal 1 – Menjalankan FastAPI**

```bash
python -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 – Menjalankan Streamlit**

Windows PowerShell:

```powershell
$env:API_URL="http://127.0.0.1:8000"
python -m streamlit run app/ui/streamlit_app.py
```

Windows CMD:

```cmd
set API_URL=http://127.0.0.1:8000
python -m streamlit run app/ui/streamlit_app.py
```

Mac / Linux:

```bash
export API_URL=http://127.0.0.1:8000
python -m streamlit run app/ui/streamlit_app.py
```

Jika `API_URL` tidak diatur, aplikasi menggunakan Mode A. Jika `API_URL` diatur, aplikasi menggunakan Mode B.

## 🌐 Akses Aplikasi

Setelah aplikasi berhasil dijalankan, akses melalui browser.

| Layanan | Alamat |
|---|---|
| Streamlit | http://localhost:8501 |
| FastAPI | http://127.0.0.1:8000 |
| Swagger API Documentation | http://127.0.0.1:8000/docs |
| API Health Check | http://127.0.0.1:8000/health |

## 🔌 Dokumentasi REST API

Backend menyediakan dua endpoint utama.

### 1. Health Check

**Endpoint:**

```http
GET /health
```

Digunakan untuk memeriksa status API dan pemuatan model.

Contoh respons:

```json
{
  "status": "ok",
  "model_loaded": true
}
```

### 2. Prediksi RUL

**Endpoint:**

```http
POST /predict
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

Batas validasi input:

| Parameter | Nilai Minimum | Nilai Maksimum |
|---|---:|---:|
| Arus | 0 A | 100 A |
| Getaran | 0 mm/s | 50 mm/s |
| Suhu body | 0 °C | 200 °C |
| Tegangan | 0 V | 500 V |

Contoh struktur respons:

```json
{
  "status": "success",
  "remaining_useful_life_hours": 350.25,
  "status": "NORMAL",
  "latency_ms": 12.5
}
```

Nilai di atas hanya ilustrasi format respons, bukan hasil prediksi aktual.

Input yang tidak memenuhi validasi akan mendapatkan HTTP 422 dari FastAPI.

## 📑 Fitur Aplikasi

### 1. Prediksi Satuan

Pengguna dapat memasukkan empat parameter sensor melalui formulir Streamlit untuk memperoleh estimasi sisa umur motor.

Hasil ditampilkan dalam bentuk:

- Estimasi RUL dalam jam.
- Kategori kondisi motor.
- Informasi waktu pemrosesan.
- Detail input dan output dalam format JSON.

### 2. Prediksi Batch CSV

Aplikasi menyediakan fitur unggah CSV untuk melakukan prediksi terhadap beberapa baris data sekaligus.

Kolom yang wajib tersedia:

```csv
arus_ampere,getaran_mm_s,suhu_body_c,tegangan_volt
12.5,2.1,45,220
15.0,3.2,50,215
20.0,5.5,65,210
```

Hasil prediksi ditambahkan pada kolom:

```text
prediksi_rul_jam
```

**Catatan teknis:** Implementasi prediksi batch saat ini menggunakan model lokal melalui Streamlit, termasuk ketika aplikasi satuan menggunakan Mode B. Kolom CSV yang diperiksa adalah keberadaan empat fitur wajib.

## 🧪 Pengujian Program

Pengujian awal dilakukan menggunakan `tests/smoke_test.py`.

Jalankan dari root repository:

```bash
python -m tests.smoke_test
```

Skenario pengujian:

| Skenario | Input | Tujuan |
|---|---|---|
| Normal | Data sensor normal | Memeriksa prediksi pada input valid |
| Ekstrem | Data sensor bernilai tinggi | Memeriksa input valid pada nilai ekstrem |
| Invalid | Arus bernilai negatif | Memeriksa penolakan validasi API |

Pengujian menggunakan `TestClient` dari FastAPI untuk mengirimkan request ke endpoint `/health` dan `/predict`.

## 🔄 Training dan Pengembangan Model

Proses pelatihan model tersedia dalam notebook:

```text
train_rul_model.ipynb
```

Buka notebook menggunakan Visual Studio Code atau Jupyter Notebook untuk menjalankan tahapan pengembangan model.

Konfigurasi algoritma yang tercantum dalam metadata adalah XGBoost Regressor dengan 300 estimator, learning rate 0.05, dan max depth 5.

Artefak model yang digunakan aplikasi:

- `xgb_rul.json`: model XGBoost dalam format JSON.
- `imputer_rul.joblib`: objek median imputer.
- `model_rul.joblib`: model cadangan dalam format Joblib.

## 📦 Dependencies

Daftar dependensi utama berdasarkan `requirements.txt`:

```text
fastapi==0.115.4
uvicorn==0.32.0
streamlit==1.40.0
scikit-learn==1.6.1
xgboost-cpu==3.4.1
pandas==2.2.3
pydantic==2.9.2
joblib>=1.4
numpy<2.3
requests>=2.31
httpx>=0.27
```

## ⚠️ Catatan dan Batasan

- Prediksi RUL merupakan estimasi berdasarkan model dan data yang digunakan saat pelatihan.
- Hasil prediksi tidak menjamin waktu kerusakan aktual motor.
- Kualitas prediksi bergantung pada kualitas dan representativitas dataset training.
- Metrik evaluasi MAE, RMSE, dan R² belum dicantumkan karena metadata yang tersedia masih berisi placeholder.
- Ambang kategori kondisi motor merupakan aturan klasifikasi pada aplikasi, bukan standar industri universal.
- Aplikasi membutuhkan artefak model yang sesuai agar proses prediksi dapat berjalan.

---

## 👨‍💻 Pengembang

| Informasi | Keterangan |
|---|---|
| Nama | Iqbal Ianudin & Muhammad Haikal Alfaridzi |
| NIM | 2403141 & 2407942 |
| Mata Kuliah | MKB |
| Proyek | Predictive Maintenance – RUL Motor Induksi |

---

<p align="center">
  <b>Predictive Maintenance – Remaining Useful Life Prediction</b>
  <br>
  Developed using Python, XGBoost, FastAPI, and Streamlit.
</p>
