# Plan: P2 pack-scaffold-provenance

- date: 2026-09-24
- spec: docs/superpowers/specs/2026-09-24-pack-scaffold-provenance.md (review pair clean)
- plan_path: docs/superpowers/plans/2026-09-24-pack-scaffold-provenance.md
- author-leaf: claude unavailable per user; sdd-executor-deep fallback
- context: ad-hoc (spec Evidence section current; files re-verified in review)
- research: skipped (carried from spec)

## Approach

One scaffold-to-disk-to-validate data flow. Order follows the dependency arrow in the
spec, not the goal numbers:

1. Normalise `templates/PACK.yaml` first. It is the single normative shape; build_pack
   will load it and tests will assert against it.
2. Rewrite `tools/build_pack.py`: slug gate, containment, template load + field-targeted
   substitution, LICENSE stub de-em-dashed. No filesystem effect before the slug gate.
3. Upgrade `tools/validate_pack.py`: double-quote unescape in `parse_simple_yaml`, then
   the four unfilled-marker checks with signpost skip. Additive only.
4. Add regression tests that lock Goals 1-5 against the simulated-fill fixture.
5. Doc sync (Goal 6) and final green verification.

Do not invent a YAML library. `json.dumps` / `json.loads` is the escape pair. Do not add
`build_pack --self-check` (backlog b-07). Do not touch vet_source classify behaviour
beyond the existing import. The Excluded hard-stop at `build_pack` L90-101 stays
byte-equivalent in behaviour.

## Blocking-discovery rule

Before any product edit, run from the repo root in Git Bash:

```bash
python -m pytest -q 2>&1 | tail -8
for t in vet_source check_overlap outline validate_pack pack_eval; do
  python tools/$t.py --self-check || echo "SELF-CHECK-FAIL $t"
done
```

Use `python` locally when `python3` is absent; CI text stays `python3`.

If pytest is red, or any of the five self-checks fails, on the current tree: **stop and
report**. Do not silently patch product code to green the baseline. A Windows-only
symlink `OSError` in `tests/test_output_dir_security.py` (Developer Mode missing) is the
same documented environment carve-out as P1; note it and continue. Any other red is a
blocker for the controller.

Re-run the same commands after the product tasks and again after the tests task. Final
Task 5 requires green.

## Task 1: Normalise templates/PACK.yaml

**Files:** `templates/PACK.yaml` only.

Replace the file body with the normalised shape below. Rules that produced it (spec Goal 3):

- Header comments stay above the fields; no trailing comment text on a value line.
- Build-filled fields use unique bare `<TOKEN>` placeholders on otherwise bare lines.
- Fill-later fields keep literal markers: `built_on: "TODO"`, notes block starting
  `TODO:`, `source_pages: 0`, `chapters: 0`.
- Signpost guidance stays as whole-line comments at the bottom.
- No em dashes in this file's prose comments.

### Normative shape (write this exact content)

```yaml
# Copyright (c) 2026 JG Systems Consulting Ltd. MIT License (see ../LICENSE). SPDX-License-Identifier: MIT
# PACK.yaml - provenance + licence metadata for a reference pack.
# Mandatory (checked by tools/validate_pack.py): slug, title, publisher, license,
# license_tier, commercial_use. license_tier must be 1, 2, or 3 (never Excluded).
# No source-material download URL is stored or published. Attribution is textual.
#
# Build-filled tokens: build_pack substitutes each of the nine single-use
#   placeholders exactly once, field-targeted (slug, title, publisher, version,
#   licence, tier, and the three boolean flags).
# Fill-later markers: the operator replaces the built-on date marker, rewrites
#   the notes block, and sets the two counters before running validate_pack.

# slug = folder name, kebab-case
slug: <SLUG>
title: <TITLE>
# carries the attribution
publisher: <PUBLISHER>
source_version: <VERSION>
# e.g. "CC BY-NC-SA 3.0" / "Public Domain (US Gov)"
license: <LICENSE>
# 1 public domain, 2 open licence, 3 caution
license_tier: <TIER>
# false if NC
commercial_use: <COMMERCIAL_USE>
# true if SA; pack content inherits the licence
share_alike: <SHARE_ALIKE>
attribution_required: <ATTRIBUTION_REQUIRED>
build:
  method: "jgs-reference-skill: vendored book-to-skill extraction + offset-mapped chapter synthesis"
  source_pages: 0
  chapters: 0
  built_on: "TODO"
notes: >
  TODO: record how the source licence's conditions (attribution / non-commercial /
  share-alike / trademark) are carried forward into this pack. Synthesised reference
  notes only; no long verbatim passages (verify with tools/check_overlap.py). For
  multi-source packs, record per-source provenance here.

# Signpost packs (citation-only, Excluded sources) add:  kind: signpost
# and omit chapters/ + a source LICENSE (the signpost text is original/MIT).
```

