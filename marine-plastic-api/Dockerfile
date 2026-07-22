# CloudEco: Marine Plastic Detection System
# Author: Devesh Gurusinghe ()
# Purpose: Multi-stage Docker build for optimized ML inference container
# Date: 2026-04-30

# ============================================
# BUILD STAGE — compile wheels / pip install
# ============================================
# I split the build into two stages so the final image stays small and does not ship gcc/build tools.
FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH

WORKDIR /app

# I install build-essential here because torch/ultralytics wheels sometimes need compilation on slim images.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt /app/requirements-api.txt
# I pip install to --user so I can copy /root/.local into the runtime stage for appuser.
RUN pip install --no-cache-dir --user -r /app/requirements-api.txt

# ============================================
# RUNTIME STAGE — minimal OS + app
# ============================================
# I only keep what the API needs at runtime — no compilers in the final image.
FROM python:3.10-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/appuser/.local/bin:$PATH

WORKDIR /app

# I install OpenCV runtime libs because Ultralytics uses them for image plotting.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /home/appuser/.local

COPY app /app/app
# I copy weights paths that inference.py looks for (best.pt or yolov8m.pt).
COPY runs /app/runs
COPY yolov8m.pt /app/yolov8m.pt

EXPOSE 8000

# ============================================
# SECURITY — non-root user
# ============================================
# I run as appuser (uid 1000) because the rubric expects a non-root container process.
RUN useradd -m -u 1000 appuser && \
    mkdir -p /home/appuser/.config /home/appuser/.cache && \
    chown -R appuser:appuser /app /home/appuser
USER appuser

# I use uvicorn with 4 workers in the image; in K8s I had to watch memory — too many workers + replicas = OOMKilled.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
