<!-- Copyright (c) 2026 JG Systems Consulting Ltd. — MIT License (see ../LICENSE). SPDX-License-Identifier: MIT -->

# Using jgs-reference-skill

## Prerequisites

- A host that reads the [Agent Skills](https://agentskills.io) `SKILL.md` format
  (Claude Code, GitHub Copilot CLI, OpenClaw natively; Codex/Gemini/Cursor via the
  installer's format transform).
- **Python ≥ 3.9** on `PATH`. Optional extraction dependencies install on demand
  (`pip install -e ".[all]"` for every format).

## Install

```bash
python install.py                 # Claude Code (default), namespaced under ~/.claude/skills/jgs/
python install.py --agent all     # every user-global agent
python install.py --list-agents   # show each agent's target path + format
```

See [other-agents.md](other-agents.md) for per-agent paths and limitations. Restart
your agent session afterwards so it discovers the new skill.

## Invoking it

Drive it conversationally, or with the slash command:

```bash
/jgs-reference-skill                                  # load the generator spec
/jgs-reference-skill build a pack from the NASA SE Handbook
/jgs-reference-skill vet "SysML" published by the Object Management Group
/jgs-reference-skill add NIST SP 800-160 Vol 2 to my nist-sse pack
```

The skill needs the source's **title, publisher, and licence** — it vets the licence
**first** (Step 1) and refuses to package non-redistributable sources, routing them to
a citation-only signpost instead.

## What it does, in order

1. **Vet** the source's licence (`tools/vet_source.py`) — Tier 1/2/3 or Excluded.
2. **Extract** text (vendored `scripts/extract.py`).
3. **Outline** deterministically (`tools/outline.py`) → exact chapter offsets.
4. **Scaffold** provenance (`tools/build_pack.py`) → `PACK.yaml` + `LICENSE`.
5. **Generate** citation-grounded chapters + glossary/patterns/cheatsheet + `SKILL.md`.
6. **Verify** three gates: `check_overlap.py` (no verbatim), `validate_pack.py`
   (structure + tier), `pack_eval.py` (index routes are grounded).

A produced pack drops straight into the JGSC `jgs-se-knowledge-packs` repository and
passes its release gates unmodified.

## Running the tools directly

Every tool is stdlib-only and self-testing:

```bash
python tools/vet_source.py --title "NASA SE Handbook" --publisher "NASA" --license "Public Domain (US Government work)"
python tools/outline.py --source /tmp/book_skill_work/full_text.txt --out outline.json
python tools/check_overlap.py --source /tmp/book_skill_work/full_text.txt --pack packs/<slug>
python tools/validate_pack.py packs/<slug>
python tools/pack_eval.py --pack packs/<slug>
```
