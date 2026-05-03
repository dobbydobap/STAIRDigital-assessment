FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PDFAGENT_DATA_DIR=/data \
    HF_HOME=/data/.hfcache

# System deps for PyMuPDF, ChromaDB, rapidocr (onnxruntime).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the whole project first; simpler than splitting deps from source and
# guarantees `pip install -e .` finds the pdfagent package layout.
COPY . .

# Install deps + the editable package in one shot.
RUN pip install --upgrade pip && pip install -e .

# Pre-download bge-m3 weights so cold start on the live demo isn't 2-3 min.
RUN python -c "from FlagEmbedding import BGEM3FlagModel; BGEM3FlagModel('BAAI/bge-m3', use_fp16=False)"

# HF Spaces gives a writable /data; create the dirs the app expects.
RUN mkdir -p /data/chroma /data/traces /data/uploads /data/page_images /data/pdfs

EXPOSE 8501

# Streamlit on 8501 (matches `app_port: 8501` in README front matter).
CMD ["streamlit", "run", "pdfagent/ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]