The file is em-dash-free end to end (the header line above uses an ASCII hyphen).

**Check:**

```bash
python -c "
from pathlib import Path
t = Path('templates/PACK.yaml').read_text(encoding='utf-8')
tokens = ['SLUG','TITLE','PUBLISHER','VERSION','LICENSE','TIER','COMMERCIAL_USE','SHARE_ALIKE','ATTRIBUTION_REQUIRED']
for tok in tokens:
    assert t.count('<' + tok + '>') == 1, tok
assert 'built_on: \"TODO\"' in t and 'source_pages: 0' in t and 'chapters: 0' in t
comment_lines = [ln for ln in t.splitlines() if ln.lstrip().startswith('#')]
assert not any('TODO' in ln for ln in comment_lines), 'TODO must not appear in comments'
assert not any(chr(0x2014) in ln for ln in t.splitlines()), 'em dash must not appear'
import re as _re
extras = set(_re.findall(r'<([A-Z][A-Z_]*)>', t)) - set(tokens)
assert not extras, 'unexpected placeholder tokens: %s' % extras
assert 'title: <TITLE>' in t
print('TEMPLATE_OK')
"
```

## Task 2: Rewrite tools/build_pack.py

**Files:** `tools/build_pack.py` only.

### 2a. Delete the embed; load the template

- Remove `PACK_YAML_TEMPLATE` entirely.
- Resolve the template once:

```python
_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "PACK.yaml"
```

- Load with `read_text(encoding="utf-8")` at scaffold time (not import time is fine; either works).
- Missing template file: exit nonzero with a clear error, create nothing.

### 2b. Slug validation (before any mkdir or write)

Order is mandatory (spec Goal 1):

1. **Kebab-case regex:** `^[a-z0-9]+(-[a-z0-9]+)*$`. Fail `"Bad Slug"`, `/tmp/evil`, `../../x`.
2. **Windows reserved-name blocklist**, case-insensitive, applied to the full slug string
   and to each hyphen-separated segment: `con`, `prn`, `aux`, `nul`, `com1`..`com9`,
   `lpt1`..`lpt9`. Fail `con`, `CON`, `foo-con`, `com1`.
3. **Containment:**

```python
out_root = Path(args.out_dir).resolve()          # parents need not exist
pack_dir = (out_root / args.slug).resolve()
if pack_dir != out_root and out_root not in pack_dir.parents:
    # reject
```

Require `pack_dir` to be a direct-or-nested child of `out_root`. Absolute slug and `..`
segments are already killed by the regex; containment is defence in depth and must still
run. On any violation: print a clear error to stderr, return nonzero, create nothing
(including when `--out-dir` does not exist yet).

Place the slug gate **after** the Excluded hard-stop (so Excluded still returns 2 with the
same message) and **before** the `exists()` check / `mkdir`. Existing-dir check stays.

### 2c. Field-targeted token substitution

Do **not** global-replace `<TITLE>` across the whole file in a way that could hit comments
twice. Substitute each token by exact unique occurrence. Concrete shape:

```python
import json

def _q(value: str) -> str:
    """YAML double-quoted scalar via JSON escaping (stdlib)."""
    return json.dumps(value, ensure_ascii=False)

def render_pack_yaml(template: str, *, slug, title, publisher, version, license,
                     tier, commercial_use, share_alike, attribution_required) -> str:
    replacements = {
        "<SLUG>": slug,                                 # bare kebab
        "<TITLE>": _q(title),                           # includes surrounding quotes
        "<PUBLISHER>": _q(publisher),
        "<VERSION>": _q(version),
        "<LICENSE>": _q(license),
        "<TIER>": str(tier),                            # bare 1|2|3
        "<COMMERCIAL_USE>": commercial_use,             # bare true|false
        "<SHARE_ALIKE>": share_alike,
        "<ATTRIBUTION_REQUIRED>": attribution_required,
    }
    out = template
    for token, value in replacements.items():
        if out.count(token) != 1:
            raise SystemExit(f"template token {token} count={out.count(token)}, expected 1")
        out = out.replace(token, value, 1)
    return out
```

