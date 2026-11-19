<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/TensorFlow-2.12+-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white" />
  <img src="https://img.shields.io/badge/Ollama-LLM-black?style=for-the-badge" />
</p>

# ✈️ AeroReason — Hybrid AI Predictive Maintenance Framework

> End-to-end predictive maintenance system for aircraft turbofan engines using the **NASA C-MAPSS** dataset. Combines **deep learning (LSTM)** for numerical RUL prediction with a **rule-based + LLM reasoning engine** for context-aware, human-readable maintenance insights.

---

## 🎯 Key Features

- **RUL Prediction** — Predicts Remaining Useful Life (in cycles) for each engine using a 2-layer LSTM model.
- **Risk Classification** — Automatically classifies engines as `CRITICAL`, `MODERATE`, or `LOW` risk.
- **AI-Powered Insights** — Generates actionable maintenance recommendations using rule-based heuristics + optional local LLM (Ollama/llama3).
- **Fleet Monitoring Dashboard** — Interactive web UI for fleet-wide and per-engine health monitoring.
- **Sensor Trend Analysis** — Detects degrading sensors via linear regression slope analysis.
- **Custom Data Upload** — Upload your own CSV sensor data for real-time RUL inference.
- **Multi-Dataset Support** — Supports all four NASA C-MAPSS sub-datasets (FD001–FD004) with per-dataset trained models.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React / Vite Frontend                │
│         (Dark-mode cinematic dashboard @ :5173)         │
├─────────────────────────────────────────────────────────┤
│                     FastAPI Backend                     │
│              (REST API server @ :8000)                  │
├──────────┬──────────────┬───────────────────────────────┤
│   LSTM   │  Reasoning   │     Ollama LLM (optional)    │
│  Model   │   Engine     │       llama3 @ :11434        │
└──────────┴──────────────┴───────────────────────────────┘
```

---

## 📁 Project Structure

```
AeroReason/
├── api_server.py              # FastAPI REST API (6 endpoints)
├── main.py                    # CLI training & evaluation pipeline
├── requirements.txt           # Python dependencies
├── run.sh / stop.sh           # One-click start/stop scripts
│
├── preprocessing/
│   └── data_loader.py         # Data loading, RUL labeling, normalization, windowing
│
├── models/
│   └── lstm_model.py          # LSTM model definition, training, save/load
│
├── reasoning/
│   ├── reasoning_engine.py    # Rule-based risk classification & insights
│   └── ollama_engine.py       # LLM integration via Ollama
│
├── utils/
│   └── helpers.py             # Plotting utilities (CLI mode)
│
├── data/                      # Trained models (.keras) & scaler (.joblib)
├── Research/                  # NASA C-MAPSS datasets & research notebook
│
└── frontend/                  # React 18 + Vite 5 dashboard
    └── src/
        ├── pages/             # Home, FleetOverview, EngineAnalysis,
        │                      # ModelPerformance, PredictData
        └── components/        # Navbar, MetricCard, RiskBadge, InsightCard, etc.
```

---

## 🚀 Quick Start

### Prerequisites

| Requirement    | Version  | Note                              |
| -------------- | -------- | --------------------------------- |
| Python         | 3.10+    | Required                          |
| Node.js        | 18+      | Required (with npm)               |
| Ollama         | Latest   | Optional — for AI-powered insights |

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/JathinKodali/AeroReason.git
cd AeroReason

# 2. Create Python virtual environment & install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Install frontend dependencies
cd frontend && npm install && cd ..

# 4. (Optional) Start Ollama for LLM-powered insights
ollama serve
ollama pull llama3
```

### Run

```bash
# One-click launcher (starts both backend & frontend)
bash run.sh

# Or manually:
# Terminal 1 — Backend
source venv/bin/activate
TF_ENABLE_ONEDNN_OPTS=0 python -m uvicorn api_server:app --port 8000 --host 0.0.0.0

# Terminal 2 — Frontend
cd frontend && npx vite --host
```

### Access

| Service           | URL                          |
| ----------------- | ---------------------------- |
| Web Dashboard     | http://localhost:5173         |
| API Swagger Docs  | http://localhost:8000/docs    |

### Stop

```bash
bash stop.sh
```

---

## 🧠 LSTM Model

| Parameter         | Value                              |
| ----------------- | ---------------------------------- |
| Architecture      | LSTM(128) → Dropout(0.2) → LSTM(64) → Dropout(0.2) → Dense(32) → Dense(1) |
| Optimizer         | Adam (lr=0.001)                    |
| Loss              | Mean Squared Error                 |
| Epochs            | 50 (early stopping, patience=10)   |
| Batch Size        | 256                                |
| Window Size       | 30 cycles (configurable)           |
| RUL Cap           | 125 cycles (piecewise linear)      |
| Features          | 16 sensors/settings (7 dropped)    |

