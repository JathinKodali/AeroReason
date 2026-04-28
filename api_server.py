"""
FastAPI Backend for the Predictive Maintenance Framework.
Wraps existing Python ML/reasoning modules as REST endpoints.
"""

import os
import sys
import io
import numpy as np
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from preprocessing.data_loader import (
    load_data, add_rul_labels, add_test_rul, normalize_features,
    create_test_sequences, FEATURES, SENSOR_COLS, ALL_COLS, RUL_CAP,
    save_scaler, load_scaler, normalize_with_scaler,
)
from models.lstm_model import load_trained_model
from reasoning.reasoning_engine import reason, classify_risk
from reasoning.ollama_engine import is_ollama_available, get_available_models

app = FastAPI(title="AeroReason API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(PROJECT_ROOT, "Research")
MODEL_DIR = os.path.join(PROJECT_ROOT, "data")
SCALER_PATH = os.path.join(PROJECT_ROOT, "data", "scaler.joblib")


def _model_path(dataset_id):
    """Return the path to the per-dataset model, falling back to the generic one."""
    per_ds = os.path.join(MODEL_DIR, f"trained_model_{dataset_id}.keras")
    if os.path.exists(per_ds):
        return per_ds
    return os.path.join(MODEL_DIR, "trained_model.keras")

_cache = {}


def _get_dataset(dataset_id, window_size):
    key = f"{dataset_id}_{window_size}"
    if key not in _cache:
        train_df, test_df, rul_df = load_data(DATA_DIR, dataset_id)
        train_df = add_rul_labels(train_df)
        test_df = add_test_rul(test_df, rul_df)
        train_df, test_df, scaler = normalize_features(train_df, test_df)
        save_scaler(scaler, SCALER_PATH)
        _cache[key] = (train_df, test_df, scaler)
    return _cache[key]


def _get_predictions(dataset_id, window_size):
    pred_key = f"pred_{dataset_id}_{window_size}"
    if pred_key not in _cache:
        _, test_df, _ = _get_dataset(dataset_id, window_size)
        mp = _model_path(dataset_id)
        model = load_trained_model(mp)
        X_test, y_test_norm, engine_ids = create_test_sequences(test_df, window_size)
        y_test_norm = y_test_norm / RUL_CAP
        y_pred_norm = model.predict(X_test).flatten()
        y_pred = y_pred_norm * RUL_CAP
        y_test = y_test_norm * RUL_CAP
        rmse = float(np.sqrt(np.mean((y_test - y_pred) ** 2)))
        _cache[pred_key] = {
            "y_pred": y_pred, "y_test": y_test,
            "engine_ids": engine_ids, "rmse": rmse,
        }
    return _cache[pred_key]


@app.get("/api/datasets")
def list_datasets():
    return {"datasets": ["FD001", "FD002", "FD003", "FD004"]}


@app.get("/api/model/status")
def model_status():
    return {"model_exists": any(
        os.path.exists(os.path.join(MODEL_DIR, f"trained_model_{d}.keras"))
        for d in ["FD001", "FD002", "FD003", "FD004"]
    )}


@app.get("/api/ollama/status")
def ollama_status():
    online = is_ollama_available()
    models = get_available_models() if online else []
    return {"online": online, "models": models}


@app.get("/api/predictions")
def get_predictions(dataset: str = Query("FD001"), window: int = Query(30)):
    if not os.path.exists(_model_path(dataset)):
        return JSONResponse(status_code=400, content={"error": "No trained model"})
    preds = _get_predictions(dataset, window)
    y_pred, y_test, engine_ids = preds["y_pred"], preds["y_test"], preds["engine_ids"]
    risk_labels = [classify_risk(r)[0] for r in y_pred]
    fleet = []
    for i, eid in enumerate(engine_ids):
        fleet.append({
            "engine_id": int(eid),
            "predicted_rul": round(float(y_pred[i]), 1),
            "actual_rul": round(float(y_test[i]), 1),
            "error": round(float(y_test[i] - y_pred[i]), 1),
            "risk_level": risk_labels[i],
        })
    return {
        "rmse": preds["rmse"],
        "total_engines": len(engine_ids),
        "critical": risk_labels.count("CRITICAL"),
        "moderate": risk_labels.count("MODERATE"),
        "low": risk_labels.count("LOW"),
        "fleet": fleet,
    }


@app.get("/api/engine/{engine_id}")
def get_engine_analysis(engine_id: int, dataset: str = Query("FD001"),
                        window: int = Query(30), use_llm: bool = Query(False),
                        llm_model: str = Query("llama3")):
    if not os.path.exists(_model_path(dataset)):
        return JSONResponse(status_code=400, content={"error": "No trained model"})
    preds = _get_predictions(dataset, window)
    _, test_df, _ = _get_dataset(dataset, window)
    engine_ids = preds["engine_ids"]
    if engine_id not in engine_ids:
        return JSONResponse(status_code=404, content={"error": "Engine not found"})
    idx = engine_ids.index(engine_id)
    pred_rul = float(preds["y_pred"][idx])
    actual_rul = float(preds["y_test"][idx])
    engine_data = test_df[test_df["engine_id"] == engine_id]
    sensor_features = [c for c in SENSOR_COLS if c in engine_data.columns]
    insight = reason(engine_id, pred_rul, engine_data, sensor_features,
                     use_llm=use_llm, llm_model=llm_model)
    available_sensors = [
        c for c in SENSOR_COLS
        if c not in ["sensor_1","sensor_5","sensor_6","sensor_10",
                      "sensor_16","sensor_18","sensor_19"]
        and c in engine_data.columns
    ]
    sensor_data = {}
    for s in available_sensors:
        sensor_data[s] = {
            "cycles": engine_data["cycle"].tolist(),
            "values": engine_data[s].tolist(),
        }
    return {
        "engine_id": engine_id,
        "predicted_rul": round(pred_rul, 1),
        "actual_rul": round(actual_rul, 1),
        "risk_level": insight.risk_level,
        "risk_color": insight.risk_color,
        "explanation": insight.explanation,
        "recommendation": insight.recommendation,
        "trend_summary": insight.trend_summary,
        "sensors": available_sensors,
        "sensor_data": sensor_data,
    }


@app.get("/api/performance")
def get_performance(dataset: str = Query("FD001"), window: int = Query(30)):
    if not os.path.exists(_model_path(dataset)):
        return JSONResponse(status_code=400, content={"error": "No trained model"})
    preds = _get_predictions(dataset, window)
    y_pred, y_test = preds["y_pred"], preds["y_test"]
    errors = y_test - y_pred
    hist, bin_edges = np.histogram(errors, bins=30)
    return {
        "rmse": preds["rmse"],
        "mean_error": round(float(np.mean(errors)), 2),
        "std_error": round(float(np.std(errors)), 2),
        "engines_tested": len(preds["engine_ids"]),
        "scatter": {
            "actual": [round(float(v), 1) for v in y_test],
            "predicted": [round(float(v), 1) for v in y_pred],
        },
        "histogram": {
            "counts": hist.tolist(),
            "bins": [round(float(b), 1) for b in bin_edges],
        },
    }


@app.post("/api/predict/upload")
async def predict_upload(file: UploadFile = File(...), window: int = Query(30),
                         use_llm: bool = Query(False), llm_model: str = Query("llama3")):
    mp = _model_path("FD001")  # fallback for uploads
    if not os.path.exists(mp):
        return JSONResponse(status_code=400, content={"error": "No trained model"})
    contents = await file.read()
    user_df = pd.read_csv(io.BytesIO(contents))
    required = {"engine_id", "cycle"}
    missing = required - set(user_df.columns)
    if missing:
        return JSONResponse(status_code=400, content={"error": f"Missing columns: {', '.join(missing)}"})
    avail_features = [f for f in FEATURES if f in user_df.columns]
    if len(avail_features) < 5:
        return JSONResponse(status_code=400, content={"error": f"Only {len(avail_features)} sensor columns found"})
    if os.path.exists(SCALER_PATH):
        scaler = load_scaler(SCALER_PATH)
    else:
        _, _, scaler = _get_dataset("FD001", window)
    user_df_norm = normalize_with_scaler(user_df.copy(), scaler, avail_features)
    model = load_trained_model(mp)
    sequences, _, user_engine_ids = create_test_sequences(user_df_norm, window, features=avail_features)
    y_pred_norm = model.predict(sequences).flatten()
    y_pred_user = y_pred_norm * RUL_CAP
    results = []
    for i, eid in enumerate(user_engine_ids):
        pred = float(y_pred_user[i])
        eng_data = user_df_norm[user_df_norm["engine_id"] == eid]
        sensor_f = [c for c in SENSOR_COLS if c in eng_data.columns]
        ins = reason(eid, pred, eng_data, sensor_f, use_llm=use_llm, llm_model=llm_model)
        results.append({
            "engine_id": int(eid), "predicted_rul": round(pred, 1),
            "risk_level": ins.risk_level, "explanation": ins.explanation,
            "recommendation": ins.recommendation, "trend_summary": ins.trend_summary,
        })
    risk_labels = [r["risk_level"] for r in results]
    return {
        "total_engines": len(user_engine_ids),
        "avg_rul": round(float(np.mean(y_pred_user)), 1),
        "critical": risk_labels.count("CRITICAL"),
        "moderate": risk_labels.count("MODERATE"),
        "low": risk_labels.count("LOW"),
        "features_detected": len(avail_features),
        "rows_loaded": len(user_df),
        "results": results,
    }
