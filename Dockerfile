# --- Builder ---
FROM python:3.14-slim AS builder

WORKDIR /app

# Only install build tools if your requirements actually need them (like psycopg2 or cryptography)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Using --user installs to /root/.local, which is cleaner to copy
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Final ---
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:${PATH}"

# Create a non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
WORKDIR /home/appuser/app

# Copy installed packages from builder to the new user's home
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appgroup . .

# Switch to the non-root user
USER appuser

EXPOSE 8000

# Use a standard list format for CMD to handle signals (like SIGTERM) correctly for K8s
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]