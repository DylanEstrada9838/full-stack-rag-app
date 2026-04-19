# ── Backend Dockerfile ──────────────────────────────────────────────────────
# Multi-stage is not needed here; we just need Python + our packages.
# ---------------------------------------------------------------------------

FROM python:3.11-slim

# Keeps Python from buffering stdout/stderr (important for Docker logs)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONIOENCODING=utf-8

# Where Ollama is running inside the Docker network
# (overridable via docker-compose environment section)
ENV OLLAMA_HOST=http://ollama:11434

WORKDIR /app

# Install system deps needed by some Python packages (e.g. PyMuPDF, chromadb)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full backend source
COPY . .

# Install local package
RUN pip install -e .

# Expose FastAPI port
EXPOSE 8000

# Healthcheck is defined in docker-compose.yml

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
