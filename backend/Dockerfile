# ================================
# 🏗️ Stage 1: Base setup
# ================================
FROM python:3.11-slim AS base

# Prevent Python from writing pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install essential dependencies (for building some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl \
    && rm -rf /var/lib/apt/lists/*

# ================================
# 👤 Create non-root user
# ================================
RUN useradd -m appuser
USER appuser

# ================================
# 📦 Install Python dependencies
# ================================
# Copy requirements first to leverage Docker layer caching
COPY --chown=appuser:appuser requirements.txt .

# Create a virtual environment and install dependencies
RUN python -m venv /home/appuser/venv && \
    . /home/appuser/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ================================
# 🚀 Copy application code
# ================================
COPY --chown=appuser:appuser app ./app

# ================================
# ⚙️ Environment variables
# ================================
ENV PATH="/home/appuser/venv/bin:$PATH"
ENV PORT=8000
ENV HOST=0.0.0.0
ENV APP_MODULE=app.main:app

# ================================
# 🌐 Expose and run with Gunicorn
# ================================
EXPOSE 8000

# Use Gunicorn with Uvicorn workers (optimized for FastAPI)
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "app.main:app"]
