"""Smoke test: normal, ekstrem, invalid. Jalankan: python -m tests.smoke_test"""
from fastapi.testclient import TestClient
from app.api.main import app

c = TestClient(app)
normal = dict(arus_ampere=12.5, getaran_mm_s=2.1, suhu_body_c=45, tegangan_volt=220)
ekstrem = dict(arus_ampere=20, getaran_mm_s=12, suhu_body_c=95, tegangan_volt=200)
invalid = dict(arus_ampere=-5, getaran_mm_s=2.1, suhu_body_c=45, tegangan_volt=220)

print("health ", c.get("/health").json())
for nama, p in [("normal", normal), ("ekstrem", ekstrem), ("invalid", invalid)]:
    r = c.post("/predict", json=p)
    print(nama, r.status_code, r.json() if r.status_code == 200 else r.json()["detail"][0]["msg"])
