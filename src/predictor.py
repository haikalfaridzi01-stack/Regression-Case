"""Loader model + fungsi prediksi (satu sumber kebenaran untuk API & UI)."""
import sys
import time
from pathlib import Path

import joblib
import pandas as pd

from src.features import FITUR_INPUT, bersihkan_data

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "artifacts" / "model_rul.joblib"


class RULModel:
    """Model portabel: cleaning -> imputer (median) -> XGBoost (format JSON).

    Format JSON/joblib-imputer lintas platform, tidak bergantung pada format
    pickle internal XGBoost yang bisa gagal dibaca di mesin/versi lain.
    """

    def __init__(self, imputer, booster):
        self.imputer = imputer
        self.booster = booster

    def predict(self, df):
        import numpy as np
        import xgboost as xgb

        x = self.imputer.transform(bersihkan_data(df[FITUR_INPUT]))
        return self.booster.predict(xgb.DMatrix(np.asarray(x, dtype="float32")))


def load_model(path: Path = MODEL_PATH):
    json_path = ROOT / "artifacts" / "xgb_rul.json"
    imp_path = ROOT / "artifacts" / "imputer_rul.joblib"
    if json_path.exists() and imp_path.exists():
        import xgboost as xgb

        booster = xgb.Booster()
        booster.load_model(str(json_path))
        return RULModel(joblib.load(imp_path), booster)

    # Cadangan: pipeline pickle asli. Fungsi bersihkan_data tersimpan sebagai
    # '__main__.bersihkan_data', jadi daftarkan ke __main__ agar bisa dibaca.
    main = sys.modules["__main__"]
    if not hasattr(main, "bersihkan_data"):
        setattr(main, "bersihkan_data", bersihkan_data)
    return joblib.load(path)


def status_dari_rul(rul: float) -> str:
    if rul > 500:
        return "PRIMA"
    if rul > 100:
        return "NORMAL"
    if rul > 24:
        return "PERHATIAN"
    return "KRITIS"


def predict_rul(model, data: dict) -> dict:
    t0 = time.perf_counter()
    df = pd.DataFrame([data])[FITUR_INPUT]
    rul = max(0.0, float(model.predict(df)[0]))
    return {
        "remaining_useful_life_hours": round(rul, 2),
        "status": status_dari_rul(rul),
        "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
    }
