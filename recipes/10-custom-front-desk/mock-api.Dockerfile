# Mock vendor API for Recipe 10 — lets the front desk work OOTB.
FROM python:3.14.8-slim

WORKDIR /app
RUN pip install --no-cache-dir "fastapi==0.156.5" "uvicorn==0.54.0"

COPY mock-api.py .

EXPOSE 8080
CMD ["uvicorn", "mock-api:app", "--host", "0.0.0.0", "--port", "8080"]
