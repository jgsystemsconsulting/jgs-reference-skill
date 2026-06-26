<!-- Copyright (c) 2026 JG Systems Consulting Ltd. MIT License (see LICENSE). SPDX-License-Identifier: MIT -->

# Contributing

Thanks for your interest in `jgs-reference-skill`. It's a small, focused tool,
and contributions that keep it small and sharp are very welcome.

## Ground rules

- **By contributing you agree your contribution is licensed under the repository's
  MIT License** (see [LICENSE](LICENSE)).
- Be civil. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
- **Do not touch `book_to_skill/` or `scripts/extract.py`** in a way that diverges
  from upstream; that is the vendored [book-to-skill](https://github.com/virgiliojr94/book-to-skill)
  engine (see [ATTRIBUTION.md](ATTRIBUTION.md)). Improvements to the engine belong
  upstream; re-vendor afterwards.
- **The vetting rubric is integrity-critical.** Changes to `tools/vet_source.py` or
  `docs/SOURCE-VETTING.md` must keep the two in sync and must not weaken the
  Excluded hard-stop without a written rationale in the PR.

## Dev setup

No build step. Python ≥ 3.9, stdlib only for the `tools/`. Optional extraction
dependencies install on demand (`pip install -e ".[all]"` for everything).

## Before you open a PR

1. Run every tool's self-check; all must pass:
   ```bash
   for t in vet_source check_overlap outline validate_pack pack_eval; do
       python3 tools/$t.py --self-check
   done
   ```
2. Compile-check: `python3 -m py_compile tools/*.py scripts/extract.py`.
3. If you changed a tool's interface, update `SKILL.md` (the generator spec invokes
   the tools by exact name/flag) and `README.md`.
4. Keep the diff minimal and the change single-purpose.

## Reporting bugs / security

Normal bugs: open an issue. Security issues: **do not** open an issue; see
[SECURITY.md](SECURITY.md).
