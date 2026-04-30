FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PDFAGENT_DATA_DIR=/data

# System deps for PyMuPDF, ChromaDB, rapidocr (onnxruntime), torch (CPU).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first for better layer caching.
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install -e .

COPY pdfagent ./pdfagent
COPY eval ./eval
COPY .streamlit ./.streamlit

# Pre-download bge-m3 so cold start in production isn't 2 minutes long.
# Comment out for a smaller image (~3 GB savings) if you'd rather pay the cost on first request.
RUN python -c "from FlagEmbedding import BGEM3FlagModel; BGEM3FlagModel('BAAI/bge-m3', use_fp16=False)"

RUN mkdir -p /data/chroma /data/traces /data/uploads /data/page_images /data/pdfs

EXPOSE 8000 8501

# By default we run the Streamlit UI (it imports pdfagent.service directly,
# so no separate API process is required). To run the FastAPI surface instead:
#   docker run … pdfagent uvicorn pdfagent.api.app:app --host 0.0.0.0 --port 8000
CMD ["streamlit", "run", "pdfagent/ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
