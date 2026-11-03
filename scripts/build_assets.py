#!/usr/bin/env python3
"""Build the SVG assets used by the profile README.

Usage:  python3 scripts/build_assets.py [languages.json]

- assets/profile-banner.svg  hero banner; embeds assets/portrait.jpg as base64
- assets/languages.svg       language spread across owned repositories
- assets/divider.svg         thin section divider

languages.json is optional: a list of {"lang": str, "repos": int}. Regenerate it with
  gh repo list geekynitish --limit 200 --json name,isFork --jq '.[]|select(.isFork|not)|.name' \
    | while read r; do gh api repos/geekynitish/$r/languages --jq keys; done \
    | jq -s 'flatten|group_by(.)|map({lang:.[0],repos:length})|sort_by(-.repos)'
"""
import base64
import json
import pathlib
import random
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

SANS = "'Inter','Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

BG0, BG1, BG2 = "#060a12", "#0a1322", "#0b1a2e"
INK, MUTED, DIM = "#e6edf7", "#8b9bb4", "#5b6b85"
CYAN, BLUE = "#22d3ee", "#3b82f6"


def network(seed: int, x0: int, x1: int, y0: int, y1: int, n: int, hole: tuple = (0, 0, 0)) -> str:
    """Deterministic constellation of nodes and short links, kept clear of `hole` (cx, cy, r)."""
    rnd = random.Random(seed)
    hx, hy, hr = hole
    pts = []
    while len(pts) < n:
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if (x - hx) ** 2 + (y - hy) ** 2 > hr ** 2:
            pts.append((x, y))
    out = []
    for i, (ax, ay) in enumerate(pts):
        for bx, by in pts[i + 1:]:
            d = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
            if d < 120:
                op = round(0.22 * (1 - d / 120), 3)
                out.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="url(#link)" stroke-opacity="{op}" stroke-width="1"/>')
    for x, y in pts:
        r = rnd.choice([1.2, 1.6, 2.2])
        op = rnd.choice([0.35, 0.5, 0.7])
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{CYAN}" fill-opacity="{op}"/>')
    return "\n    ".join(out)