Leave every TODO marker, `source_pages: 0`, `chapters: 0`, and the notes `TODO:` block
untouched. No second pass that strips them.

### 2d. LICENSE stub

Keep `LICENSE_STUB` in build_pack (no second source). Changes only:

- Remove em dashes (the `tier {tier} — see` line becomes e.g. `tier {tier}; see ...`).
- Keep the fill-later line exactly: `TODO: reproduce the source's full licence text` (or the
  existing longer form starting with that phrase; validate_pack will match the substring
  `TODO: reproduce`).
- User values (`title`, `publisher`, `version`, `license`, `slug`) go in **raw** after
  stripping any embedded newlines (`value.replace("\n", " ").replace("\r", " ")`). No
  `json.dumps`, no backslash artifacts.

### 2e. Write path

After gates pass:

```python
(pack_dir / "chapters").mkdir(parents=True)
(pack_dir / "PACK.yaml").write_text(rendered, encoding="utf-8")
(pack_dir / "LICENSE").write_text(license_text, encoding="utf-8")
```

Determinism: same inputs, two runs, byte-identical `PACK.yaml` and `LICENSE` (no
timestamps, no random ids).

### 2f. Sanity check (manual, not a product self-check)

```bash
rm -rf /tmp/p2-scaffold-probe 2>/dev/null; mkdir -p /tmp/p2-scaffold-probe
python tools/build_pack.py --slug nasa-probe \
  --title 'NASA SE Handbook' --publisher NASA --version 'Rev 2' \
  --license 'Public Domain (US Government work)' \
  --out-dir /tmp/p2-scaffold-probe
# expect exit 0, PACK.yaml has title: "NASA SE Handbook", built_on: "TODO", no <TITLE>
python tools/build_pack.py --slug /tmp/evil \
  --title T --publisher P --version V --license 'Public Domain (US Government work)' \
  --out-dir /tmp/p2-scaffold-probe; echo exit=$?
# expect nonzero, and test ! -e /tmp/evil and nothing new under out-dir from this call
rg -n "PACK_YAML_TEMPLATE" tools/build_pack.py && echo STILL_EMBEDDED || echo EMBED_GONE
```

## Task 3: Upgrade tools/validate_pack.py

**Files:** `tools/validate_pack.py` only. Additive; existing check meanings stay.

### 3a. `parse_simple_yaml` double-quote unescape

After extracting `val = m.group(2).strip()`:

- If `val` is fully double-quoted (`len >= 2`, starts and ends with `"`), unescape with
  `json.loads(val)` and store that string. On `json.JSONDecodeError`, fall back to the
  current strip-quotes behaviour (or record a parse finding; prefer fallback so legacy
  fixtures do not break).
- Otherwise keep today's behaviour: `val.strip().strip('"').strip("'")`.
- Still skip indented lines, blank lines, comments, and bare `>` / `|` block indicators.

Round-trip contract: a value emitted by `json.dumps` in build_pack parses back equal to
the original Python string. No key injection from a title containing `: ` or `#` or a
newline (newline is escaped inside the quoted scalar, so it never splits a line).

### 3b. Unfilled-marker rejection (non-signpost only)

Inside `check_pack`, after the existing mandatory-field / tier / slug checks, when
`pack_yaml.is_file()` and **not** `is_signpost`, run these raw-text checks on
`raw = pack_yaml.read_text(encoding="utf-8")` (and LICENSE when present). Named findings,
fail-closed:

| Check | Detection | Example finding text |
| --- | --- | --- |
| TODO anywhere in PACK.yaml | `"TODO" in raw` | `PACK.yaml contains unfilled TODO marker` |
| Placeholder token | `re.search(r"<[A-Z][A-Z_]*>", raw)` | `PACK.yaml contains unfilled placeholder <...>` (include the match) |
| Zero source_pages | raw-line match `source_pages: 0` (allow trailing whitespace; anchor as a full line after optional indent, e.g. `re.search(r"(?m)^\s*source_pages:\s*0\s*$", raw)`) | `PACK.yaml build.source_pages still 0` |
| Zero chapters | same form for `chapters: 0` | `PACK.yaml build.chapters still 0` |
| LICENSE stub | LICENSE file present and `"TODO: reproduce" in license_text` | `LICENSE still contains stub line TODO: reproduce` |

Signpost packs (`kind: signpost`): **skip all four checks** (and the existing LICENSE /
chapters requirements already skip). No TODO scan, no placeholder scan, no zero checks,
no LICENSE stub check.

