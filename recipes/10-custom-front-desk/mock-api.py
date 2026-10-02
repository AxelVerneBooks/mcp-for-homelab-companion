#!/usr/bin/env python3
"""Mock pool-controller API for Recipe 10 — stands in for the vendor's
cloud API so the front desk works out of the box. Two routes, matching
server.py: GET /status, GET /sensors."""

import random

from fastapi import FastAPI

app = FastAPI(title="Mock Pool Controller")

MODES = ("auto", "low", "high")


@app.get("/status")
def status() -> dict:
    return {
        "water_temp_c": round(random.uniform(26.0, 29.5), 1),
        "heater": random.choice(("on", "off")),
        "pump_mode": random.choice(MODES),
        "filter_pressure_psi": round(random.uniform(8.0, 14.0), 1),
    }


@app.get("/sensors")
def sensors() -> list[dict]:
    return [
        {"id": "water", "name": "Water temp", "c": round(random.uniform(26.0, 29.5), 1)},
        {"id": "solar", "name": "Solar intake", "c": round(random.uniform(24.0, 34.0), 1)},
        {"id": "ambient", "name": "Ambient", "c": round(random.uniform(15.0, 32.0), 1)},
    ]
