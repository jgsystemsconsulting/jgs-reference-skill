<!-- Copyright (c) 2026 JG Systems Consulting Ltd. MIT License (see LICENSE). SPDX-License-Identifier: MIT -->

# Changelog

## [Unreleased]

Release-standard hygiene after the 0.2.1 cut (P9). No product version bump.

### Added
- `docs/DISTRIBUTION.md` channel ledger (last reviewed 0.2.1 / 2026-09-24).
- Root `SKILLS.md` (single skill index).
- Host manifests: `.cursor-plugin/`, root `gemini-extension.json`, `.agents/plugins/marketplace.json`.
- `.github/pull_request_template.md` and `.github/ISSUE_TEMPLATE/improvement.yml`.

### Fixed
- Version drift: `CITATION.cff`, README badge, and agent-install prompt now agree at 0.2.1 with RELEASE-INFO / pyproject / plugin / landing.
- `SECURITY.md` supported-versions table tracks the 0.2.x line.
- `scripts/check_release.py`: explicit forbidden-paths class, RR-B-37 escape guard (never-track, gitignore rules, frozen `docs/superpowers/` baseline), version agreement for CITATION/README.
- Landing `#usage` anchor compatibility; README Support names bug vs improvement vs security channels.
- Codex install path documented as the deliberate prompts-path alternative.

### Notes
- **RR-S-12 deviation (dated 2026-09-24):** the standard CI verify line says no step executes checked-out repository code. Since P1, the `tests` job deliberately runs pytest, tools `--self-check`, and `py_compile` under `pull_request` semantics with `permissions: read-all` and no secrets. The read-only `integrity` job is unchanged. Fork PRs gain no write access. Revisit only if GitHub changes pull_request token semantics.
- P1-P8 product work is already on the tree around the 0.2.1 cut; this Unreleased section records post-tag standard hygiene only. Publish-time remains open: GitHub Release object for `v0.2.1` (tag exists), optional About/topic polish, directory submissions (see `docs/DISTRIBUTION.md`).

## 0.2.1 - 2026-09-24

Release-hygiene cut: land the superpowers review and packaging pipeline
artifacts, merge the outstanding vet-hardening branch, and correct release
provenance.

### Added
- `docs/superpowers/`: repository review findings and triage log (10 issues:
  2 HIGH, 8 MEDIUM; 20 advisories), the converged packages document (P1-P9),
  the routed backlog, and the P1 CI spec (pipeline in progress).

### Fixed
- `tools/vet_source.py`: Excluded list gains AFOTEC, Defense Acquisition
  Guidebook (DAG), and CMU/SEI sources (merged from branch hyg-03).
- RELEASE-INFO.txt now names a real, reachable Source-Commit, and the v0.2.1
  tag exists (v0.2.0 shipped without a tag).

## 0.2.0 - 2026-08-14

Synced the vendored extraction engine with upstream
[book-to-skill](https://github.com/virgiliojr94/book-to-skill) **v1.4.0**
(forked at v1.2.0). Fork-specific tooling (`tools/`, `templates/`, installers,
docs) is untouched.

### Updated (from upstream v1.3.0/v1.4.0)
- `book_to_skill/`: +963/−126 across 12 files, new `sanitize.py`
  (invisible/bidi Unicode scrubbing), DOCX XXE/Billion-Laughs hardening,
  subprocess argument-injection hardening, pypdf migration (PyPDF2 deprecated),
  Korean/Thai chapter detection, encoding/BOM/EPUB-spine/RTF fixes.
- `tests/`: upstream suite carried over (452 passed, 5 skipped).
  Dropped `test_publish_visibility_gate.py`: it asserts upstream SKILL.md
  publish-flow wording this fork deliberately replaced.
- Vendored upstream `tools/discovery_tax.py` and `tools/scan_generated_skill.py`
  (advisory prompt-injection scan for generated skills).

### Changed
- `pyproject.toml`: `pdf`/`all` extras PyPDF2 → pypdf; version 0.2.0.

## 0.1.0 - 2026-06-22

Initial fork of [book-to-skill](https://github.com/virgiliojr94/book-to-skill)
(MIT), repositioned from personal study skills to **publishable, licence-clean
reference packs**.

### Vendored unchanged
- `book_to_skill/` extraction engine + `scripts/extract.py` (PDF/EPUB/DOCX/HTML/RTF/Calibre).

### Added
- **`tools/vet_source.py`**: licence-vetting gate: classifies a source as Tier
  1/2/3/Excluded and hard-stops (exit 2) on non-redistributable sources.
- **`tools/check_overlap.py`**: verbatim n-gram overlap detector; fails if any run
  of ≥ N words is lifted from the source.
- **`tools/outline.py`**: deterministic ToC + char/line offsets as JSON for exact
  chapter slicing.
- **`tools/build_pack.py`**: vet-gated provenance scaffold (`PACK.yaml` + `LICENSE`).
- **`tools/validate_pack.py`**: structural + licence validator, with signpost rubric.
- **`tools/pack_eval.py`**: checks every Topic-Index route is grounded in its chapter.
- **`SKILL.md`**: reference-pack generator spec (vet, extract, outline, scaffold,
  generate, verify), with signpost and fold-in workflows.
- **`docs/PACK-SPEC.md`, `docs/SOURCE-VETTING.md`, `templates/PACK.yaml`**: the pack
  standard the generator targets.

Every tool ships a `--self-check`.
