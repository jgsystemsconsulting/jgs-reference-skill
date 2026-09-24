# Spec: P8 website-align-jgs-archi-standard

- date: 2026-09-24
- project: jgs-reference-skill
- package: P8 (docs/superpowers/packages/2026-09-24-jgs-reference-skill-packages.md)
- author-leaf: fallback (inline); Claude-pinned leaf unavailable; constraints locked at the package proposal stop
- context: ad-hoc (P8 package section; sibling standard `jgs-archi-skills/docs/index.html` 217 lines plus `site.css`, `site.js`, `fonts/`, favicons, `images/`; this repo `docs/index.html` 205 lines plus `docs/fonts/` and `docs/.nojekyll`; P4 Step 9 four-gate contract in SKILL.md L204-224; packages doc P8 in-scope handoff on verify copy at index L142 and L187)
- research: skipped (internal alignment against a sibling repo that is fully readable locally; no external APIs)

## Research

research: skipped (internal alignment against a sibling repo that is fully readable locally; no external APIs)

## Problem

The public landing page at `docs/index.html` (GitHub Pages, `.nojekyll` present) was authored ad hoc during the release-standard pass. Sibling repo `jgs-archi-skills` ships the de facto JGSC site standard: external `site.css` / `site.js`, a dedicated `nav.site` row with brand mark, richer OG/Twitter/JSON-LD and favicon set, and shared token/layout conventions. This repo was never diffed against that standard, so structure and convention drift stayed unquantified.

Separately, P4 rewrote Step 9 from three verify gates to four (`check_overlap`, `validate_pack`, `pack_eval`, `scan_generated_skill`). The landing page still says three gates in two places (pipeline cell ~L142; use-it lead ~L187). The site therefore documents a stale publish contract.

## Divergence inventory

Read against current trees on 2026-09-24. **Align** means adopt the sibling convention while keeping this repo's product copy, DOC-ID, rev, and factual claims. **Don't** means leave this repo as-is (content/brand accuracy, or out of P8 scope).

