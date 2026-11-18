# Predictive Maintenance: RUL Motor Induksi

Regresi XGBoost untuk memperkirakan Remaining Useful Life (jam) motor induksi dari 4 sensor:
arus (A), getaran (mm/s), suhu body (°C), tegangan (V).

## Struktur
```
app/api/main.py        FastAPI (/health, /predict, /docs)
app/ui/streamlit_app.py  UI Streamlit (Mode A langsung / Mode B via API)
src/features.py        bersihkan_data + daftar fitur
src/predictor.py       load model + prediksi (dipakai API & UI)
artifacts/             model_rul.joblib + metadata.json
tests/smoke_test.py    uji normal / ekstrem / invalid
train_model.py         latih ulang dari CSV
```

## Menjalankan (VS Code terminal, dari root folder)
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   |  source .venv/bin/activate (Mac/Linux)
pip install -r requirements.txt

# Mode A (satu proses, = deploy Streamlit Cloud)
python -m streamlit run app/ui/streamlit_app.py

# Mode B (dua terminal)
python -m uvicorn app.api.main:app --port 8000          # terminal 1
set API_URL=http://127.0.0.1:8000                        # terminal 2 (PowerShell: $env:API_URL="...")
python -m streamlit run app/ui/streamlit_app.py

python -m tests.smoke_test      # uji cepat
```
Gunakan Python 3.11–3.13.

## Pengembang
Nama: Iqbal Ianudin · NIM: [isi] · Mata kuliah: MKB
