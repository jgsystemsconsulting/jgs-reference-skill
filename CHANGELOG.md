<!-- Copyright (c) 2026 JG Systems Consulting Ltd. MIT License (see LICENSE). SPDX-License-Identifier: MIT -->

# Changelog

## 0.3.0 - 2026-09-25

First cut carrying the 2026-09-24 review: every review finding landed as a
numbered package (P1-P6), the landing page aligned to the JGSC site standard
(P8), and the release standard re-run over the finished tree (P9). Test suite
grew from 452 to 543 passed (5 skipped, POSIX-only).

### Added
- CI `tests` job (P1): pytest, the five-tool self-check loop, and a compile
  smoke on every push and PR; CONTRIBUTING documents the matching local
  runbook. See the RR-S-12 deviation note below.
- Scaffold hardening (P2): `build_pack` slug validation and containment under
  the out-dir, safe YAML emission, single provenance template;
  `validate_pack` rejects TODO/stub provenance.
- Licence matching (P3): `vet_source` licence-family matching is
  boundary-aware, ending mit/apache/bsd substring false Tier 2 results.
- Verify gates (P4): `pack_eval` fails closed on a missing or empty Topic
  Index and on ungroundable terms; `scan_generated_skill` joins Step 9 as a
  fourth gate; SKILL.md and README gate lists say four.
- Installer (P5): namespace and config-dir containment with
  validate-then-install ordering, payload adds `pyproject.toml` so
  `pip install -e ".[all]"` works from the installed tree, install-path and
  workdir docs synced (`BOOK_SKILL_WORKDIR` documented).
- Provenance guard (P6): RELEASE-INFO `Source-Commit` must be a real ancestor
  of HEAD, undecodable RELEASE-INFO is a gate error, regression suite
  included.
- Website (P8): landing page aligned to the JGSC site shell; CSS extracted to
  `docs/site.css`, local icons and emblem, product-neutral OG card, four-gate
  wording.
- Release-standard hygiene (P9): `docs/DISTRIBUTION.md` channel ledger, root
  `SKILLS.md` index, host manifests (`.cursor-plugin/`,
  `gemini-extension.json`, `.agents/plugins/marketplace.json`), PR template
  and improvement issue form.

### Fixed
- Version drift: CITATION.cff, README badge, and agent-install prompt now
  agree with RELEASE-INFO / pyproject / plugin manifests / landing (P9).
- SECURITY.md supported-versions table tracks the current line (P9; backlog
  b-04 closed).
- `scripts/check_release.py`: explicit forbidden-paths class, RR-B-37 escape
  guard with a frozen `docs/superpowers/` baseline, version agreement for
  CITATION/README.
- Landing `#usage` anchor compatibility; README Support names bug vs
  improvement vs security channels; Codex install path documented.

### Notes
- **RR-S-12 deviation (dated 2026-09-24):** the standard CI verify line says
  no step executes checked-out repository code. Since P1, the `tests` job
  deliberately runs pytest, tools `--self-check`, and `py_compile` under
  `pull_request` semantics with `permissions: read-all` and no secrets. The
  read-only `integrity` job is unchanged. Fork PRs gain no write access.
  Revisit only if GitHub changes pull_request token semantics.
- Publish-time follow-ups remain open: GitHub Release objects (v0.2.1 and
  this tag), About/topic polish, directory submissions (see
  `docs/DISTRIBUTION.md`).

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