| Aspect | jgs-archi-skills convention | jgs-reference-skill current | Align? |
|---|---|---|---|
| Page shell | `<!doctype html>`, `lang="en"`, copyright + SPDX comments, `charset`, `viewport`, `color-scheme: dark` | Same shell family; single-line copyright/SPDX comment | Align (keep two-line copyright/SPDX shape if splitting matches sibling; no content rewrite) |
| CSS delivery | External `site.css` (fonts + tokens + layout + nav + tables + reduced-motion) | Inline `<style>` block (~L20-99) duplicating the same tokens and most rules | Align (extract shared base into `docs/site.css`; drop inline duplicate) |
| JS delivery | External `site.js` (defer): `js-reveal` + optional scroll reveals; respects `prefers-reduced-motion` | No JS | Don't (P7 owns motion; do not port brand-trace SVG, reveal animations, or `site.js`) |
| Design tokens | `:root` ink/line/mute/text/paper, mono/sans, pad clamps | Identical token set in the inline block | Align (reuse same token names/values in extracted CSS; do not invent a second palette) |
| Local fonts | `@font-face` Inter 400/600 + JetBrains Mono 400/700 from `fonts/*.woff2` | Same four woff2 files under `docs/fonts/`; faces declared inline | Align (keep local files; move `@font-face` into `site.css`; no CDN) |
| Favicon / app icons | `favicon.ico`, `favicon-32x32.png`, `apple-touch-icon.png` linked from head | `link rel="icon" href="data:,"` (empty data URI) | Align (add real local favicon assets under `docs/`; link like the standard; no remote icon URL) |
| Brand mark in nav | `nav.site` brand link with `images/jgs-emblem.png` (alt empty, decorative) + optional motion SVG overlay | No brand image; no `docs/images/` | Align (add local `docs/images/jgs-emblem.png` copy or equivalent JGSC emblem already owned; wire brand link on `index.html` only; **no** brand-trace SVG / motion overlay) |
| Primary nav structure | Separate `<nav class="site" aria-label="Site">` below masthead; mono uppercase links; in-page anchors + sibling HTML pages + GitHub | Nav nested inside masthead via inline-styled `<nav aria-label="Primary">` | Align (split `nav.site` out of masthead; keep this repo's section anchors and single-page shape; no multi-page Guide/Engage links unless pages already exist here) |
| Masthead | Classification / Licence / DOC-ID / Rev only | Same four fields + embedded nav | Align (masthead metadata only; move links to `nav.site`) |
| Masthead identity values | DOC-ID `JGS-ARCHI-SKILLS`, REV product version | DOC-ID `JGS-REF-SKILL`, REV `0.2.0` | Align rev only: DOC-ID stays `JGS-REF-SKILL`; REV cells (masthead + footer) sync to the pyproject version (0.2.1 today) as a truth fix |
| Hero | H1 product name, lead, sub, primary+ghost CTA | Same pattern; CTAs point at GitHub / README install | Don't on copy targets (keep this product's CTAs and wording accuracy); Align on classnames/structure already shared |
| Main sections | Numbered `§NN ·` labels, `.shead` / `.lead` / `.grid` / `.cell` / `.sheet` | Same section system and classnames; six product sections | Don't on section topics/order beyond truth fixes (content stays this product); Align only where structure/class drift is found |
| Data tables | `table.data` inside `.sheet` for layer/eval matrices | No data tables on the landing page | Don't (no requirement to invent tables) |
| Extra HTML pages | `guide.html`, `why-soam.html`, `hatherley.html`, `engage.html`, diagrams | Single `index.html` plus markdown docs | Don't (P8 is landing alignment, not a multi-page site build-out) |
| OG basic tags | `og:type`, `og:url`, `og:title`, `og:description` | Present with this product's URL/title/description | Align (keep product-specific strings; ensure tag set parity for the basics already listed) |
| OG image | `og:image` + width 1200 + height 630 pointing at `images/og/...jpg` on Pages URL | No `og:image` (or dimensions) | Align (add local `docs/images/og/` asset sized for 1200x630, or a checked-in placeholder the implementer can generate without a build step; absolute Pages URL in meta) |
| Twitter card | `summary_large_image` + title/description/image | `summary` only; no image | Align (`summary_large_image` once an OG image exists; product-specific text) |
| JSON-LD | `SoftwareApplication` block (name, category, OS, version, license, url, codeRepository, author org) | Absent | Align (add equivalent block for `jgs-reference-skill` with this repo's version, URLs, MIT license link) |
| Canonical URL | Pages root canonical | Present for this repo | Don't beyond keeping the correct product canonical |
| Footer title-block | `.tblock` 3-col grid: Product, Rev, Licence, Repository, domain-specific field, Owner | Same six-cell pattern (Engine instead of Canvas) | Align structure already met; Don't rewrite field meanings (Engine / book-to-skill stays accurate) |
| Footer note | © year, MIT, licensing URL, domain trademark note | © year, MIT tooling note, pack licence note, book-to-skill attribution, licensing link | Don't (keep this product's legal/attribution facts; prose-standard polish only if a touched sentence must change) |
| Owner punctuation | `JG Systems Consulting Ltd` (no trailing period in tblock) | `JG Systems Consulting Ltd.` (trailing period) | Align (drop trailing period in tblock Owner to match house style) |
| Accessibility: lang | `html lang="en"` | Present | Align (already met; keep) |
| Accessibility: focus | `:focus-visible` paper outline | Present in inline CSS | Align (carry into `site.css`) |
| Accessibility: nav label | `aria-label="Site"` on `nav.site` | `aria-label="Primary"` on in-masthead nav | Align (use `nav.site` + `aria-label="Site"`) |
| Accessibility: brand img | Decorative emblem `alt=""`; brand link has `aria-label` | N/A today | Align when emblem is added |
| Accessibility: reduced motion | CSS (+ JS early-return in standard) | CSS-only `prefers-reduced-motion` kills transitions | Align CSS rule in `site.css`; Don't port JS motion |
| Contrast basics | Dark ink background, mute/text/paper tokens (paper-on-ink CTAs) | Same tokens | Align (keep token contrast; no new low-contrast colors) |
| GitHub Pages | `.nojekyll` present; static files only | `.nojekyll` present; static files only | Align (keep; no build step) |
| Verify gate copy | N/A (different product) | L142 verify cell: "Three gates: ..."; L187: "the three verification gates" | Replace three-gate strings with four, e.g. cell text `Four gates: overlap, pack structure, index truth, injection scan` and lead wording `the four verification gates (check_overlap, validate_pack, pack_eval, scan_generated_skill)`; exact sentence final polish belongs to the implementer within these truth constraints | Align to **four** gates naming `check_overlap`, `validate_pack`, `pack_eval`, `scan_generated_skill` (truth fix from P4; not a content rewrite of the product story) |
| L187 `--self-check` claim | N/A | "Every step is a stdlib script with a `--self-check`" | Align (P4: `scan_generated_skill` has no `--self-check`; reword so the page does not claim every verify tool self-checks) |
| Motion / brand-trace / scroll reveal | Present via `site.js` + CSS keyframes + SVG in nav brand | Absent | Don't (P7 / packages out of scope: "motion or video assets") |
| Sibling repo files | Source of standard | Must not be modified | Don't touch `jgs-archi-skills` |

