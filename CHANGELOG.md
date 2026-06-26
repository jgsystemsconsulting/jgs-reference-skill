<!-- Copyright (c) 2026 JG Systems Consulting Ltd. MIT License (see LICENSE). SPDX-License-Identifier: MIT -->

# Changelog

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