### CLI Training

```bash
python main.py                     # Train on FD001 (default)
python main.py --dataset FD003     # Train on a different sub-dataset
python main.py --load              # Evaluate with existing model
python main.py --epochs 100        # Custom training epochs
```

---

## 🔮 Reasoning Engine

| Risk Level   | RUL Threshold | Action                                   |
| ------------ | ------------- | ---------------------------------------- |
| 🟢 LOW       | > 100 cycles  | Continue routine monitoring               |
| 🟡 MODERATE  | 50–100 cycles | Schedule inspection in 20–30 cycles       |
| 🔴 CRITICAL  | ≤ 50 cycles   | Ground engine, initiate replacement       |

When **Ollama** is enabled, the reasoning engine generates richer, context-aware explanations using the **llama3** model. Falls back gracefully to rule-based templates if Ollama is unavailable.

---

## 📡 API Endpoints

| Method | Endpoint              | Description                         |
| ------ | --------------------- | ----------------------------------- |
| GET    | `/api/datasets`       | List available sub-datasets         |
| GET    | `/api/model/status`   | Check if trained model exists       |
| GET    | `/api/ollama/status`  | Check Ollama availability & models  |
| GET    | `/api/predictions`    | Fleet-wide RUL predictions & stats  |
| GET    | `/api/engine/{id}`    | Single engine detailed analysis     |
| GET    | `/api/performance`    | Model accuracy metrics & chart data |
| POST   | `/api/predict/upload` | Upload CSV for custom predictions   |

---

## 📊 NASA C-MAPSS Dataset

| Sub-dataset | Train Engines | Test Engines | Op. Conditions | Fault Modes      |
| ----------- | ------------- | ------------ | -------------- | ---------------- |
| FD001       | 100           | 100          | 1              | 1 (HPC)          |
| FD002       | 260           | 259          | 6              | 1 (HPC)          |
| FD003       | 100           | 100          | 1              | 2 (HPC + Fan)    |
| FD004       | 249           | 248          | 6              | 2 (HPC + Fan)    |

> Source: [NASA Prognostics Center of Excellence](https://data.nasa.gov/dataset/C-MAPSS-Aircraft-Engine-Simulator-Data)

---

## 🛠️ Tech Stack

**Backend:** Python · FastAPI · TensorFlow/Keras · Scikit-learn · Pandas · NumPy · Ollama  
**Frontend:** React 18 · Vite 5 · React Router · Recharts · Framer Motion · Lucide Icons  
**Infrastructure:** Bash scripts · Python venv · Node.js/npm

---

## 📄 License

This project was developed as an academic minor project.

---


## Windows / VS Code local setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-local.txt
cd frontend
npm.cmd ci
cd ..
code .
```

In VS Code select **Terminal > Run Task > AeroReason: Run All** to start both services.
Open http://localhost:5173 for the dashboard and http://localhost:8000/docs for the API.
Stop both running tasks with **Terminal > Terminate Task** before restarting them.
The Python interpreter is configured to use the project-local `.venv` environment.
Ollama is optional; the app falls back to rule-based insights when it is unavailable.

## Render deployment

The root `render.yaml` creates one Docker web service serving the React build
and FastAPI API from the same origin. Production browser requests use relative
API URLs; local Vite development still uses http://localhost:8000.

Push this project to a Git repository you control, then create a Render Blueprint
from that repository. Use the root Dockerfile. The service listens on Render's
`PORT` (10000 in the Blueprint), with `/api/model/status` as its health check.
The image installs `requirements-deploy.txt` and runs the bundled trained models;
it does not train during deployment. No environment secrets are required.

The Blueprint retains the existing free plan. TensorFlow and cached datasets may
exceed its memory limit; verify prediction requests after deployment. Upgrade
only after reviewing and approving the hosting cost. Ollama is not included in
this container, so explanations use the existing rule-based fallback.

Deployment verification: visit `/`, `/fleet`, `/docs`, `/api/model/status`, and
`/api/predictions?dataset=FD001&window=30`. A working landing page alone does not
verify model inference. Docker is not installed on the local setup, so the full
Linux image build must be verified by Render's build logs.

To repeat the local combined-service smoke tests after a frontend change:

```powershell
npm.cmd --prefix frontend run build
New-Item -ItemType Directory -Path static -Force | Out-Null
Copy-Item frontend\dist\* static -Recurse -Force
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

These checks verify the built dashboard, static assets, client-side routes,
API documentation, model health, missing API routes, and FD001 inference.
They do not replace a successful Docker build and live Render inference check.
