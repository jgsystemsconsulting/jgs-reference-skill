<!-- Copyright (c) 2026 JG Systems Consulting Ltd. — MIT License (see LICENSE). SPDX-License-Identifier: MIT -->

# Attribution

`jgs-reference-skill` is a fork of **[book-to-skill](https://github.com/virgiliojr94/book-to-skill)**
by **virgiliojr94**, used under the MIT License (© 2025 virgiliojr94).

## What is reused verbatim

The text-extraction engine is vendored unchanged so the proven, boring part
(PDF/EPUB/DOCX/HTML/RTF/Calibre parsing with graceful fallbacks) is not rewritten:

- `book_to_skill/` — the extractor package (parsers, dependency probing, CLI)
- `scripts/extract.py` — the entry-point wrapper

Their original MIT notice is retained at `book_to_skill/LICENSE.upstream.md`.

## What jgs-reference-skill adds (the improvements)

book-to-skill produces **personal study skills** from books. jgs-reference-skill
produces **publishable, licence-clean reference packs** from authoritative sources,
adding what book-to-skill has none of:

| Theme | Added |
|---|---|
| **Provenance & licence safety** | `tools/vet_source.py` (Tier 1/2/3/Excluded gate), `tools/build_pack.py` (provenance scaffold), `tools/check_overlap.py` (verbatim-overlap detector) |
| **Trust & verification** | citation-grounded chapters, required `Scope & Limits`, `tools/pack_eval.py` (index-truth check) |
| **Pack-standard output** | `PACK.yaml` + per-pack `LICENSE`, `tools/validate_pack.py`, first-class **signpost** output |
| **Engineering ergonomics** | `tools/outline.py` (deterministic offsets), hash/idempotent re-runs, light pack-eval |

The `PACK.yaml`/`validate_pack`/`SOURCE-VETTING` conventions are themselves adapted
from **jgs-se-knowledge-packs** (MIT, © 2026 JG Systems Consulting Ltd.), where this
build method was developed by hand across ~16 packs.