def banner() -> str:
    portrait = base64.b64encode((ASSETS / "portrait.jpg").read_bytes()).decode()
    W, H = 1280, 400
    cx, cy, r = 1052, 200, 116
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">Nitish Kumar · Developer | Thinker | Researcher</title>
  <desc id="d">Developer by Practice. Thinker by Nature. Researcher by Curiosity.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BG0}"/><stop offset=".55" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/>
    </linearGradient>
    <radialGradient id="glow" cx="{cx / W:.3f}" cy=".5" r=".42">
      <stop offset="0" stop-color="{BLUE}" stop-opacity=".22"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="link" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="{CYAN}"/>
    </linearGradient>
    <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{BLUE}" stop-opacity=".35"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".9"/>
    </linearGradient>
    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="#9fb4d9" stroke-opacity=".05"/>
    </pattern>
    <clipPath id="face"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>
  </defs>

  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <rect width="{W}" height="{H}" fill="url(#glow)"/>

  <g>
    {network(7, 640, 1270, 20, 380, 46, (cx, cy, r + 40))}
  </g>

  <!-- orbits -->
  <g fill="none" stroke-linecap="round">
    <circle cx="{cx}" cy="{cy}" r="{r + 26}" stroke="{BLUE}" stroke-opacity=".18"/>
    <circle cx="{cx}" cy="{cy}" r="{r + 58}" stroke="{CYAN}" stroke-opacity=".08" stroke-dasharray="2 7"/>
    <path d="M{cx - (r + 26)} {cy} A{r + 26} {r + 26} 0 0 1 {cx} {cy - (r + 26)}" stroke="{CYAN}" stroke-opacity=".7" stroke-width="1.5"/>
    <circle cx="{cx}" cy="{cy - (r + 26)}" r="3.5" fill="{CYAN}"/>
    <circle cx="{cx + r + 58}" cy="{cy}" r="2.5" fill="{BLUE}"/>
  </g>

  <!-- portrait -->
  <circle cx="{cx}" cy="{cy}" r="{r + 4}" fill="{BG0}"/>
  <image x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" clip-path="url(#face)" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{portrait}" xlink:href="data:image/jpeg;base64,{portrait}"/>
  <circle cx="{cx}" cy="{cy}" r="{r + 3}" fill="none" stroke="url(#ring)" stroke-width="2.5"/>

  <!-- text -->
  <g font-family="{SANS}">
    <text x="72" y="104" font-family="{MONO}" font-size="15" fill="{CYAN}" letter-spacing="1.5">~/geekynitish <tspan fill="{DIM}">— jaipur, india</tspan></text>
    <text x="70" y="182" font-size="72" font-weight="700" fill="{INK}" letter-spacing="-1.5">Nitish Kumar</text>
    <rect x="72" y="208" width="120" height="2" fill="url(#rule)"/>
    <text x="72" y="250" font-size="23" font-weight="500" fill="#c7d6ee" letter-spacing="1">Developer <tspan fill="{CYAN}">|</tspan> Thinker <tspan fill="{CYAN}">|</tspan> Researcher</text>
    <text x="72" y="296" font-size="17" fill="{MUTED}">Developer by Practice. Thinker by Nature. Researcher by Curiosity.</text>
    <text x="72" y="344" font-family="{MONO}" font-size="13" fill="{DIM}" letter-spacing=".5">web · ai · automation · edge · search</text>
  </g>
</svg>
'''


def languages(data: list[dict]) -> str:
    # GitHub's linguist labels some PHP as "Hack"; fold it into PHP.
    merged: dict[str, int] = {}
    for d in data:
        if d["lang"] in {"Less", "Smarty"}:  # minor stylesheet/template dialects
            continue
        name = {"Hack": "PHP", "PLpgSQL": "PL/pgSQL"}.get(d["lang"], d["lang"])
        merged[name] = max(merged.get(name, 0), d["repos"])
    rows = sorted(merged.items(), key=lambda kv: -kv[1])[:10]
    total = REPO_TOTAL
    W, top, row_h = 880, 92, 26
    H = top + row_h * len(rows) + 46
    bar_x, bar_w = 190, 560
    peak = rows[0][1]
    out = []
    for i, (name, n) in enumerate(rows):
        y = top + i * row_h
        w = max(4, bar_w * n / peak)
        out.append(
            f'<text x="48" y="{y + 13}" font-size="14" fill="#c7d6ee">{name}</text>'
            f'<rect x="{bar_x}" y="{y + 2}" width="{bar_w}" height="12" rx="6" fill="#1a2740" fill-opacity=".6"/>'
            f'<rect x="{bar_x}" y="{y + 2}" width="{w:.1f}" height="12" rx="6" fill="url(#bar)" fill-opacity="{0.55 + 0.45 * n / peak:.2f}"/>'
            f'<text x="{bar_x + bar_w + 20}" y="{y + 13}" font-family="{MONO}" font-size="13" fill="{MUTED}">{n} repos</text>'
        )
    body = "\n  ".join(out)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
  <title id="t">Languages used across {total} repositories</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG2}"/></linearGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
  </defs>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="url(#bg)" stroke="#1e2b44"/>
  <g font-family="{SANS}">
  <text x="48" y="48" font-size="18" font-weight="600" fill="{INK}">Language spread</text>
  <text x="48" y="70" font-size="13" fill="{DIM}">Repositories using each language · {total} owned repos, public and private · snapshot {date.today():%b %Y}</text>
  {body}
  </g>
</svg>
'''


def divider() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="24" viewBox="0 0 1280 24" role="presentation">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{BLUE}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN}" stop-opacity=".7"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/>
  </linearGradient></defs>
  <rect x="140" y="11.5" width="1000" height="1" fill="url(#g)"/>
  <circle cx="640" cy="12" r="3" fill="{CYAN}"/>
</svg>
'''


if __name__ == "__main__":
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ASSETS / "languages.json"
    lang_data = json.loads(src.read_text())
    REPO_TOTAL = int(json.loads((ASSETS / "languages.meta.json").read_text())["repos"])
    (ASSETS / "profile-banner.svg").write_text(banner())
    (ASSETS / "languages.svg").write_text(languages(lang_data))
    (ASSETS / "divider.svg").write_text(divider())
    print("wrote", *(p.name for p in sorted(ASSETS.glob("*.svg"))))
