# Recipe 10 — The Custom Front Desk (book, Chapter 6)
# Base and dependencies are pinned to exact, tested versions (book, Ch. 5).
FROM python:3.14.8-slim

WORKDIR /app

# MCP SDK + HTTP client, pinned to the versions the smoke test passes with.
# mcp stays on the 1.x line: 2.x renamed FastMCP to MCPServer, and server.py
# follows the book's FastMCP code.
RUN pip install --no-cache-dir "mcp==1.30.0" "httpx==0.28.1" "uvicorn==0.54.0"

COPY server.py .

# Streamable HTTP so any client (and the repo's smoke test) can reach it.
# For a personal stdio setup, run server.py locally instead.
EXPOSE 9110
CMD ["python", "server.py"]
