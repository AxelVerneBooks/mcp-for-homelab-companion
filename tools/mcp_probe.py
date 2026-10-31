#!/usr/bin/env python3
"""mcp_probe.py — a tiny, dependency-free MCP client for CI.

Speaks just enough MCP to prove a server is really up, not just "running":
initialize → notifications/initialized → tools/list → (optional) tools/call.

  HTTP (streamable HTTP):  mcp_probe.py --http http://127.0.0.1:9110/mcp
  stdio (subprocess):      mcp_probe.py [options] --stdio -- docker compose run --rm -T svc
                           (options go BEFORE --stdio; everything after is the command)

Options:
  --call NAME [--args JSON] [--expect TEXT]   call a tool; fail unless it
                                              succeeds (and contains TEXT)
  --deny NAME [--deny-args JSON]              call a tool; fail unless the
                                              server REFUSES it (isError)
  --retry-for SECONDS                         keep retrying the handshake
                                              (HTTP only) while the server boots
Exit 0 = every check passed.
"""

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

PROTOCOL = "2025-06-18"


class Fail(Exception):
    pass


def log(msg: str) -> None:
    print(f"    {msg}", flush=True)


# --- transports ------------------------------------------------------------

class HttpTransport:
    def __init__(self, url: str):
        self.url = url
        self.session = None

    def send(self, msg: dict):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": PROTOCOL,
        }
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        req = urllib.request.Request(
            self.url, data=json.dumps(msg).encode(), headers=headers, method="POST"
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            self.session = resp.headers.get("Mcp-Session-Id") or self.session
            body = resp.read().decode()
        if "id" not in msg:
            return None  # notification: 202, no body
        return self._parse(body, msg["id"])

    @staticmethod
    def _parse(body: str, want_id):
        # Either a plain JSON body or an SSE stream of "data: {...}" lines.
        candidates = [body] if body.lstrip().startswith("{") else [
            line[5:].strip() for line in body.splitlines() if line.startswith("data:")
        ]
        for c in candidates:
            try:
                obj = json.loads(c)
            except json.JSONDecodeError:
                continue
            if obj.get("id") == want_id:
                return obj
        raise Fail(f"no response for id={want_id} in body: {body[:300]!r}")

    def close(self):
        pass


class StdioTransport:
    def __init__(self, cmd: list[str]):
        self.proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1
        )

    def send(self, msg: dict):
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        if "id" not in msg:
            return None
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise Fail(f"server exited (code {self.proc.poll()}) before answering id={msg['id']}")
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue  # stray log line on stdout
            if obj.get("id") == msg["id"]:
                return obj

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=20)
        except Exception:
            self.proc.kill()


# --- the probe -------------------------------------------------------------

def rpc(t, mid: int, method: str, params: dict) -> dict:
    resp = t.send({"jsonrpc": "2.0", "id": mid, "method": method, "params": params})
    if "error" in resp:
        raise Fail(f"{method} → JSON-RPC error {resp['error']}")
    return resp["result"]


def tool_text(result: dict) -> str:
    return "\n".join(c.get("text", "") for c in result.get("content", []))


def probe(t, a) -> None:
    init = rpc(t, 1, "initialize", {
        "protocolVersion": PROTOCOL,
        "capabilities": {},
        "clientInfo": {"name": "homelab-companion-ci", "version": "1"},
    })
    info = init.get("serverInfo", {})
    log(f"✓ initialize — {info.get('name')} {info.get('version')} (protocol {init.get('protocolVersion')})")
    t.send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    tools = [x["name"] for x in rpc(t, 2, "tools/list", {}).get("tools", [])]
    if not tools:
        raise Fail("tools/list returned no tools")
    log(f"✓ tools/list — {len(tools)} tools: {', '.join(tools[:8])}{' …' if len(tools) > 8 else ''}")

    if a.call:
        res = rpc(t, 3, "tools/call", {"name": a.call, "arguments": json.loads(a.args)})
        text = tool_text(res)
        if res.get("isError"):
            raise Fail(f"tools/call {a.call} errored: {text[:300]}")
        if a.expect and a.expect not in text:
            raise Fail(f"tools/call {a.call} result lacks {a.expect!r}: {text[:300]}")
        log(f"✓ tools/call {a.call} — {' '.join(text.split())[:100] or '(empty)'}")

    if a.deny:
        res = rpc(t, 4, "tools/call", {"name": a.deny, "arguments": json.loads(a.deny_args)})
        if not res.get("isError"):
            raise Fail(f"tools/call {a.deny} SUCCEEDED but must be refused: {tool_text(res)[:300]}")
        log(f"✓ tools/call {a.deny} refused — {tool_text(res).strip()[:80]}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--http")
    p.add_argument("--stdio", action="store_true")
    p.add_argument("--call")
    p.add_argument("--args", default="{}")
    p.add_argument("--expect")
    p.add_argument("--deny")
    p.add_argument("--deny-args", default="{}")
    p.add_argument("--retry-for", type=float, default=0)
    p.add_argument("cmd", nargs=argparse.REMAINDER)
    a = p.parse_args()

    if a.stdio:
        cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
        t = StdioTransport(cmd)
        try:
            probe(t, a)
        except Fail as e:
            log(f"✗ {e}")
            return 1
        finally:
            t.close()
        return 0

    if not a.http:
        p.error("need --http URL or --stdio -- CMD")

    deadline = time.monotonic() + a.retry_for
    while True:
        try:
            probe(HttpTransport(a.http), a)
            return 0
        except (urllib.error.URLError, ConnectionError, TimeoutError, Fail) as e:
            if time.monotonic() >= deadline:
                log(f"✗ {e}")
                return 1
            time.sleep(2)


if __name__ == "__main__":
    sys.exit(main())
