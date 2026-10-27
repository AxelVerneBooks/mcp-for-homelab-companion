# Mock vendor API for Recipe 10 — lets the front desk work OOTB.
FROM python:3.12.7-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install --no-cache-dir "fastapi>=0.115,<1" "uvicorn>=0.30,<1"

COPY mock-api.py .

USER 65534:65534

EXPOSE 8080
CMD ["uvicorn", "mock-api:app", "--host", "0.0.0.0", "--port", "8080"]
