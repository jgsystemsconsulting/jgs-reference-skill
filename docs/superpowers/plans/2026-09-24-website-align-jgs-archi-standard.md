# Plan: P8 website-align-jgs-archi-standard

- date: 2026-09-24
- spec: docs/superpowers/specs/2026-09-24-website-align-jgs-archi-standard.md (reviewed clean over 2 ARL rounds)
- plan_path: docs/superpowers/plans/2026-09-24-website-align-jgs-archi-standard.md
- author-leaf: claude unavailable; plan-author fallback (inline on sdd-executor-deep seat)
- context: ad-hoc (spec divergence inventory is the alignment contract; this repo `docs/index.html` + `docs/fonts/*.woff2` + `docs/.nojekyll`; sibling standard `jgs-archi-skills/docs/index.html` + `site.css` + favicons + `images/jgs-emblem.png` readable locally; pyproject version 0.2.1)
- research: skipped (carried from spec)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align this repo's GitHub Pages landing page with the jgs-archi-skills site shell (external `site.css`, masthead-only metadata, `nav.site` + brand emblem, local favicons, OG/Twitter/JSON-LD parity) while keeping product copy, fixing four-gate + `--self-check` truth, and shipping a repo-specific 1200x630 OG PNG with no build step.

**Architecture:** Three tasks in dependency order. Task 1 extracts CSS and wires the stylesheet. Task 2 restructures `index.html` chrome and truth copy. Task 3 copies JGSC-owned icon/emblem binaries, generates a product-neutral OG PNG via local PIL (stdlib zlib+struct fallback), and runs SC1-SC18 greps. No `site.js`, no motion, no multi-page IA, no edits under `jgs-archi-skills`.

**Tech stack:** Static HTML + CSS only. Python 3.9+ stdlib for verification greps; Pillow if importable for OG PNG, else pure-stdlib PNG writer included below. No bundler, no CDN fonts, no new project dependencies.

## Approach

S-sized, three tasks:

1. Create `docs/site.css` from this page's inline CSS plus sibling non-motion `nav.site` / brand rules; point `index.html` at it; delete the inline `<style>` block.
2. Structural HTML: two-line copyright comment, favicon links, OG/Twitter/JSON-LD, masthead metadata only, `nav.site` with emblem + six anchors + Repository, REV `0.2.1`, four-gates + self-check truth, Owner punctuation.
3. Assets (favicon set, emblem, OG PNG) + final SC1-SC18 verification battery.

Pinned product values (single source: `pyproject.toml` version `0.2.1` today):

| Field | Value |
|---|---|
| DOC-ID | `JGS-REF-SKILL` |
| REV / softwareVersion | `0.2.1` |
| Canonical / og:url | `https://jgsystemsconsulting.github.io/jgs-reference-skill/` |
| codeRepository | `https://github.com/jgsystemsconsulting/jgs-reference-skill` |
| license URL | `https://github.com/jgsystemsconsulting/jgs-reference-skill/blob/main/LICENSE` |
| OG file (local) | `docs/images/og/og-reference-skill-1200.png` |
| OG absolute meta | `https://jgsystemsconsulting.github.io/jgs-reference-skill/images/og/og-reference-skill-1200.png` |
| Emblem (local) | `docs/images/jgs-emblem.png` |
| applicationCategory | `DeveloperApplication` |
| operatingSystem | `Any` |

Sibling paths are **read/copy sources only** (never commit into that tree):

- `C:/Users/gower/OneDrive/Documents/GitHub/jgs-archi-skills/docs/site.css`
- `C:/Users/gower/OneDrive/Documents/GitHub/jgs-archi-skills/docs/favicon.ico` (3151 B)
- `C:/Users/gower/OneDrive/Documents/GitHub/jgs-archi-skills/docs/favicon-32x32.png` (306 B)
- `C:/Users/gower/OneDrive/Documents/GitHub/jgs-archi-skills/docs/apple-touch-icon.png` (10168 B)
- `C:/Users/gower/OneDrive/Documents/GitHub/jgs-archi-skills/docs/images/jgs-emblem.png` (3397 B)

Do **not** copy `og-skills-1200.jpg` (Archi product art). Do **not** add `site.js` or brand-trace SVG.

## Blocking-discovery rule

Before any product edit, run from the repo root in Git Bash:

```bash
test -f docs/index.html && test -f docs/.nojekyll || { echo "BLOCKED: docs landing missing"; exit 1; }
ls docs/fonts/*.woff2 | wc -l   # expect 4
test -f ../jgs-archi-skills/docs/site.css \
  && test -f ../jgs-archi-skills/docs/favicon.ico \
  && test -f ../jgs-archi-skills/docs/favicon-32x32.png \
  && test -f ../jgs-archi-skills/docs/apple-touch-icon.png \
  && test -f ../jgs-archi-skills/docs/images/jgs-emblem.png \
  || { echo "BLOCKED: sibling standard assets not readable at ../jgs-archi-skills/docs"; exit 1; }
python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])" 2>/dev/null \
  || python -c "import re; print(re.search(r'^version\s*=\s*\"([^\"]+)\"', open('pyproject.toml',encoding='utf-8').read(), re.M).group(1))"
# expect 0.2.1 (or whatever pyproject says; that string is the only REV source)
python -c "import PIL; print('PIL', PIL.__version__)" 2>/dev/null || echo "PIL_MISSING (use Task 3 stdlib PNG writer)"
```

