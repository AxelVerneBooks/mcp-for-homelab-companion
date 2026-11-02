# Recipe 10 — The Custom Front Desk (book, Chapter 6)
# Pin the base tag when you adopt this for a real service.
FROM python:3.12-slim

WORKDIR /app

# MCP Registry ownership check for the OCI package in server.json.
LABEL io.modelcontextprotocol.server.name="io.github.AxelVerneBooks/homelab-pool-front-desk"

# MCP SDK + HTTP client. Pin to the versions you tested with.
RUN pip install --no-cache-dir "mcp>=1.2,<2" "httpx>=0.27,<1" "uvicorn>=0.30,<1"

COPY server.py .

# Streamable HTTP so any client (and the repo's smoke test) can reach it.
# For a personal stdio setup, run server.py locally instead.
EXPOSE 9110
CMD ["python", "server.py"]
