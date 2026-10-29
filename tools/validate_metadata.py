#!/usr/bin/env python3
"""validate_metadata.py — schema-check every recipe.json and server.json.

  recipes/*/recipe.json  against tools/schemas/recipe.schema.json
  recipes/*/server.json  against tools/schemas/server.schema.json
                         (vendored copy of the MCP Registry 2025-12-11 schema)

Also cross-checks recipe.json against docker-compose.yml: every variable in
environmentVariables must appear in the compose file, and the declared port
must be published there.

Usage: pip install jsonschema && python3 tools/validate_metadata.py
"""

import json
import re
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    sys.exit("needs jsonschema: pip install jsonschema")

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "tools" / "schemas"

recipe_schema = json.loads((SCHEMAS / "recipe.schema.json").read_text())
server_schema = json.loads((SCHEMAS / "server.schema.json").read_text())

errors = []
dirs = sorted(d for d in (ROOT / "recipes").iterdir() if d.is_dir())
for d in dirs:
    rel = d.relative_to(ROOT)
    rj = d / "recipe.json"
    if not rj.is_file():
        errors.append(f"{rel}: missing recipe.json")
        continue
    recipe = json.loads(rj.read_text())
    for err in jsonschema.Draft7Validator(recipe_schema).iter_errors(recipe):
        errors.append(f"{rel}/recipe.json: {err.json_path}: {err.message}")

    compose = (d / "docker-compose.yml").read_text()
    for var in recipe.get("environmentVariables", []):
        if not re.search(r"\$\{" + re.escape(var["name"]) + r"\b", compose) and var["name"] not in compose:
            errors.append(f"{rel}/recipe.json: {var['name']} not referenced in docker-compose.yml")
    port = recipe.get("port")
    if port and f'"{port}:' not in compose:
        errors.append(f"{rel}/recipe.json: port {port} not published in docker-compose.yml")

    sj = d / "server.json"
    if sj.is_file():
        server = json.loads(sj.read_text())
        for err in jsonschema.Draft7Validator(server_schema).iter_errors(server):
            errors.append(f"{rel}/server.json: {err.json_path}: {err.message}")

# Docs pages: relative links must resolve; every recipe README and the
# catalog page must link back to the book.
BOOK_URL = "https://axelverne.com"
md_files = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", *sorted((ROOT / "recipes").glob("*/README.md"))]
for md in md_files:
    rel = md.relative_to(ROOT)
    text = md.read_text()
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        if re.match(r"[a-z]+:|#", target):
            continue
        if not (md.parent / target.split("#")[0]).exists():
            errors.append(f"{rel}: broken link to {target}")
    if md.parent.parent == ROOT / "recipes" and BOOK_URL not in text:
        errors.append(f"{rel}: no link to {BOOK_URL}")
index = ROOT / "docs" / "index.html"
if index.is_file() and f'href="{BOOK_URL}"' not in index.read_text():
    errors.append(f"docs/index.html: no link to {BOOK_URL}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print(f"metadata OK ({len(dirs)} recipes)")
