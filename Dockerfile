FROM node:22-slim AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.13-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    TF_ENABLE_ONEDNN_OPTS=0 \
    TF_NUM_INTRAOP_THREADS=1 \
    TF_NUM_INTEROP_THREADS=1 \
    OMP_NUM_THREADS=1
COPY requirements-deploy.txt ./
RUN pip install --no-cache-dir -r requirements-deploy.txt
COPY api_server.py deploy_server.py ./
COPY preprocessing/ preprocessing/
COPY models/ models/
COPY reasoning/ reasoning/
COPY data/ data/
COPY Research/ Research/
COPY sample_engine_data.csv ./
COPY --from=frontend /build/dist ./static
EXPOSE 10000
CMD ["python", "deploy_server.py"]