Markers are reserved: a real pack whose notes legitimately say "TODO" must reword to
publish. Do not special-case.

### 3c. Self-check fixture stays green

`_self_check` already writes a minimal filled PACK.yaml with no TODO, no placeholders, no
`source_pages: 0`. Confirm it still passes after 3a/3b. Optionally extend the self-check
to assert that a PACK.yaml containing `built_on: "TODO"` produces a TODO finding; not
required if Task 4 covers it.

**Check:**

```bash
python tools/validate_pack.py --self-check
```

## Task 4: Regression tests

**Files (new):**

- `tests/test_build_pack_scaffold.py`
- `tests/test_validate_pack_markers.py`

Reuse existing style: pytest, `tmp_path`, no extra fixtures framework. Import via
subprocess or by calling `main([...])` after `sys.path` insert; prefer calling
`build_pack.main` / `validate_pack.check_pack` directly so exit codes and filesystem
effects are asserted without shell quoting pain on Windows.

### Shared helpers

- Pick a licence string that `vet_source.classify` accepts without warnings (or pass
  `--force` only if needed). Prefer a clean Public Domain title/publisher/licence triple
  so the Excluded and warnings paths stay out of these tests.
- Helper `scaffold(tmp_path, slug, title=..., **kwargs)` invoking build_pack into
  `tmp_path / "packs"`.

### Test list mapped to Success criteria

| Test | Asserts | Spec success criterion |
| --- | --- | --- |
| `test_slug_absolute_path_rejected` | `--slug /tmp/evil` (or `C:\evil` shape on win if exercised) exits nonzero; out-dir empty of new pack; no `/tmp/evil` created by the tool | criterion 1 |
| `test_slug_dotdot_rejected` | `--slug ../../x` exits nonzero; creates nothing under out-dir or outside it | criterion 1 |
| `test_slug_bad_kebab_rejected` | `--slug "Bad Slug"` exits nonzero; creates nothing | criterion 1 |
| `test_slug_reserved_con_rejected` | `--slug con` (and optionally `CON`) exits nonzero; creates nothing | criterion 1 |
| `test_slug_rejected_when_outdir_missing` | out-dir path does not exist yet; bad slug still exits nonzero and does not create the out-dir or any pack | criterion 1 ("including when --out-dir does not exist yet") |
| `test_yaml_title_roundtrip_special_chars` | titles containing `"`, `: `, `#`, and an embedded newline each: scaffold succeeds; `parse_simple_yaml` returns the original title; parsed keys equal the expected set (no injected keys) | criterion 2 |
| `test_license_raw_title_no_json_artifacts` | title with a quote scaffolds; LICENSE text contains the raw title characters and no `\"` backslash-quote artifact | criterion 3 (raw title half) |
| `test_no_embedded_pack_yaml_template` | `Path("tools/build_pack.py").read_text()` has no `PACK_YAML_TEMPLATE` assignment | criterion 4 |
| `test_scaffold_deterministic_and_matches_template_shape` | two scaffolds with identical inputs produce byte-identical PACK.yaml; output still contains `built_on: "TODO"`, `source_pages: 0`, `chapters: 0`, and none of the `<TOKEN>`s | criterion 4 |
| `test_fresh_scaffold_fails_validate_naming_markers` | after scaffold, write a minimal SKILL.md + one chapter so structural file checks are not the only failures; `check_pack` returns findings that name TODO / placeholder-or-zero / LICENSE stub as applicable | criterion 5 (fail half) |
| `test_simulated_fill_fixture_passes` | build the normative filled fixture (below); `check_pack` returns `[]` | criterion 5 (pass half) |
| `test_signpost_skips_marker_checks` | pack with `kind: signpost`, SKILL.md + PACK.yaml only, PACK.yaml may contain `TODO` or omit LICENSE; `check_pack` does not emit the four new marker findings (existing signpost structural rules still apply) | criterion 5 (signpost half) |

### Simulated-fill fixture (normative, from spec)

Construct under `tmp_path`:

1. Run build_pack with a clean slug (e.g. `fill-demo`) and ordinary title/publisher/version/licence.
2. Manually rewrite `PACK.yaml`: set `built_on` to a real date (`"2026-09-24"`), rewrite
   `notes` as real provenance prose with **no** `TODO` substring, set `source_pages` and
   `chapters` to positive integers (e.g. `12` and `3`).
