#!/usr/bin/env python3
"""Recipe 10 — The Custom Front Desk (book, Chapter 6).

A complete, runnable FastMCP server wrapping the (mock) pool controller
API with two READ-ONLY tools. This is the minimal "wrap anything" pattern:

  - docstrings are the menu (the assistant reads them to pick tools)
  - the signature is the schema (params become the JSON contract)
  - scope is enforced in CODE (asserts, allowlists), never in prompts
  - write tools ship COMMENTED OUT (the Chapter 6 promotion ritual)

Transport: streamable HTTP on :9110 (so the repo's smoke test can exercise
a real handshake). For stdio, use mcp.run(transport="stdio").
"""

import os

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pool", host="0.0.0.0", port=int(os.environ.get("PORT", "9110")))

API = os.environ.get("POOL_API_URL", "http://pool-api:8080")
TIMEOUT = float(os.environ.get("POOL_TIMEOUT", "10"))


def _client() -> httpx.AsyncClient:
    # Secrets come from env (book, Ch. 7 Rule 2) — never baked into code.
    key = os.environ.get("POOL_API_KEY", "")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    return httpx.AsyncClient(base_url=API, headers=headers, timeout=TIMEOUT)


@mcp.tool()
async def get_pool_status() -> dict:
    """Current pool temperature (C), heater state, and pump mode."""
    async with _client() as c:
        r = await c.get("/status")
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def list_pool_sensors() -> list[dict]:
    """List every sensor the controller knows about, with last readings."""
    async with _client() as c:
        r = await c.get("/sensors")
        r.raise_for_status()
        return r.json()


# --- WRITE TOOL, DELIBERATELY DISABLED (book, Ch. 6) ---------------------
# Uncomment after a clean week of read-only operation, then re-scope:
#   1. note the promotion in your menu-notes file (date, reason)
#   2. keep the assert — the menu is enforced in code, not prompts
#   3. keep the approval click on for this tool, forever
#
# @mcp.tool()
# async def set_pump_mode(mode: str) -> str:
#     """Set pump mode: 'auto', 'low', or 'high'."""
#     assert mode in ("auto", "low", "high"), f"bad mode {mode}"
#     async with _client() as c:
#         r = await c.post("/pump", json={"mode": mode})
#         r.raise_for_status()
#         return f"pump set to {mode}"


if __name__ == "__main__":
    # NOTE (the bug every first-timer hits): FastMCP.run() defaults to stdio —
    # in a container that means an instant, silent exit (stdin closes).
    # Serving streamable HTTP on the host/port set in the constructor:
    mcp.run(transport="streamable-http")
