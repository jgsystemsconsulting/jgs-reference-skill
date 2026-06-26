---
name: jgs-reference-skill
description: "Converts an authoritative reference document (standard, handbook, guidebook, framework: PDF/EPUB/DOCX/HTML/MD/RTF) into a licence-clean, citable knowledge pack: a progressive-disclosure agent skill with SKILL.md + chapters + glossary + patterns + cheatsheet, plus PACK.yaml provenance and a per-pack LICENSE. Use when you want a trustworthy reference oracle over a vetted open source (not study notes). Vets the source's licence FIRST and refuses to package non-redistributable (paywalled/all-rights-reserved) sources, routing them to a citation-only signpost instead."
---

<!--
Copyright (c) 2026 JG Systems Consulting Ltd. MIT License (see LICENSE). SPDX-License-Identifier: MIT

Fork of book-to-skill (MIT, © 2025 virgiliojr94): extraction engine vendored
verbatim in book_to_skill/. jgs-reference-skill repositions it from "personal study
skills" to "publishable, licence-clean reference packs", and adds: a licence-vet
gate, provenance/LICENSE emission, deterministic outlining, verbatim-overlap
detection, index-truth eval, and signpost mode. See ATTRIBUTION.md.
Tool paths below are relative to this skill's own directory.
-->

# jgs-reference-skill: authoritative source → citable knowledge pack

Turn a vetted reference document into a **reference oracle**: an agent skill that
answers "what does this body of knowledge say about X?" from the actual source,
with provenance and licence baked in, never a hallucination, never a photocopy.

## When to use

Use this skill when the user wants to:
- **build a reference pack** from a standard, handbook, guidebook, or framework
  ("turn this PDF into a skill", "make a pack from the NASA SE Handbook");
- **vet a source's licence** before packaging it ("can I redistribute this?");
- **add a new source** to an existing pack, or produce a **signpost** for a source
  that is authoritative but not redistributable (ISO/IEC/IEEE, OMG, INCOSE…).

