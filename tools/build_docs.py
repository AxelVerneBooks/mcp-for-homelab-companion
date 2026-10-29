#!/usr/bin/env python3
"""build_docs.py — render the GitHub Pages catalog from recipes/*/recipe.json.

Every recipe folder carries a recipe.json (schema: tools/schemas/recipe.schema.json).
This script turns them into:

  docs/index.html    the catalog page (static, no build step, no JS framework)
  docs/catalog.json  the same data, machine-readable, for indexers and agents
  docs/sitemap.xml   one URL, so crawlers find the page

Stanzas are lifted from the first ```json block in each recipe README, so the
README stays the single source of truth for client config.

Usage:
  python3 tools/build_docs.py           regenerate docs/
  python3 tools/build_docs.py --check   exit 1 if docs/ is stale (CI uses this)

Standard library only — nothing to install.
"""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECIPES = ROOT / "recipes"
DOCS = ROOT / "docs"

REPO_URL = "https://github.com/AxelVerneBooks/mcp-for-homelab-companion"
SITE_URL = "https://axelvernebooks.github.io/mcp-for-homelab-companion/"
BOOK_URL = "https://axelverne.com"

STATUS_LABEL = {"works-ootb": "Works OOTB", "needs-backend": "Needs backend"}
TRANSPORT_LABEL = {"stdio": "stdio", "streamable-http": "Streamable HTTP"}


def load_recipes():
    missing = [d.name for d in sorted(RECIPES.iterdir()) if d.is_dir() and not (d / "recipe.json").is_file()]
    if missing:
        sys.exit(f"recipes missing recipe.json (would be absent from the catalog): {', '.join(missing)}")
    out = []
    for path in sorted(RECIPES.glob("*/recipe.json")):
        r = json.loads(path.read_text())
        if r["id"] != path.parent.name:
            sys.exit(f"{path}: id {r['id']!r} does not match folder name")
        readme = (path.parent / "README.md").read_text()
        m = re.search(r"```json\n(.*?)```", readme, re.S)
        r["stanza"] = m.group(1).rstrip() if m else ""
        sj = r["upstream"].get("serverJson")
        if sj and not (path.parent / sj).is_file():
            sys.exit(f"{path}: upstream.serverJson points at missing {sj}")
        out.append(r)
    if not out:
        sys.exit("no recipes/*/recipe.json found")
    return out


def e(s):
    return html.escape(str(s), quote=True)


def card(r):
    folder = f"{REPO_URL}/tree/main/recipes/{r['id']}"
    up = r["upstream"]
    badges = [
        f'<span class="b {r["status"]}">{STATUS_LABEL[r["status"]]}</span>',
        f'<span class="b">{TRANSPORT_LABEL[r["transport"]]}</span>',
    ]
    if r.get("port"):
        badges.append(f'<span class="b">:{r["port"]}</span>')
    upstream = e(up["description"])
    if up.get("repository"):
        upstream = f'<a href="{e(up["repository"])}">{upstream}</a>'
    if up.get("registryName"):
        upstream += f' · registry: <code>{e(up["registryName"])}</code>'
    if up.get("serverJson"):
        upstream += f' · <a href="{REPO_URL}/blob/main/recipes/{e(r["id"])}/{e(up["serverJson"])}">server.json</a>'
    env_rows = "".join(
        f"<tr><td><code>{e(v['name'])}</code></td>"
        f"<td>{'required' if v['isRequired'] else 'optional'}{' · secret' if v['isSecret'] else ''}</td>"
        f"<td>{e(v['description'])}</td></tr>"
        for v in r["environmentVariables"]
    )
    scope = "".join(f"<li>{e(s)}</li>" for s in r["scopeNotes"])
    search = " ".join([r["title"], r["summary"], *r.get("tags", []), r["status"], r["transport"]]).lower()
    return f"""
<article class="card" id="recipe-{e(r['id'])}" data-status="{e(r['status'])}" data-transport="{e(r['transport'])}" data-search="{e(search)}">
  <header>
    <span class="num">{r['number']:02d}</span>
    <h2><a href="#recipe-{e(r['id'])}">{e(r['title'])}</a></h2>
  </header>
  <div class="badges">{''.join(badges)}</div>
  <p class="sum">{e(r['summary'])}</p>
  <p class="q">“{e(r['firstQuestion'])}”</p>
  <details>
    <summary>Stanza, env, scope</summary>
    <p class="meta">Upstream: {upstream}<br>Book: <a href="{BOOK_URL}"><em>MCP for the Homelab</em></a>, {e(r['chapter'])}</p>
    <pre><code>{e(r['stanza'])}</code></pre>
    {f'<table><thead><tr><th>Variable</th><th></th><th>Purpose</th></tr></thead><tbody>{env_rows}</tbody></table>' if env_rows else ''}
    <ul class="scope">{scope}</ul>
  </details>
  <footer><a href="{folder}">Open recipe folder →</a></footer>
</article>"""


