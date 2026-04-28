# ---- Stage 1: Build React frontend ----
FROM node:18-slim AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci --production=false
COPY frontend/ .
# Replace hardcoded localhost URL with empty string so API calls become
# relative (same-origin) — only affects this build, not the source code.
RUN sed -i 's|http://localhost:8000||g' src/App.jsx && npm run build

# ---- Stage 2: Python backend + static frontend ----
FROM python:3.12-slim
WORKDIR /app

# Install Python dependencies (use tensorflow-cpu for smaller image)
COPY requirements.txt .
RUN sed -i 's/tensorflow>=2.12.0/tensorflow-cpu/g' requirements.txt \
    && pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY api_server.py main.py deploy_server.py ./
COPY preprocessing/ preprocessing/
COPY models/ models/
COPY reasoning/ reasoning/
COPY utils/ utils/
COPY data/ data/
COPY Research/ Research/
COPY sample_engine_data.csv .

# Copy frontend build output into /app/static
COPY --from=frontend /build/dist ./static

ENV TF_ENABLE_ONEDNN_OPTS=0

# Render injects $PORT; default to 8000 for local Docker runs
CMD uvicorn deploy_server:app --host 0.0.0.0 --port ${PORT:-8000}
