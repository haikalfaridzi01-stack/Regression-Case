import logging

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.predictor import load_model, predict_rul

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("rul-api")

app = FastAPI(title="API RUL Motor Induksi", version="1.0.0")
model = load_model()  # dimuat sekali saat startup


class SensorMotor(BaseModel):
    arus_ampere: float = Field(ge=0, le=100, description="Arus (A)")
    getaran_mm_s: float = Field(ge=0, le=50, description="Getaran (mm/s)")
    suhu_body_c: float = Field(ge=0, le=200, description="Suhu body (°C)")
    tegangan_volt: float = Field(ge=0, le=500, description="Tegangan (V)")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
def predict(data: SensorMotor):
    hasil = predict_rul(model, data.model_dump())
    log.info("input=%s output=%s", data.model_dump(), hasil)
    return {"status": "success", **hasil}
