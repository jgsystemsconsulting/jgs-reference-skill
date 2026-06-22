<!--
Copyright (c) 2026 JG Systems Consulting Ltd. — MIT License (see ../LICENSE).
Adapted from jgs-se-knowledge-packs/docs/PACK-SPEC.md (MIT).
-->

# Pack Specification

A **reference pack** is a self-contained, installable agent skill built from one
vetted, redistributable source. It follows the
[Agent Skills](https://github.com/agentskills/agentskills) `SKILL.md` convention, so
it loads in Claude Code, GitHub Copilot CLI, and Amp without modification.

## Required layout

```
packs/<slug>/
├── SKILL.md          REQUIRED. Always-loaded index: frontmatter + core frameworks
│                       + chapter index + topic index. Keep body < ~4,000 tokens.
├── PACK.yaml         REQUIRED. Provenance + licence metadata (schema below).
├── LICENSE           REQUIRED. Reproduces the SOURCE's licence/terms.
├── chapters/         REQUIRED. On-demand chapter files, chNN-<slug>.md.
├── glossary.md       optional — key terms, alphabetical, with chapter refs.
├── patterns.md       optional — concrete techniques (when / how / trade-offs).
└── cheatsheet.md     optional — decision rules, selection tables, tells & smells.
```
Signpost packs (`kind: signpost` in PACK.yaml) require only `SKILL.md` + `PACK.yaml`.

## `SKILL.md` rules

- **YAML frontmatter**: `name` (= folder slug) and a `description` that states what
  the pack covers **and its scope limits** (be honest about what the source is thin on).
- Body order (most important first — hosts truncate from the end on compaction):
  `How to Use This Skill` → `Core Frameworks & Mental Models` (~2,000 tokens, a
  toolkit not a summary) → `Chapter Index` (links every `chapters/chNN-*.md`) →
  `Topic Index` (alphabetical term → chapter routing) → `Supporting Files` →
  `Scope & Limits` (**required**: what the pack does *not* cover; which source version).
- Every `chapters/` link must resolve to a real file (`validate_pack.py` checks this).

## Chapter file rules

Reference depth: `Core Idea`, `Frameworks Introduced` (cite source section),
`Key Concepts`, `Mental Models`, `Anti-patterns` (only if the source names them),
`Key Takeaways`, `Connects To`. **Ground every claim in the source slice — do not
invent frameworks the source does not contain.** Synthesize compactly; never copy
long verbatim passages (`check_overlap.py` enforces this).

## `PACK.yaml` schema

See [`../templates/PACK.yaml`](../templates/PACK.yaml). Mandatory fields:
`slug`, `title`, `publisher`, `license`, `license_tier` (∈ {1,2,3}), `commercial_use`.
**No `source_url` is stored or published** — the source is identified textually
(title + publisher + version), and `publisher` carries the attribution.

## Validation

```bash
python3 tools/validate_pack.py packs/<slug>     # structure + provenance + tier
python3 tools/check_overlap.py --source <full_text.txt> --pack packs/<slug>   # no verbatim
python3 tools/pack_eval.py --pack packs/<slug>  # topic-index routes are grounded
```
