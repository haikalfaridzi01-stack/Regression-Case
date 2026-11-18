"""Latih ulang model RUL dari data/dataset_motor_induksi_rul.csv.

Jalankan dari root repo:  python train_model.py
Output default ke artifacts/model_rul_retrained.joblib supaya model asli tidak tertimpa.
"""
import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
import xgboost
from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from xgboost import XGBRegressor

import __main__
from src.features import FITUR_INPUT, bersihkan_data

# Agar pickle merujuk ke fungsi yang bisa diimpor, bukan '__main__'
bersihkan_data.__module__ = "src.features"

ap = argparse.ArgumentParser()
ap.add_argument("--data", default="data/dataset_motor_induksi_rul.csv")
ap.add_argument("--out", default="artifacts/model_rul_retrained.joblib")
args = ap.parse_args()

df = pd.read_csv(args.data)
X, y = df[FITUR_INPUT], df["sisa_umur_jam"]
if len(df) < 50:
    print(f"PERINGATAN: hanya {len(df)} baris. Metrik tidak bermakna; pakai dataset penuh.", file=sys.stderr)

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

pipe = Pipeline([
    ("cleaning", FunctionTransformer(bersihkan_data)),
    ("imputer", SimpleImputer(strategy="median")),
    ("model", XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=5, random_state=42)),
])
pipe.fit(X_tr, y_tr)

base = Pipeline([("imputer", SimpleImputer(strategy="median")), ("m", DummyRegressor(strategy="mean"))]).fit(X_tr, y_tr)
metrik = {
    "mae_model": float(mean_absolute_error(y_te, pipe.predict(X_te))),
    "mae_baseline": float(mean_absolute_error(y_te, base.predict(X_te))),
    "r2_model": float(r2_score(y_te, pipe.predict(X_te))) if len(y_te) > 1 else None,
    "n_train": len(X_tr), "n_test": len(X_te),
}
print(metrik)

out = Path(args.out)
out.parent.mkdir(exist_ok=True)
joblib.dump(pipe, out)
meta = {
    "versi_model": "1.0.0",
    "fitur_input": FITUR_INPUT,
    "target": "sisa_umur_jam",
    "metrik_test": metrik,
    "library": {"scikit-learn": sklearn.__version__, "xgboost": xgboost.__version__,
                "pandas": pd.__version__, "numpy": np.__version__},
}
(out.with_suffix(".metadata.json")).write_text(json.dumps(meta, indent=2))
print("Tersimpan:", out)
