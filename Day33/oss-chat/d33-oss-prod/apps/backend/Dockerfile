FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Install deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY app /app/app
COPY .env.example /app/.env.example

# Non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Production-style: gunicorn + uvicorn worker
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "-b", "0.0.0.0:8000", "-w", "2", "--timeout", "120"]