3. Rewrite `LICENSE` with reproduced terms and **no** `TODO: reproduce` line.
4. Write `SKILL.md` with valid frontmatter (`name` = slug, a `description`) and one
   chapter link `(chapters/ch01-example.md)`.
5. Write `chapters/ch01-example.md` with any short body.

`validate_pack.check_pack(pack_dir) == []`. The unfilled scaffold from step 1 (plus minimal
SKILL/chapter so missing-files do not dominate) must fail.

### Check

```bash
python -m pytest -q tests/test_build_pack_scaffold.py tests/test_validate_pack_markers.py
python -m pytest -q
for t in vet_source check_overlap outline validate_pack pack_eval; do
  python tools/$t.py --self-check || echo "SELF-CHECK-FAIL $t"
done
```

Expect: new tests green; full suite at baseline 452 passed / 5 skipped **plus** the new
tests; five-tool self-check still passes. If the suite is red for reasons outside these
files, stop and report (blocking-discovery rule still applies).

## Task 5: Doc sync + final verification

**Files:**

- `SKILL.md` (Step 5, around L151-152 only)
- `docs/PACK-SPEC.md` (PACK.yaml schema blurb around L49; wording only, no field redesign)

### SKILL.md

Replace the fill instruction so it matches the normalised marker scheme. Current text
says "Fill the `PACK.yaml` TODOs (`source_pages`, `chapters`, `built_on`, `notes`)". New
text must name:

- replace `built_on: "TODO"` with the build date
- rewrite the notes block (remove the leading `TODO:`)
- set `source_pages` and `chapters` to positive integers
- reproduce the source terms in `LICENSE` (remove the `TODO: reproduce` stub line)

Keep the surrounding Step 5 structure. No em dashes in the touched sentences. Written
prose standard applies.

### docs/PACK-SPEC.md

Keep the `templates/PACK.yaml` pointer. Add one short sentence that build_pack loads that
template, substitutes the `<TOKEN>` placeholders, and leaves the fill-later markers
(`built_on: "TODO"`, notes `TODO:`, zero `source_pages` / `chapters`) for the operator;
`validate_pack` rejects those markers on non-signpost packs. No field redesign. No em
dashes.

### Final verification

```bash
python -m pytest -q
for t in vet_source check_overlap outline validate_pack pack_eval; do
  python tools/$t.py --self-check || echo "SELF-CHECK-FAIL $t"
done
python -m py_compile tools/build_pack.py tools/validate_pack.py && echo COMPILE_OK
# optional prose check on touched docs:
python ~/.zcode/scripts/prose_check.py SKILL.md docs/PACK-SPEC.md docs/superpowers/plans/2026-09-24-pack-scaffold-provenance.md || true
```

All green required before this plan is marked executed.

## Acceptance criteria checklist

Mirror of the spec Success criteria. Every box must hold before merge:

- [ ] `python tools/build_pack.py --slug /tmp/evil ...`, `--slug ../../x`, `--slug "Bad Slug"`, and `--slug con` each exit nonzero with a clear error and create nothing, including when `--out-dir` does not exist yet.
- [ ] A title containing `"`, `: `, `#`, or a newline produces a PACK.yaml whose upgraded `parse_simple_yaml` returns the original value, with no extra keys; regression tests prove it.
- [ ] The emitted LICENSE shows the raw title text (no backslash artifacts); after fill, no `TODO: reproduce` line remains.
- [ ] `tools/build_pack.py` contains no embedded PACK.yaml template string; two runs with the same inputs produce byte-identical scaffolds that match the normalised `templates/PACK.yaml` shape (tokens filled, fill-later markers intact).
- [ ] `python tools/validate_pack.py <fresh-scaffold>` fails and names the unfilled markers; the simulated-fill fixture passes; signpost fixtures skip the four new checks.
- [ ] Doc sync applied: `SKILL.md` Step 5 and `docs/PACK-SPEC.md` describe the normalised marker scheme; no stale "Fill the PACK.yaml TODOs" wording that contradicts it.
- [ ] New regression tests green alongside the existing suite (452 passed / 5 skipped baseline plus the new tests); five-tool self-check loop still passes.

## Out of scope (do not touch)

- `tools/vet_source.py` classify / tier logic (P3)
- CI workflow (P1, done)
- `install.py` (P5)
- Step 9 gate-set beyond validate_pack's additive checks (P4)
- `build_pack --self-check` (b-07)
- New dependencies; tools stay pure stdlib