Do **not** use it for personal study notes over a copyrighted book; that is
[book-to-skill](https://github.com/virgiliojr94/book-to-skill)'s job. This skill is
for *publishable, licence-clean* reference oracles.

## Prerequisites

- **Python ≥ 3.9** on `PATH` (`python3` or `python`).
- Optional extraction dependencies, installed on demand by `scripts/extract.py`
  (`pip install -e ".[all]"` for every format; plain text/Markdown/HTML need none).
- The source's **title, publisher, and licence**, required for vetting (Step 1) and
  provenance. Ask the user if not provided.

## Philosophy

A reference pack differs from a study skill in three ways, and every step below
exists to enforce one of them:

1. **Licence-clean by construction.** The pack is *published*, so the source must
   be redistributable. Vetting is the **first** step, not an afterthought; an
   Excluded source is refused, not packaged.
2. **Grounded, not invented.** Every framework named in the pack must actually
   appear in the source. Synthesize compactly; **never reproduce long verbatim
   passages** (a quality rule *and* a licence-safety rule, enforced mechanically).
3. **Honest about scope.** The pack states what its source is *thin on*. A
   reference oracle that won't admit its limits is worse than none.

It keeps book-to-skill's proven shape: front-loaded `SKILL.md`, on-demand
chapters, decision-layer cheatsheet, because that part works.

---

## Modes

| Mode | Trigger | Path |
|---|---|---|
| **Full pack** (default) | a document path/glob for a redistributable source | Steps 0–10 |
| **Signpost** | source is Excluded, or user asks for "citation-only" | Step 1 → Signpost Workflow |
| **Analyze only** | "analyze" / "preview before generating" | Steps 0–4, emit report, stop |
| **Update / fold-in** | new source(s) for an existing pack | Step 1 → Update Workflow |

The tool paths assume this skill lives at `<SKILL_DIR>`. Run Python as `python3`
(fall back to `python`).

---

## Step 0: Inputs

If no path is given, stop:
> "jgs-reference-skill needs a source document path, folder, or glob, plus the
> source's publisher and licence so it can be vetted."

Identify: `INPUT_PATHS`, optional `SLUG`, and the source's **title / publisher /
licence** (ask if not given; they are required for vetting and provenance).

## Step 1: VET THE SOURCE FIRST (the gate)

Before extracting anything, classify the licence:

```bash
python3 <SKILL_DIR>/tools/vet_source.py \
  --title "<title>" --publisher "<publisher>" --license "<licence if known>" --json
```

- **Exit 2 / `excluded: true`** → the source is read-and-cite-only (ISO/IEC/IEEE,
  INCOSE, OMG specs, PMBOK, TOGAF, MITRE, Wiley…). **Do not build a pack.** Switch
  to the **Signpost Workflow**.
- **Tier 1/2/3** → keep the returned `license_tier`, `commercial_use`,
  `share_alike`, `attribution_required`, which fill `PACK.yaml` later. Surface any
  warnings to the user (e.g. US-gov works that quote third-party ISO text; quote
  none of it).

If the user disputes the verdict, they may override on Step 5, but the override
must be justified in `PACK.yaml` `notes`. See `docs/SOURCE-VETTING.md` for the rubric.

## Step 2: Validate & extract

Confirm at least one supported file exists, then extract with the vendored engine:

```bash
python3 <SKILL_DIR>/scripts/extract.py $INPUT_PATHS --mode <technical|text> --install-missing ask
```

`technical` (Docling, structure-aware: tables/code/formulas) for standards and
handbooks; `text` (fast) for prose. Output lands in
`<tempdir>/book_skill_work/{full_text.txt,metadata.json}`. Read `metadata.json`
for pages/words/tokens and present a quick cost estimate before generating.

## Step 3: Outline deterministically

Map structure once, exactly; don't grep for headings ad hoc:

```bash
python3 <SKILL_DIR>/tools/outline.py --source <full_text.txt> --out outline.json
```

`outline.json` gives each section's `start_char`/`end_char`/`start_line`/`end_line`
and `est_tokens`. Slice chapters from these offsets so each chapter file is built
from a precise, non-overlapping range. For sources > ~50k tokens, read slices via
offsets instead of loading `full_text.txt` whole.

**Analyze-only mode stops here**: emit the extraction report (title, author,
frameworks found, chapters detected, suggested slug + tier) and stop.

## Step 4: Purpose & depth

Ask what the pack is for (apply frameworks / think with the models / reference
chapters). Reference packs default to `DEPTH=reference` (lean, decision-ready
chapters). Use `DEPTH=study` only if the user wants worked examples.

## Step 5: Scaffold with provenance (the vet result becomes metadata)

```bash
python3 <SKILL_DIR>/tools/build_pack.py --slug <slug> \
  --title "<title>" --publisher "<publisher>" --version "<version>" \
  --license "<exact source licence>" --out-dir packs
```

This re-runs the vet gate (refusing Excluded sources), then creates
`packs/<slug>/` with `chapters/`, a pre-filled `PACK.yaml` (tier + flags inferred
from the licence), and a `LICENSE` stub to complete. Fill the `PACK.yaml` TODOs
(`source_pages`, `chapters`, `built_on`, `notes`) and reproduce the source's terms
in `LICENSE`.

## Step 6: Generate chapters (reference depth, grounded)

For each section in `outline.json`, read its slice and write
`packs/<slug>/chapters/ch<NN>-<slug>.md`:

```markdown
# Chapter N: <Title>
## Core Idea
<the single most important thing this chapter establishes (1–2 sentences)>
## Frameworks Introduced
- **<exact name from the source>**: when to use / how (steps or criteria). [§<source section>]
## Key Concepts
- **<term>**: <one-sentence precise definition>
## Mental Models
<2–4 "use X when Y" thinking tools>
## Anti-patterns *(only if the source names them)*
- **<what to avoid>**: <why it fails>
## Key Takeaways
1–7 decision-ready insights a practitioner must remember
## Connects To
- **Ch N** / **<external standard>**: <relationship>
```

Rules: **ground every framework in the slice**: if the source doesn't contain it,
it does not go in. Cite the source section where practical. Synthesize; never copy
long passages. Density beats length.

## Step 7: Supporting files

- `glossary.md`: every significant term, alphabetical, `**Term**: def (Ch N)`.
- `patterns.md`: concrete techniques: `## Name / When / How / Trade-offs`.
- `cheatsheet.md`: the **decision layer**: "when X do Y because Z", selection
  tables, thresholds, tells & smells. Not term→definition (that's the glossary).

## Step 8: Write the pack's SKILL.md

Front-load it (hosts truncate from the end), body order:
`## How to Use This Skill` → `## Core Frameworks & Mental Models` (~2,000 tokens,
the toolkit) → `## Chapter Index` (table linking every `chapters/chNN-*.md`) →
`## Topic Index` (alphabetical term → chapter routing (how the agent navigates)) →
`## Supporting Files` → `## Scope & Limits` (**required**: what the source is thin
on + which source version). Frontmatter `name:` must equal `<slug>`; `description`
must state coverage **and** scope limits.

## Step 9: VERIFY (three gates, all must pass)

```bash
# (a) licence-safety + quality: no verbatim passages lifted from the source
python3 <SKILL_DIR>/tools/check_overlap.py --source <full_text.txt> --pack packs/<slug>
# (b) structure + provenance: required files, frontmatter, links, PACK.yaml fields, tier
python3 <SKILL_DIR>/tools/validate_pack.py packs/<slug>
# (c) index truth: every Topic-Index route is grounded in the chapter it points to
python3 <SKILL_DIR>/tools/pack_eval.py --pack packs/<slug>
```

Any verbatim overlap → paraphrase and re-run (this is the by-hand fix, automated).
Any validate failure → fix structure/provenance. Any mis-route → fix the index.
Do not report the pack as done until all three are green.

## Step 10: Report & clean up

Remove `<tempdir>/book_skill_work/`. Report: pack path, source + tier, chapter
count, the three gate results, and how to install (`cp -r packs/<slug>
~/.claude/skills/<slug>`).

---

## Signpost Workflow (Excluded sources)

When Step 1 returns Excluded, build a **citation-only signpost**, with zero source
content reproduced:

- `packs/<slug>/PACK.yaml` with `kind: signpost`, `license: "MIT"` (the signpost
  text is *your* original writing), and a `notes:` block stating it contains no
  source content and why the source is Excluded.
- `packs/<slug>/SKILL.md` listing, per source: designation, title, one-line
  purpose, owning body, redistributability status, and the official catalogue/deed
  URL **only where the licence permits citation**. No transformed source text.
- Validate with `validate_pack.py` (it applies the reduced signpost rubric; no
  `chapters/` required).

This is how authoritative-but-paywalled standards (ISO/IEC/IEEE, OMG, INCOSE) are
honoured without breaching their terms.

## Update / Fold-in Workflow

For new source(s) into an existing pack: vet the new source (Step 1), extract +
outline it (Steps 2–3), then merge: revise existing chapters in place or add
`chNN` files after the highest existing number; merge `glossary`/`patterns`/
`cheatsheet`; bump `PACK.yaml` `chapters`/`source_pages`/`built_on` and add the new
source to `notes`; append to the Chapter & Topic indexes. Multi-source packs keep
**per-source provenance** in `notes` (e.g. Vol 1 + Vol 2), not one merged blob.
Re-run Step 9. (This mirrors book-to-skill's fold-in, with the vet gate added.)

---

## Quality Rules

1. **Vet first**: an Excluded source is never packaged; it becomes a signpost.
2. **Ground every claim**: no framework the source doesn't contain.
3. **Never copy raw text**: synthesize; `check_overlap.py` must pass.
4. **Carry licence conditions forward**: NC → `commercial_use: false`; SA → pack
   content under the source's licence; BY → attribution in `LICENSE` + `PACK.yaml`.
5. **State the thin-on**: `## Scope & Limits` is required, not optional.
6. **Front-load SKILL.md**, on-demand chapters, decision-layer cheatsheet.
7. **Topic Index is the router**, and it must be true (`pack_eval.py`).
8. **No source-material URLs in published output**: attribution travels as text
   (title + publisher + version + licence). See `docs/SOURCE-VETTING.md`.