If `docs/index.html`, `docs/.nojekyll`, the four woff2 files, or any sibling asset above is missing: **stop and report**. Do not invent a second palette, re-download fonts, or deep-link runtime URLs into the sibling repo.

If PIL is missing, do **not** block the whole package: Task 3 ships a pure-stdlib PNG writer. Only block if both PIL and the stdlib writer path fail to produce a valid 1200x630 PNG on disk.

Do not modify anything under `jgs-archi-skills`. After each task, keep working tree limited to this repo's `docs/` paths listed in the task.

---

## Task 1: Extract `docs/site.css` and drop inline style

**Files:**
- Create: `docs/site.css`
- Modify: `docs/index.html` (stylesheet link in; delete entire `<style>...</style>` block only in this task; leave body structure for Task 2)

### Step 1: Write `docs/site.css`

Create `docs/site.css` with this exact content (lifted from this repo's inline block L21-98, plus sibling non-motion `nav.site` / brand rules; copyright names **this** repo; no keyframes, no `.brand-trace`, no `js-reveal`):

```css
/* Copyright (c) 2026 JG Systems Consulting Ltd. Source: https://github.com/jgsystemsconsulting/jgs-reference-skill. See LICENSE. */
/* SPDX-License-Identifier: MIT */
@font-face{font-family:'JetBrains Mono';font-weight:400;font-style:normal;font-display:swap;src:url('fonts/jetbrains-mono-400.woff2') format('woff2');}
@font-face{font-family:'JetBrains Mono';font-weight:700;font-style:normal;font-display:swap;src:url('fonts/jetbrains-mono-700.woff2') format('woff2');}
@font-face{font-family:'Inter';font-weight:400;font-style:normal;font-display:swap;src:url('fonts/inter-400.woff2') format('woff2');}
@font-face{font-family:'Inter';font-weight:600;font-style:normal;font-display:swap;src:url('fonts/inter-600.woff2') format('woff2');}
:root{
  --ink:#0a0a0b; --ink-2:#111113; --ink-3:#16171a; --ink-4:#1e2024;
  --line:#2a2d33; --line-2:#3a3e46;
  --mute:#6b7078; --mute-2:#8b9099;
  --text:#c7ccd3; --text-hi:#e8ebf0;
  --paper:#f4f2ec; --paper-ink:#0a0a0b;
  --mono:'JetBrains Mono',ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace;
  --sans:'Inter',ui-sans-serif,system-ui,sans-serif;
  --pad-x:clamp(24px,4vw,80px); --pad-section:clamp(48px,6vw,96px);
}
*{box-sizing:border-box;margin:0;padding:0;}
html{background:var(--ink);}
body{background:var(--ink);color:var(--mute-2);font:400 16px/1.7 var(--sans);-webkit-font-smoothing:antialiased;}
.wrap{max-width:1200px;margin:0 auto;padding:0 var(--pad-x);}
a{color:var(--text-hi);text-decoration:none;border-bottom:1px solid var(--line-2);}
a:hover{border-color:var(--paper);}
:focus-visible{outline:2px solid var(--paper);outline-offset:2px;}
.label{font:700 .6875rem/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--mute);}
h1,h2,h3{color:var(--text-hi);font-family:var(--mono);font-weight:700;letter-spacing:-0.02em;}
.masthead{border-bottom:1px solid var(--line);}
.masthead .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:.75rem 1.5rem;padding-top:14px;padding-bottom:14px;}
.masthead span{font:700 .625rem/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;color:var(--mute);}
.masthead b{color:var(--text);font-weight:700;}
nav.site{border-bottom:1px solid var(--line);}
nav.site .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:.75rem 1.5rem;padding-top:12px;padding-bottom:12px;}
nav.site a{font:700 .6875rem/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;border:0;color:var(--mute-2);}
nav.site a:hover{color:var(--text-hi);}
nav.site .brand{border:0;display:inline-flex;align-items:center;}
nav.site .brand img{display:block;}
.hero{padding:var(--pad-section) 0;border-bottom:1px solid var(--line);}
.hero h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.05;margin-bottom:1.25rem;}
.hero p{max-width:62ch;font-size:1.0625rem;color:var(--text);}
.hero .sub{margin-top:.5rem;color:var(--mute-2);}
.cta{display:flex;flex-wrap:wrap;gap:14px;margin-top:2rem;}
.btn{font:700 .8125rem/1 var(--mono);letter-spacing:.06em;text-transform:uppercase;padding:14px 20px;border:1px solid var(--line);display:inline-flex;gap:.6em;align-items:center;transition:background .15s,border-color .15s,color .15s;}
.btn-primary{background:var(--paper);color:var(--paper-ink);border-color:var(--paper);}
.btn-primary:hover{background:#fff;}
.btn-ghost{background:transparent;color:var(--text-hi);}
.btn-ghost:hover{border-color:var(--paper);}
section{padding:var(--pad-section) 0;border-bottom:1px solid var(--line);}
.shead{margin-bottom:2rem;}
.shead .label{display:block;margin-bottom:.6rem;}
.shead h2{font-size:clamp(1.4rem,3vw,2rem);}
.lead{max-width:70ch;color:var(--text);}
.grid{display:grid;gap:1px;background:var(--line);border:1px solid var(--line);}
.g3{grid-template-columns:repeat(3,1fr);}
.g2{grid-template-columns:repeat(2,1fr);}
.cell{background:var(--ink-2);padding:24px;}
.cell h3{font-size:.95rem;margin-bottom:.5rem;}
.cell p{font-size:.9375rem;color:var(--mute-2);}
.num{font:700 3rem/1 var(--mono);color:var(--line-2);display:block;margin-bottom:.5rem;}
.cell code{font:400 .8125rem var(--mono);color:var(--text);}
.sheet{background:var(--ink-2);border:1px solid var(--line);padding:24px;overflow:auto;}
.sheet pre{font:400 .875rem/1.7 var(--mono);color:var(--text);white-space:pre;}
.sheet .c{color:var(--mute);}
footer{padding:var(--pad-section) 0;}
.tblock{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--line);border:1px solid var(--line);}
.tblock div{background:var(--ink-2);padding:18px 24px;}
.tblock .label{display:block;margin-bottom:.4rem;}
.tblock b{color:var(--text);font:700 .875rem var(--mono);}
.foot-note{margin-top:1.5rem;font:400 .8125rem/1.6 var(--mono);color:var(--mute);}
@media (max-width:860px){
  .g3,.g2,.tblock{grid-template-columns:1fr;}
}
@media (prefers-reduced-motion:reduce){
  *{transition:none!important;animation:none!important;}
}
```

### Step 2: Point `index.html` at `site.css` and delete inline CSS

In `docs/index.html` head, **delete** the entire inline `<style>...</style>` block and add the `site.css` link. **Leave the `data:,` icon line untouched** for Task 2 to replace with real favicon links. For this task only, do the minimal CSS extraction:

1. Immediately after the canonical link (keep existing title/description/canonical/og basics for now), ensure this line exists once:

```html
<link rel="stylesheet" href="site.css">
```

2. Delete the entire `<style>` ... `</style>` block (current L20-99). After this step the head must contain **zero** `<style` occurrences.

Leave `link rel="icon" href="data:,"` for Task 2 (or replace early if doing Tasks 1-2 in one sitting; Task 2 owns the final favicon link set).

### Step 3: Verify Task 1

```bash
test -f docs/site.css
grep -c "@font-face" docs/site.css   # expect 4
grep -E "nav\.site|--ink:|--paper:|prefers-reduced-motion|:focus-visible" docs/site.css
grep -E "brand-trace|@keyframes|js-reveal" docs/site.css && echo "FAIL motion leaked" || echo "OK no motion"
grep -c '<style' docs/index.html     # expect 0
grep -F 'href="site.css"' docs/index.html
grep -E "fonts\.google|cdn\.|jsdelivr|unpkg" docs/site.css docs/index.html && echo FAIL || echo "OK no CDN"
```

### Step 4: Commit

```bash
git add docs/site.css docs/index.html
git commit -m "$(cat <<'EOF'
Extract docs/site.css from landing inline styles.

Move fonts, tokens, layout, and non-motion nav.site rules into an
external stylesheet so the page matches the JGSC site shell.
EOF
)"
```

---

## Task 2: `index.html` structural chrome + four-gates truth

**Files:**
- Modify: `docs/index.html` only

Do not rewrite hero/section product narrative beyond the two truth sentences named below. Keep section ids: `what-it-is`, `pipeline`, `different`, `agents`, `install`, `use`.

### Step 1: Two-line copyright / SPDX comment

Replace the single-line HTML comment at the top of `docs/index.html` with:

```html
<!doctype html>
<!-- Copyright (c) 2026 JG Systems Consulting Ltd. Source: https://github.com/jgsystemsconsulting/jgs-reference-skill. See LICENSE. -->
<!-- SPDX-License-Identifier: MIT -->
<html lang="en">
```

The source URL must name **jgs-reference-skill**, not jgs-archi-skills.

### Step 2: Head meta block (favicon + OG/Twitter + JSON-LD)

Replace the head block from charset through the old twitter tags (keep title + description + canonical text already present) so the head contains **exactly** this shape after charset/viewport/color-scheme/title/description/canonical:

```html
<link rel="icon" href="favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
<link rel="stylesheet" href="site.css">

<meta property="og:type" content="website">
<meta property="og:url" content="https://jgsystemsconsulting.github.io/jgs-reference-skill/">
<meta property="og:title" content="jgs-reference-skill">
<meta property="og:description" content="Vetted authoritative sources into licence-clean, citable knowledge packs. A fork of book-to-skill with a licence-vet gate, provenance, and verbatim-overlap detection.">
<meta property="og:image" content="https://jgsystemsconsulting.github.io/jgs-reference-skill/images/og/og-reference-skill-1200.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="jgs-reference-skill">
<meta name="twitter:description" content="Vetted authoritative sources into licence-clean, citable knowledge packs.">
<meta name="twitter:image" content="https://jgsystemsconsulting.github.io/jgs-reference-skill/images/og/og-reference-skill-1200.png">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"SoftwareApplication","name":"jgs-reference-skill","applicationCategory":"DeveloperApplication","operatingSystem":"Any","softwareVersion":"0.2.1","license":"https://github.com/jgsystemsconsulting/jgs-reference-skill/blob/main/LICENSE","url":"https://jgsystemsconsulting.github.io/jgs-reference-skill/","codeRepository":"https://github.com/jgsystemsconsulting/jgs-reference-skill","author":{"@type":"Organization","name":"JG Systems Consulting Ltd"}}
</script>
```

Rules:
- No `data:,` icon remains.
- No `site.js` script tag.
- `softwareVersion` must equal pyproject version (`0.2.1` today). If pyproject has moved, update JSON-LD + both REV cells together.
- Keep existing `<title>` and `<meta name="description" ...>` product strings; do not import Archi copy.

### Step 3: Masthead metadata only + `nav.site`

Replace the current masthead (which nests Primary nav) with:

```html
<header class="masthead"><div class="wrap">
  <span>CLASSIFICATION: <b>PUBLIC</b></span>
  <span>LICENCE: <b>MIT</b></span>
  <span>DOC-ID: <b>JGS-REF-SKILL</b></span>
  <span>REV <b>0.2.1</b></span>
</div></header>

<nav class="site" aria-label="Site"><div class="wrap">
  <a class="brand" href="index.html" aria-label="JG Systems Consulting home"><img src="images/jgs-emblem.png" alt="" width="28" height="28"></a>
  <a href="#what-it-is">What it is</a>
  <a href="#pipeline">Pipeline</a>
  <a href="#different">Different</a>
  <a href="#agents">Agents</a>
  <a href="#install">Install</a>
  <a href="#use">Use it</a>
  <a href="https://github.com/jgsystemsconsulting/jgs-reference-skill">Repository</a>
</div></nav>
```

Hard bans for this block:
- No nested `<nav>` inside masthead.
- No brand-trace `<svg>`.
- Brand img keeps `alt=""` (decorative); aria-label stays on the brand link.
- DOC-ID stays `JGS-REF-SKILL`.

### Step 4: Four-gates + `--self-check` truth fixes

**Pipeline verify cell** (section `#pipeline`, cell headed `verify`): replace the paragraph body with:

```html
<div class="cell"><span class="num">06</span><h3>verify</h3><p>Four gates: <code>check_overlap</code>, <code>validate_pack</code>, <code>pack_eval</code>, <code>scan_generated_skill</code> (overlap, pack structure, index truth, injection scan).</p></div>
```

**Use-it lead** (section `#use`, final `.lead` after the command sheet): replace the current three-gates / every-step-self-check sentence with:

```html
  <p class="lead" style="margin-top:1.5rem">The skill runs the whole pipeline for you: vet, extract, outline, scaffold, generate, and the four verification gates (<code>check_overlap</code>, <code>validate_pack</code>, <code>pack_eval</code>, <code>scan_generated_skill</code>). Prefer to run the tools by hand? The pipeline scripts that ship <code>--self-check</code> can prove themselves that way; <code>scan_generated_skill</code> is still a required gate and has no <code>--self-check</code>. See the <a href="https://github.com/jgsystemsconsulting/jgs-reference-skill/blob/main/docs/skill-usage.md">usage guide</a> for the full reference.</p>
```

After edit, the landing page must contain **zero** visible phrases claiming exactly three verification gates, and must not claim that every verify tool has `--self-check`.

### Step 5: Footer REV + Owner punctuation

In the footer `.tblock`:
- Rev cell: `<b>0.2.1</b>` (same pyproject version as masthead + JSON-LD).
- Owner cell: `<b>JG Systems Consulting Ltd</b>` with **no** trailing period inside the `<b>`.
- Leave Product, Licence, Repository, Engine, and the foot-note attribution prose unchanged (product-accurate Don't rows).

### Step 6: Verify Task 2 structure

```bash
# copyright / this repo named
head -n 4 docs/index.html
grep -F 'jgs-reference-skill' docs/index.html | head -5
grep -F 'jgs-archi-skills' docs/index.html && echo "FAIL sibling name in page" || echo "OK"

# no inline style, no site.js, no data icon
grep -c '<style' docs/index.html          # 0
grep -c 'site.js' docs/index.html         # 0
grep -c 'data:,' docs/index.html          # 0

# nav / masthead
grep -n 'aria-label="Site"' docs/index.html
grep -n 'aria-label="Primary"' docs/index.html && echo FAIL || echo "OK no Primary"
grep -n 'class="brand"' docs/index.html
grep -n 'images/jgs-emblem.png' docs/index.html
grep -n 'brand-trace' docs/index.html && echo FAIL || echo "OK no brand-trace"
# masthead has no nested nav: count nav tags == 1
grep -c '<nav' docs/index.html           # expect 1

# version lock
V=$(python -c "import re; print(re.search(r'^version\s*=\s*\"([^\"]+)\"', open('pyproject.toml',encoding='utf-8').read(), re.M).group(1))")
echo "pyproject=$V"
grep -c "REV <b>$V</b>" docs/index.html  # expect 1 (masthead)
grep -c "<span class=\"label\">Rev</span><b>$V</b>" docs/index.html  # expect 1
grep -c "\"softwareVersion\":\"$V\"" docs/index.html  # expect 1

# gates truth
grep -n 'check_overlap' docs/index.html
grep -n 'validate_pack' docs/index.html
grep -n 'pack_eval' docs/index.html
grep -n 'scan_generated_skill' docs/index.html
grep -nE 'three verification gates|Three gates' docs/index.html && echo FAIL || echo "OK no three-gates"
grep -n 'Every step is a stdlib script with a' docs/index.html && echo FAIL || echo "OK no universal self-check claim"

# owner punctuation
grep -n 'JG Systems Consulting Ltd</b>' docs/index.html   # owner cell
grep -n 'JG Systems Consulting Ltd\.</b>' docs/index.html && echo "FAIL trailing period in tblock Owner" || echo "OK"

# OG / JSON-LD shape
grep -F 'og:image' docs/index.html
grep -F 'summary_large_image' docs/index.html
grep -F 'application/ld+json' docs/index.html
grep -F 'DeveloperApplication' docs/index.html
grep -F '"operatingSystem":"Any"' docs/index.html
```

### Step 7: Commit

```bash
git add docs/index.html
git commit -m "$(cat <<'EOF'
Align landing chrome with JGSC site shell and four-gate truth.

Split nav.site, add meta/JSON-LD shape, sync REV to pyproject, and
replace stale three-gate plus universal self-check copy.
EOF
)"
```

---

## Task 3: Local assets + SC1-SC18 verification

**Files:**
- Create (copy): `docs/favicon.ico`, `docs/favicon-32x32.png`, `docs/apple-touch-icon.png`
- Create (copy): `docs/images/jgs-emblem.png`
- Create (generate): `docs/images/og/og-reference-skill-1200.png`
- Read-only verify: `docs/index.html`, `docs/site.css`, `docs/.nojekyll`, `docs/fonts/*`, `pyproject.toml`
- Must not touch: any path under `jgs-archi-skills`

### Step 1: Copy favicon set + emblem

From repo root (Git Bash). Sibling is a **read source**; runtime links stay relative under `docs/`.

```bash
mkdir -p docs/images/og
cp ../jgs-archi-skills/docs/favicon.ico docs/favicon.ico
cp ../jgs-archi-skills/docs/favicon-32x32.png docs/favicon-32x32.png
cp ../jgs-archi-skills/docs/apple-touch-icon.png docs/apple-touch-icon.png
cp ../jgs-archi-skills/docs/images/jgs-emblem.png docs/images/jgs-emblem.png
# size sanity (match sibling bytes on this machine)
wc -c docs/favicon.ico docs/favicon-32x32.png docs/apple-touch-icon.png docs/images/jgs-emblem.png
# expect ~3151, 306, 10168, 3397
```

If any `cp` fails: **stop and report** (blocking-discovery already required these paths).

### Step 2: Generate product-neutral 1200x630 OG PNG

**Method (primary): Pillow**, already present on this authoring machine (`PIL 12.2.0`). No new dependency in `pyproject.toml`. Solid ink fill `#0a0a0b` matching `--ink`, with a paper-colored top hairline band so the card is not a pure black void when compressed by crawlers. No Archi art, no text rasterization required.

Run from repo root:

```bash
python <<'PY'
from pathlib import Path
out = Path("docs/images/og/og-reference-skill-1200.png")
out.parent.mkdir(parents=True, exist_ok=True)
try:
    from PIL import Image
except ImportError:
    raise SystemExit("PIL_MISSING")
# ink #0a0a0b, paper hairline #f4f2ec (token parity; product-neutral)
ink = (10, 10, 11)
paper = (244, 242, 236)
im = Image.new("RGB", (1200, 630), ink)
# 4px paper rule under a top pad, full width
for y in range(48, 52):
    for x in range(1200):
        im.putpixel((x, y), paper)
# small 28x28 paper square as abstract mark (not the emblem binary redraw)
for y in range(280, 308):
    for x in range(586, 614):
        im.putpixel((x, y), paper)
im.save(out, format="PNG", optimize=True)
print("wrote", out, out.stat().st_size, "bytes")
assert out.stat().st_size > 100
PY
```

**Method (fallback if `PIL_MISSING`): pure stdlib zlib+struct minimal RGB PNG.** Use this exact script; do not add deps; do not shell out to ImageMagick/inkscape:

```bash
python <<'PY'
import struct, zlib
from pathlib import Path

def chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

w, h = 1200, 630
ink = (10, 10, 11)
paper = (244, 242, 236)
rows = []
for y in range(h):
    row = bytearray()
    row.append(0)  # filter None
    for x in range(w):
        if 48 <= y < 52 or (280 <= y < 308 and 586 <= x < 614):
            row.extend(paper)
        else:
            row.extend(ink)
    rows.append(bytes(row))
raw = b"".join(rows)
ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)  # 8-bit RGB
png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
out = Path("docs/images/og/og-reference-skill-1200.png")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_bytes(png)
print("wrote", out, len(png), "bytes (stdlib)")
assert out.stat().st_size > 100
# sanity: signature
assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
PY
```

If primary raises `PIL_MISSING`, run the fallback immediately in the same step. If both fail: **BLOCKED** (report to controller). Do not commit a 1x1 stub or reuse sibling `og-skills-1200.jpg`.

Verify dimensions without requiring PIL on the verify side when possible:

```bash
python <<'PY'
from pathlib import Path
p = Path("docs/images/og/og-reference-skill-1200.png")
b = p.read_bytes()
assert b[:8] == b"\x89PNG\r\n\x1a\n", "bad signature"
# IHDR width/height at fixed offsets after 8-sig + 4-len + 4-type
import struct
w, h = struct.unpack(">II", b[16:24])
print("og", w, h, "bytes", len(b))
assert (w, h) == (1200, 630)
PY
```

### Step 3: Final verification battery (SC1-SC18)

Run from repo root. Every criterion has a checkable command. All must pass before the commit.

```bash
set -euo pipefail
git -C ../jgs-archi-skills status --porcelain > /tmp/sib-before.txt
# --- SC1: index exists, lang=en, site.css linked, no <style> ---
test -s docs/index.html
grep -F 'lang="en"' docs/index.html
grep -F 'href="site.css"' docs/index.html
grep -c '<style' docs/index.html | grep -qx 0

# --- SC2: site.css fonts, tokens, required rule families ---
test -s docs/site.css
grep -c "@font-face" docs/site.css | grep -qx 4
grep -E "fonts/jetbrains-mono-400|fonts/jetbrains-mono-700|fonts/inter-400|fonts/inter-600" docs/site.css
grep -E "--ink:|--line:|--mute:|--text:|--paper:|--mono:|--sans:|--pad-x:|--pad-section:" docs/site.css
grep -E "\.masthead|nav\.site|\.hero|section|\.grid|\.cell|\.sheet|\.tblock|:focus-visible|prefers-reduced-motion" docs/site.css
grep -E "brand-trace|@keyframes|js-reveal" docs/site.css && exit 1 || true

# --- SC3: masthead metadata only; DOC-ID; REV == pyproject ---
V=$(python -c "import re; print(re.search(r'^version\s*=\s*\"([^\"]+)\"', open('pyproject.toml',encoding='utf-8').read(), re.M).group(1))")
grep -F 'DOC-ID: <b>JGS-REF-SKILL</b>' docs/index.html
grep -F "REV <b>$V</b>" docs/index.html
grep -F "<span class=\"label\">Rev</span><b>$V</b>" docs/index.html
# nested primary nav gone (nav.site lives outside <header>; exactly one <nav total)
test "$(grep -c '<nav' docs/index.html)" = 1
sed -n '/masthead/,/<\/header>/p' docs/index.html | grep '<nav' && exit 1 || true

# --- SC4: nav.site Site label, six anchors, Repository ---
grep -F 'nav class="site" aria-label="Site"' docs/index.html
grep -F 'href="#what-it-is"' docs/index.html
grep -F 'href="#pipeline"' docs/index.html
grep -F 'href="#different"' docs/index.html
grep -F 'href="#agents"' docs/index.html
grep -F 'href="#install"' docs/index.html
grep -F 'href="#use"' docs/index.html
grep -F 'href="https://github.com/jgsystemsconsulting/jgs-reference-skill">Repository</a>' docs/index.html

# --- SC5: real local favicons, not data:, ---
grep -F 'href="favicon.ico"' docs/index.html
grep -F 'href="favicon-32x32.png"' docs/index.html
grep -F 'href="apple-touch-icon.png"' docs/index.html
grep -c 'data:,' docs/index.html | grep -qx 0
test -f docs/favicon.ico && test -f docs/favicon-32x32.png && test -f docs/apple-touch-icon.png

# --- SC6: OG image + dims + twitter large image ---
grep -F 'property="og:image" content="https://jgsystemsconsulting.github.io/jgs-reference-skill/images/og/og-reference-skill-1200.png"' docs/index.html
grep -F 'property="og:image:width" content="1200"' docs/index.html
grep -F 'property="og:image:height" content="630"' docs/index.html
grep -F 'name="twitter:card" content="summary_large_image"' docs/index.html
grep -F 'name="twitter:image" content="https://jgsystemsconsulting.github.io/jgs-reference-skill/images/og/og-reference-skill-1200.png"' docs/index.html

# --- SC7: JSON-LD SoftwareApplication locked fields + version ---
grep -F 'application/ld+json' docs/index.html
grep -F '"@type":"SoftwareApplication"' docs/index.html
grep -F '"name":"jgs-reference-skill"' docs/index.html
grep -F '"applicationCategory":"DeveloperApplication"' docs/index.html
grep -F '"operatingSystem":"Any"' docs/index.html
grep -F "\"softwareVersion\":\"$V\"" docs/index.html
grep -F '"license":"https://github.com/jgsystemsconsulting/jgs-reference-skill/blob/main/LICENSE"' docs/index.html
grep -F '"url":"https://jgsystemsconsulting.github.io/jgs-reference-skill/"' docs/index.html
grep -F '"codeRepository":"https://github.com/jgsystemsconsulting/jgs-reference-skill"' docs/index.html
grep -F '"name":"JG Systems Consulting Ltd"' docs/index.html

# --- SC8: four gate tool names present ---
grep -F 'check_overlap' docs/index.html
grep -F 'validate_pack' docs/index.html
grep -F 'pack_eval' docs/index.html
grep -F 'scan_generated_skill' docs/index.html
grep -Fi 'Four gates' docs/index.html

# --- SC9: no three-gate claim ---
grep -nEi 'three verification gates|Three gates:' docs/index.html && exit 1 || true

# --- SC10: no unqualified every-tool --self-check claim ---
grep -n 'Every step is a stdlib script with a' docs/index.html && exit 1 || true
# positive: scan called out as lacking self-check
grep -F 'scan_generated_skill' docs/index.html | grep -F 'self-check' >/dev/null

# --- SC11: local fonts only ---
test -f docs/fonts/jetbrains-mono-400.woff2
test -f docs/fonts/jetbrains-mono-700.woff2
test -f docs/fonts/inter-400.woff2
test -f docs/fonts/inter-600.woff2
grep -Ei 'fonts\.googleapis|fonts\.gstatic|cdn\.jsdelivr|unpkg\.com|fontshare|typekit' docs/index.html docs/site.css && exit 1 || true

# --- SC12: no build tooling; .nojekyll remains ---
test -f docs/.nojekyll
test ! -f docs/package.json
test ! -f package.json || ! grep -q 'docs' package.json 2>/dev/null || true
# no new bundler configs introduced by this package
git status --short | grep -E 'vite|webpack|esbuild|parcel|tailwind' && exit 1 || true

# --- SC13: sibling tree gains no NEW dirty entries from this work ---
git -C ../jgs-archi-skills status --porcelain > /tmp/sib-after.txt
diff /tmp/sib-before.txt /tmp/sib-after.txt && echo "OK sibling clean"

# --- SC14: no site.js motion port / no brand-trace markup ---
test ! -f docs/site.js
grep -n 'site.js\|brand-trace' docs/index.html docs/site.css && exit 1 || true

# --- SC15: emblem file + wiring ---
test -f docs/images/jgs-emblem.png
grep -F 'src="images/jgs-emblem.png"' docs/index.html
grep -F 'alt=""' docs/index.html | grep -F 'jgs-emblem' >/dev/null || grep -F 'images/jgs-emblem.png" alt=""' docs/index.html
grep -F 'aria-label="JG Systems Consulting home"' docs/index.html

# --- SC16: Owner cell no trailing period inside <b> ---
grep -F '<span class="label">Owner</span><b>JG Systems Consulting Ltd</b>' docs/index.html
grep -F '<span class="label">Owner</span><b>JG Systems Consulting Ltd.</b>' docs/index.html && exit 1 || true

# --- SC17: two-line copyright names this repo ---
head -n 3 docs/index.html | grep -F 'Source: https://github.com/jgsystemsconsulting/jgs-reference-skill'
head -n 4 docs/index.html | grep -F 'SPDX-License-Identifier: MIT'
head -n 3 docs/index.html | grep -F 'jgs-archi-skills' && exit 1 || true

# --- SC18: runtime assets exist as relative files under docs/ ---
test -f docs/site.css
test -f docs/favicon.ico
test -f docs/favicon-32x32.png
test -f docs/apple-touch-icon.png
test -f docs/images/jgs-emblem.png
test -f docs/images/og/og-reference-skill-1200.png
# og meta is absolute Pages URL (intentional exception); file itself is local
python - <<'PY'
import struct
from pathlib import Path
b = Path("docs/images/og/og-reference-skill-1200.png").read_bytes()
assert b[:8] == b"\x89PNG\r\n\x1a\n"
w, h = struct.unpack(">II", b[16:24])
assert (w, h) == (1200, 630), (w, h)
print("SC18 og ok", w, h)
PY

echo "ALL SC1-SC18 CHECKS PASSED"
```

### Step 4: Acceptance checklist (map SC → task evidence)

| SC | Requirement (short) | Evidence command / artifact |
|---:|---|---|
| 1 | `index.html` + `site.css` link, no `<style>` | Task 1 Step 3; Task 3 SC1 block |
| 2 | `site.css` fonts, tokens, layout families | Task 1 file body; Task 3 SC2 |
| 3 | Masthead metadata; DOC-ID; REV=pyproject | Task 2 Steps 3/5; Task 3 SC3 |
| 4 | `nav.site` + anchors + Repository | Task 2 Step 3; Task 3 SC4 |
| 5 | Local favicon links | Task 2 Step 2; Task 3 Steps 1+SC5 |
| 6 | OG image + 1200x630 + twitter large | Task 2 Step 2; Task 3 Steps 2+SC6 |
| 7 | JSON-LD SoftwareApplication locked | Task 2 Step 2; Task 3 SC7 |
| 8 | Four gate tool names | Task 2 Step 4; Task 3 SC8 |
| 9 | No three-gate phrase | Task 2 Step 4; Task 3 SC9 |
| 10 | No universal `--self-check` claim | Task 2 Step 4; Task 3 SC10 |
| 11 | Local fonts only | Pre-existing `docs/fonts/`; Task 3 SC11 |
| 12 | Static only; `.nojekyll` | Task 3 SC12 |
| 13 | Sibling unmodified | Task 3 SC13 |
| 14 | No `site.js` / brand-trace | Tasks 1-2 bans; Task 3 SC14 |
| 15 | Emblem file + brand img a11y | Task 3 Step 1; Task 2 Step 3; SC15 |
| 16 | Owner without trailing period | Task 2 Step 5; SC16 |
| 17 | Two-line copyright, this repo URL | Task 2 Step 1; SC17 |
| 18 | Relative assets on disk; OG meta absolute | Task 3 Steps 1-2; SC18 |

### Step 5: Commit

```bash
git add docs/favicon.ico docs/favicon-32x32.png docs/apple-touch-icon.png \
  docs/images/jgs-emblem.png docs/images/og/og-reference-skill-1200.png
# include any residual docs/index.html / docs/site.css fixes if verification forced a tweak
git add docs/index.html docs/site.css 2>/dev/null || true
git status --short
# confirm no jgs-archi-skills paths staged
git status --short | grep archi-skills && exit 1 || true
git commit -m "$(cat <<'EOF'
Add local site icons, emblem, and product-neutral OG card.

Copy JGSC favicon and emblem binaries into docs/ and generate a
1200x630 ink-token PNG for social meta without a site build step.
EOF
)"
```

---

## Out of scope (do not do)

- `docs/site.js`, scroll reveal, brand-trace SVG, keyframes port (P7).
- New pages (`guide.html`, engage, diagrams) or multi-page IA.
- Content rewrite of hero, agent matrix, install commands, foot-note legal prose beyond Owner punctuation and the two gate-truth sentences.
- Any file write under `jgs-archi-skills`.
- Version bump of the package, CHANGELOG entry, or release-standard audit (P9).
- CDN fonts, npm/bundler, GitHub Actions site workflow.
- Reusing sibling `images/og/og-skills-1200.jpg`.

## Self-review (author)

- **Spec coverage:** Goals 1-6 and SC1-SC18 each map to a task step or verify command above.
- **No motion leak:** site.css excerpt excludes keyframes / brand-trace / js-reveal; verify greps fail closed if they appear.
- **Version single source:** masthead REV, footer Rev, JSON-LD `softwareVersion` all read from pyproject via `$V` checks.
- **OG method pinned:** PIL primary; zlib+struct stdlib fallback fully specified; sibling Archi JPG forbidden.
- **Sibling read-only:** copy via `cp` into this repo; SC13 porcelain check on sibling path.
- **Em dashes:** none in this plan body.
