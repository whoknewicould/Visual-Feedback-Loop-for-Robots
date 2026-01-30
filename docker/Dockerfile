# Visual Feedback Loop - CPU-only, Python 3.10
# Webcam optional (document limitations in README)

FROM python:3.10-slim

WORKDIR /app

# Install system deps for OpenCV (minimal for headless)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: run with camera 0 (will fail if no device in container)
# Use --no-display for headless; webcam requires --device=/dev/video0 and display if needed
CMD ["python", "run.py", "--source", "0"]
