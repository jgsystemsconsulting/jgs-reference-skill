# reference-skill

**Turn a vetted authoritative source — a standard, handbook, guidebook, or
framework — into a licence-clean, citable knowledge pack your agent loads on
demand.** A fork of [book-to-skill](https://github.com/virgiliojr94/book-to-skill)
(MIT), repositioned from *personal study skills* to *publishable reference packs*.

## Why a fork

book-to-skill turns a book into a study skill. It has no notion of who owns the
source, whether you may redistribute it, or whether the skill quotes the original
verbatim. For **published** reference packs over authoritative sources, those are
the whole game. reference-skill keeps book-to-skill's proven output shape and adds
the provenance, licence, and verification rigor — the things you otherwise do by
hand every time.

| | book-to-skill | reference-skill |
|---|---|---|
| Target | personal study notes | publishable reference oracle |
| Licence awareness | none | **vet gate**: Tier 1/2/3/Excluded, refuses non-redistributable |
| Provenance | none | `PACK.yaml` + per-pack `LICENSE` (SPDX, tier, NC/SA flags) |
| Verbatim copying | "don't" (unchecked) | **`check_overlap.py`** flags any lifted run |
| Chapter slicing | ad-hoc grep | **`outline.py`** deterministic offsets |
| Index quality | — | **`pack_eval.py`** verifies routes are grounded |
| Unredistributable source | (would package it) | **signpost** (cite-only, zero content) |

## Pipeline

```
vet_source ──▶ extract ──▶ outline ──▶ build_pack ──▶ generate ──▶ verify
 (Tier?)       (engine)    (offsets)   (provenance)   (chapters)   overlap+validate+eval
   │
   └─ Excluded ─▶ signpost (cite-only)
```

## Quick start

```bash
# 1. Vet the source FIRST — refuses paywalled / all-rights-reserved sources
python3 tools/vet_source.py --title "NASA SE Handbook" --publisher "NASA" \
    --license "Public Domain (US Government work)"

# 2. Scaffold a pack with provenance (re-runs the gate, infers tier + flags)
python3 tools/build_pack.py --slug nasa-se-handbook \
    --title "NASA Systems Engineering Handbook (SP-2016-6105 Rev 2)" \
    --publisher "NASA" --version "Rev 2 (2016)" \
    --license "Public Domain (US Government work)"

# 3. Extract + outline, then generate the pack (agent follows SKILL.md)
python3 scripts/extract.py path/to/source.pdf --mode technical
python3 tools/outline.py --source /tmp/book_skill_work/full_text.txt --out outline.json

# 4. Verify before publishing — all three must pass
python3 tools/check_overlap.py --source /tmp/book_skill_work/full_text.txt --pack packs/nasa-se-handbook
python3 tools/validate_pack.py packs/nasa-se-handbook
python3 tools/pack_eval.py --pack packs/nasa-se-handbook
```

As an agent skill, install it where your host discovers skills (e.g.
`~/.claude/skills/reference-skill/`) and drive it conversationally — see
[SKILL.md](SKILL.md). It vets, extracts, outlines, scaffolds, generates, and runs
the three gates for you.

## What it produces

```
packs/<slug>/
├── SKILL.md        core frameworks + chapter index + topic index + scope-limits
├── PACK.yaml       provenance: title, publisher, version, licence, tier, NC/SA flags
├── LICENSE         the SOURCE's terms (independent of this repo's MIT)
├── chapters/chNN-*.md   on-demand, citation-grounded
├── glossary.md · patterns.md · cheatsheet.md
```

A pack drops straight into [jgs-se-knowledge-packs](https://github.com/jgsystemsconsulting/jgs-se-knowledge-packs)
and passes its release gates unmodified.

## Tools (all pure stdlib, all `--self-check`)

| Tool | Does |
|---|---|
| `tools/vet_source.py` | licence tier classification + Excluded hard-stop |
| `tools/build_pack.py` | vet-gated provenance scaffold |
| `tools/outline.py` | deterministic ToC + char/line offsets (JSON) |
| `tools/check_overlap.py` | verbatim n-gram overlap detector |
| `tools/validate_pack.py` | structural + licence validator (signpost-aware) |
| `tools/pack_eval.py` | topic-index-to-chapter grounding check |

## Licensing

Tooling + spec: **MIT** (© 2026 JG Systems Consulting Ltd.). Extraction engine
vendored from book-to-skill (MIT, © 2025 virgiliojr94) — see
[ATTRIBUTION.md](ATTRIBUTION.md). Packs you produce carry **their source's** licence,
not this one. Read [docs/SOURCE-VETTING.md](docs/SOURCE-VETTING.md) before packaging
anything.