## Goals

1. **Structural alignment (accepted rows).** Refactor `docs/index.html` toward the sibling shell: masthead metadata only; separate `nav.site`; external `docs/site.css` carrying fonts, tokens, layout, nav, grids, sheet, footer, focus, and reduced-motion rules already used here. Add local favicon links and brand emblem path. Keep a single landing page (no new multi-page IA).
2. **Meta / social parity.** Add OG image tags (with dimensions), Twitter `summary_large_image` + image, and a product-accurate JSON-LD `SoftwareApplication` block. Keep canonical, description, and titles specific to jgs-reference-skill.
3. **Four-gates truth fix (P4 handoff).** Replace both stale three-gate strings so the pipeline verify cell and the use-it lead name four gates: `check_overlap`, `validate_pack`, `pack_eval`, `scan_generated_skill`. Fix the adjacent "every step has `--self-check`" overclaim so it stays true (self-check on the tools that have it; scan is gate-required without self-check).
4. **Self-contained static site.** Fonts stay local under `docs/fonts/` (reuse existing woff2). No CDN. No bundler, framework, or GitHub Actions build for the site. `.nojekyll` remains. Page must remain openable as static HTML (file:// or Pages).
5. **Content boundary.** Do not rewrite product narrative, section topics, install commands, or marketing claims except where alignment or gate-truth requires a minimal sentence edit. Do not copy jgs-archi-skills body copy, altitudes tables, or Archi-specific footer fields.
6. **Written prose standard.** Any touched durable sentences in the HTML visible copy follow the repo written prose standard (no em dashes, no Tier-1 slop). Code/CSS/HTML structure is exempt from caveman speak; visible English is normal technical prose.

## Constraints

- No frameworks, preprocessors, or site build tooling.
- No content rewrites beyond alignment and the four-gates / self-check truth fixes.
- `jgs-archi-skills` repo is read-only for this work (survey only).
- Reuse this repo's existing `docs/fonts/*.woff2`; do not re-download from a CDN at runtime.
- P7 motion assets stay out: no `site.js` reveal port, no brand-trace SVG animation, no video.
- Favicon/emblem assets must be local files under `docs/` (copying JGSC-owned sibling binaries such as the emblem and favicons is allowed; do not depend on cross-repo relative links at runtime). The sibling's `og-skills-1200.jpg` is Archi product art and is NOT reusable here: the OG card for this repo must be repo-specific or product-neutral generated art (a simple branded 1200x630 placeholder is acceptable), never the sibling's card.
- GitHub Pages compatible: static files only; keep `docs/.nojekyll`.
- Ponytail: fewest files that satisfy the accepted align rows (`index.html`, `site.css`, asset files as needed). No component system.
- Version/DOC-ID/product strings stay this repo's.

## Non-goals / out of scope

- P7 motion pack, scroll reveals, brand-trace animation, video.
- New pages (guide, engage, diagrams) or IA expansion.
- New tooling, generators, or CI site checks beyond what static file review can assert.
- Content rewrites of the product story, agent matrix, or install narrative except gate-truth and required structural chrome.
- Changes inside `jgs-archi-skills`.
- Release-standard audit (P9) and version bump decisions.

## Implementation sketch (binding intent, not a task plan)

Implementers may choose mechanical order; the end state must match success criteria.

1. Add `docs/site.css` by lifting this page's current inline CSS and merging any missing **non-motion** rules needed for `nav.site` / brand link from the sibling CSS (exclude keyframes, `.brand-trace`, `js-reveal` section reveal rules).
2. Point `index.html` at `site.css`; delete the inline `<style>` block.
3. Restructure header: masthead metadata row; sibling-style `nav.site` with this repo's six anchors + Repository external link; brand emblem (required, see SC16) linking `index.html`.
4. Add local favicon (+ optional apple-touch) files and head links; replace `data:,` icon.
5. Add OG/Twitter image meta + JSON-LD; add `docs/images/og/` (and emblem) assets as local files.
6. Edit L142-class verify cell and L187-class lead to four named gates; correct `--self-check` wording.
7. Normalize footer Owner punctuation; leave Engine / attribution facts intact.
8. Do not add `site.js` unless a future package explicitly scopes motion (not P8).

## Success criteria

Checkable from the tree and HTML source (open/read files; no browser lab required).

1. `docs/index.html` exists, non-empty, `lang="en"`, links `site.css`, and contains no `<style>` element at all (the design system lives entirely in `docs/site.css`).
2. `docs/site.css` exists and declares the four local `@font-face` rules pointing at `fonts/*.woff2`, the shared `:root` tokens (ink/line/mute/text/paper/mono/sans/pad-*), and rules for masthead, `nav.site`, hero, section, grid/cell, sheet, footer tblock, `:focus-visible`, and `prefers-reduced-motion`.
3. Masthead contains classification / licence / DOC-ID / rev only (no nested primary nav). DOC-ID remains `JGS-REF-SKILL`; the REV cells (masthead + footer) equal pyproject's version (0.2.1 today).
4. A `nav.site` element with `aria-label="Site"` lists the in-page section links needed for this landing page and a Repository link to this GitHub repo.
5. Head includes real favicon link(s) to local files under `docs/` (not `data:,` only).
6. Head includes `og:image` (absolute Pages URL under this repo), `og:image:width` 1200, `og:image:height` 630, Twitter `summary_large_image`, and matching `twitter:image`.
7. Head includes `application/ld+json` `SoftwareApplication` for `jgs-reference-skill` with url, codeRepository, MIT license URL, author organization JG Systems Consulting Ltd, `applicationCategory` (developer tool), `operatingSystem` (Any), and `softwareVersion` matching pyproject's version (0.2.1 today), which is also the REV the masthead and footer cells carry after this package (single version source: pyproject).
8. Pipeline verify copy names **four** gates and includes the identifiers `check_overlap`, `validate_pack`, `pack_eval`, and `scan_generated_skill` (exact tool names present in visible text or immediately adjacent code-style spans).
9. No remaining visible phrase claiming exactly three verification gates on the landing page.
10. No remaining visible claim that every pipeline/verify tool provides `--self-check` without qualification; wording allows scan (or any non-self-check tool) to be gate-required without self-check.
11. Fonts load only from local `docs/fonts/`; HTML/CSS contain no font CDN hostnames.
12. No new framework, bundler config, or site build step is introduced; `docs/.nojekyll` remains.
13. `jgs-archi-skills` tree is unmodified by this package's commits.
14. No `site.js` motion port and no brand-trace SVG animation markup required for P8 success.
15. Brand emblem present at `docs/images/jgs-emblem.png` (JGSC-owned binary; copying the sibling emblem file is allowed), wired as the `nav.site` brand image with `alt=""` and an `aria-label` on the brand link.
16. Footer tblock Owner cell reads `JG Systems Consulting Ltd` with no trailing period.
17. The head copyright/SPDX comment uses the two-line sibling shape and names THIS repo (`jgs-reference-skill`) in its source URL, not the sibling.
18. Page remains static: all runtime-loaded assets (CSS, fonts, icons, img src) are relative files under `docs/` that exist in the commit. Meta `og:image` / `twitter:image` content values are the exception the standard itself uses: absolute published Pages URLs (crawlers fetch social cards off-site), while the underlying image file is still a relative local asset.

## Risks / notes

- OG image binary: if no designer pass is available, a minimal checked-in 1200x630 asset still satisfies meta parity; perfect art direction is not a P8 gate.
- Emblem/favicon binaries may be reused from JGSC-owned sibling docs assets; runtime must not deep-link into the other repo.
- Extracting CSS will make sibling CSS drift possible later; P8 does not create a shared package across repos (copy, do not submodule).
- Four-gates copy must track SKILL.md Step 9; if P4 is not yet on the branch an implementer lands on, still write four gates as packages-doc P8 + P4 resolution require (site documents final behavior after P1-P6).

## References

- Packages binding scope: `docs/superpowers/packages/2026-09-24-jgs-reference-skill-packages.md` § P8
- Four-gate contract: `SKILL.md` Step 9; `docs/superpowers/specs/2026-09-24-step9-verify-gates.md`
- Standard (read-only): `jgs-archi-skills/docs/index.html`, `site.css`, `site.js`, `fonts/`, favicons, `images/`
- Target tree: `docs/index.html`, `docs/fonts/`, `docs/.nojekyll`
