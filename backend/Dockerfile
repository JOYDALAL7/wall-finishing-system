# ================================
# 🏗️ Stage 1: Base setup
# ================================
FROM python:3.11-slim

# Prevent Python from writing pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install essential dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl && \
    rm -rf /var/lib/apt/lists/*

# ================================
# 👤 Create non-root user
# ================================
RUN useradd -m appuser

# ================================
# 📦 Install Python dependencies
# ================================
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ================================
# 🚀 Copy application code
# ================================
COPY app ./app

# ✅ Fix: Set correct permissions *after* copying code
RUN chmod -R 777 /app

# Switch to non-root user
USER appuser

# ================================
# ⚙️ Environment variables
# ================================
ENV PORT=8000
ENV HOST=0.0.0.0
ENV APP_MODULE=app.main:app

# ================================
# 🌐 Expose and run with Gunicorn
# ================================
EXPOSE 8000
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000", "app.main:app"]