def page(recipes):
    cards = "".join(card(r) for r in recipes)
    n = len(recipes)
    ootb = sum(r["status"] == "works-ootb" for r in recipes)
    ld = {
        "@context": "https://schema.org",
        "@type": "SoftwareSourceCode",
        "name": "MCP for the Homelab — Companion Recipes",
        "description": f"{n} Docker Compose recipes for running Model Context Protocol (MCP) servers in a homelab, read-only by default.",
        "codeRepository": REPO_URL,
        "license": "https://opensource.org/licenses/MIT",
        "programmingLanguage": ["Python", "YAML"],
        "isBasedOn": {"@type": "Book", "name": "MCP for the Homelab", "url": BOOK_URL},
    }
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MCP for the Homelab — Recipe Catalog</title>
<meta name="description" content="{n} copy-paste MCP server recipes for your homelab: Docker Compose stacks for Home Assistant, Proxmox, Grafana, Pi-hole, TrueNAS, *arr and more. Read-only by default. Free and MIT-licensed.">
<link rel="canonical" href="{SITE_URL}">
<meta property="og:type" content="website">
<meta property="og:title" content="MCP for the Homelab — Recipe Catalog">
<meta property="og:description" content="{n} copy-paste MCP stacks for your lab. Docker Compose recipes, scoped servers, read-only by default.">
<meta property="og:url" content="{SITE_URL}">
<meta property="og:image" content="{SITE_URL}social-preview.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/json" href="catalog.json" title="Recipe catalog (JSON)">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>
:root{{--bg:#0C1210;--panel:#0e1613;--ink:#cfe9d7;--muted:#7f9b8a;--accent:#3DDC68;--line:#1d2a22;--code:#070b09;--warn:#e3c26b;color-scheme:dark}}
@media (prefers-color-scheme:light){{:root{{--bg:#f6faf7;--panel:#fff;--ink:#14231a;--muted:#55705f;--accent:#1a8f3c;--line:#d5e3da;--code:#eef4f0;--warn:#8a6a00;color-scheme:light}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}}
code,pre,.num,.b{{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace}}
a{{color:var(--accent)}}
.wrap{{max-width:1100px;margin:0 auto;padding:0 16px}}
.hero{{padding:48px 0 24px;border-bottom:1px solid var(--line)}}
.kicker{{font:600 12px/1 ui-monospace,monospace;letter-spacing:.2em;text-transform:uppercase;color:var(--muted)}}
h1{{font-size:clamp(28px,5vw,44px);line-height:1.1;margin:12px 0}}
h1 span{{color:var(--accent)}}
.lede{{max-width:62ch;color:var(--muted);margin:0 0 20px}}
.cta{{display:flex;flex-wrap:wrap;gap:10px}}
.btn{{display:inline-block;padding:10px 16px;border-radius:8px;border:1px solid var(--line);text-decoration:none;font-weight:600}}
.btn.primary{{background:var(--accent);color:#06100a;border-color:var(--accent)}}
.quick{{margin:24px 0 0;background:var(--code);border:1px solid var(--line);border-radius:10px;padding:14px 16px;overflow-x:auto}}
.tools{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:28px 0 16px}}
.tools input{{flex:1 1 220px;min-width:0;padding:10px 12px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:var(--ink);font:inherit}}
.tools button{{padding:9px 12px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:var(--ink);font:inherit;cursor:pointer}}
.tools button[aria-pressed=true]{{border-color:var(--accent);color:var(--accent)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,330px),1fr));gap:16px;padding-bottom:40px}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px;display:flex;flex-direction:column;gap:10px;min-width:0}}
.card header{{display:flex;gap:10px;align-items:baseline}}
.num{{color:var(--accent);font-weight:700}}
.card h2{{font-size:18px;margin:0}} .card h2 a{{color:inherit;text-decoration:none}}
.badges{{display:flex;flex-wrap:wrap;gap:6px}}
.b{{font-size:12px;padding:2px 8px;border:1px solid var(--line);border-radius:999px;color:var(--muted)}}
.b.works-ootb{{color:var(--accent);border-color:var(--accent)}} .b.needs-backend{{color:var(--warn);border-color:var(--warn)}}
.sum{{margin:0}} .q{{margin:0;color:var(--muted);font-style:italic}}
details summary{{cursor:pointer;color:var(--muted)}}
.meta{{font-size:14px;color:var(--muted)}}
pre{{background:var(--code);border:1px solid var(--line);border-radius:8px;padding:12px;overflow-x:auto;font-size:13px;margin:8px 0}}
table{{width:100%;border-collapse:collapse;font-size:13px;margin:8px 0}} td,th{{text-align:left;padding:6px 4px;border-top:1px solid var(--line);vertical-align:top}} td:first-child{{white-space:nowrap}}
.scope{{font-size:14px;padding-left:18px;margin:8px 0}}
.card footer{{margin-top:auto;font-size:14px}}
.book{{border-top:1px solid var(--line);padding:32px 0}}
.book h2{{margin-top:0}}
.foot{{border-top:1px solid var(--line);padding:20px 0 40px;color:var(--muted);font-size:14px}}
[hidden]{{display:none!important}}
</style>
</head>
<body>
<section class="hero"><div class="wrap">
  <div class="kicker">companion repo · free · MIT</div>
  <h1>MCP for the <span>Homelab</span></h1>
  <p class="lede">{n} copy-paste Model Context Protocol stacks for your lab — Docker Compose recipes, scoped servers, read-only by default. {ootb} run with zero external services. The recipes stand alone; <a href="{BOOK_URL}">the book</a> teaches the why, the scoping ritual, the security model, and the error catalog behind them.</p>
  <div class="cta">
    <a class="btn primary" href="{BOOK_URL}">Get the book</a>
    <a class="btn" href="{REPO_URL}">View on GitHub</a>
    <a class="btn" href="catalog.json">catalog.json</a>
  </div>
  <pre class="quick"><code>git clone {REPO_URL}.git
cd mcp-for-homelab-companion && ./tools/smoke.sh</code></pre>
</div></section>
<main class="wrap">
  <div class="tools" role="search">
    <input id="q" type="search" placeholder="Filter: proxmox, grafana, stdio…" aria-label="Filter recipes">
    <button type="button" data-f="status" data-v="works-ootb" aria-pressed="false">Works OOTB</button>
    <button type="button" data-f="transport" data-v="stdio" aria-pressed="false">stdio</button>
    <button type="button" data-f="transport" data-v="streamable-http" aria-pressed="false">HTTP</button>
  </div>
  <div class="grid" id="grid">{cards}
  </div>
  <section class="book">
    <h2>The book behind the recipes</h2>
    <p><a href="{BOOK_URL}"><em>MCP for the Homelab</em></a> walks through every recipe here and the reasoning that keeps them safe: transports (Ch. 3), scoping and promotion ceremonies (Ch. 5–6), the security rules (Ch. 7), and the failure catalog. DRM-free, one flat price.</p>
    <a class="btn primary" href="{BOOK_URL}">axelverne.com →</a>
  </section>
</main>
<footer class="foot"><div class="wrap">
  MIT-licensed · <a href="{REPO_URL}/blob/main/CONTRIBUTING.md">Contribute a recipe</a> · <a href="{REPO_URL}/issues/new/choose">Report a problem</a> · Generated from <code>recipes/*/recipe.json</code>
</div></footer>
<script>
(function(){{
  var q=document.getElementById('q'),btns=[].slice.call(document.querySelectorAll('.tools button')),cards=[].slice.call(document.querySelectorAll('.card'));
  function apply(){{
    var t=q.value.trim().toLowerCase(),on=btns.filter(function(b){{return b.getAttribute('aria-pressed')==='true'}});
    cards.forEach(function(c){{
      var ok=!t||c.dataset.search.indexOf(t)>-1;
      on.forEach(function(b){{if(c.dataset[b.dataset.f]!==b.dataset.v)ok=false}});
      c.hidden=!ok;
    }});
  }}
  q.addEventListener('input',apply);
  btns.forEach(function(b){{b.addEventListener('click',function(){{
    var p=b.getAttribute('aria-pressed')!=='true';
    btns.forEach(function(o){{if(o.dataset.f===b.dataset.f)o.setAttribute('aria-pressed','false')}});
    b.setAttribute('aria-pressed',String(p));apply();
  }})}});
}})();
</script>
</body>
</html>
"""


def catalog(recipes):
    items = []
    for r in recipes:
        r = {k: v for k, v in r.items() if k != "$schema"}
        r["url"] = f"{REPO_URL}/tree/main/recipes/{r['id']}"
        items.append(r)
    return json.dumps(
        {"name": "MCP for the Homelab — Companion Recipes", "book": BOOK_URL, "repository": REPO_URL, "recipes": items},
        indent=2,
        ensure_ascii=False,
    ) + "\n"


def sitemap():
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{SITE_URL}</loc></url>\n"
        "</urlset>\n"
    )


def main():
    check = "--check" in sys.argv[1:]
    recipes = load_recipes()
    outputs = {
        DOCS / "index.html": page(recipes),
        DOCS / "catalog.json": catalog(recipes),
        DOCS / "sitemap.xml": sitemap(),
    }
    stale = [p for p, body in outputs.items() if not p.is_file() or p.read_text() != body]
    if check:
        if stale:
            print("docs/ is stale — run: python3 tools/build_docs.py", file=sys.stderr)
            for p in stale:
                print(f"  {p.relative_to(ROOT)}", file=sys.stderr)
            sys.exit(1)
        print(f"docs/ up to date ({len(recipes)} recipes)")
        return
    DOCS.mkdir(exist_ok=True)
    for p, body in outputs.items():
        p.write_text(body)
    print(f"wrote {len(outputs)} files for {len(recipes)} recipes")


if __name__ == "__main__":
    main()
