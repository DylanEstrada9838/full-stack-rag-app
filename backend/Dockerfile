# ── Backend Dockerfile ──────────────────────────────────────────────────────
# Multi-stage is not needed here; we just need Python + our packages.
# ---------------------------------------------------------------------------

FROM python:3.11-slim

# Keeps Python from buffering stdout/stderr (important for Docker logs)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8 \
    MALLOC_ARENA_MAX=2 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1

WORKDIR /app

# Install system deps needed by some Python packages (e.g. PyMuPDF, chromadb)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch first (drastically reduces package size and RAM usage)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full backend source
COPY . .

# Install local package
RUN pip install -e .

# Pre-build vectorstore and cache model during Docker build (uses builder RAM, not runtime 512MB)
RUN python rebuild_db.py

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI app with a single worker
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
