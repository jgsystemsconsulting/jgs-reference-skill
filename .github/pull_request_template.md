## Summary

One concern per PR. Link the issue if there is one.

## Type

- [ ] Code
- [ ] Docs
- [ ] Tests
- [ ] Packaging / installer
- [ ] Release files

## Checklist

- [ ] One concern only.
- [ ] Vet rubric and SOURCE-VETTING.md stay in sync when either changes; Excluded hard-stop is not weakened without a written rationale.
- [ ] This PR contains no secrets, tokens, keys, or credentials.
- [ ] I have the right to license this contribution under the repo licence (see LICENSE).
- [ ] I did not diverge `book_to_skill/` or `scripts/extract.py` from upstream without an upstream-first plan (see CONTRIBUTING.md).

## Tests run

- [ ] `python3 -m pytest -q`
- [ ] five-tool self-check: `vet_source` `check_overlap` `outline` `validate_pack` `pack_eval`
- [ ] `python3 scripts/check_release.py`
