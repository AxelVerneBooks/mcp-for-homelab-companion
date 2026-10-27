# Recipe 10 — The Custom Front Desk (book, Chapter 6)
# Base pinned to an exact patch release; bump deliberately (SECURITY.md).
FROM python:3.12.7-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# MCP SDK + HTTP client. Pin to the versions you tested with.
RUN pip install --no-cache-dir "mcp>=1.2,<2" "httpx>=0.27,<1" "uvicorn>=0.30,<1"

COPY server.py .

# Never run as root (SECURITY.md). Code stays root-owned, so the server
# can't rewrite itself even if the rootfs weren't read-only.
USER 65534:65534

# Streamable HTTP so any client (and the repo's smoke test) can reach it.
# For a personal stdio setup, run server.py locally instead.
EXPOSE 9110
CMD ["python", "server.py"]
