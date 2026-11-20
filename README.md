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
