# Plan: P3 vet-licence-token-match

- date: 2026-09-24
- spec: docs/superpowers/specs/2026-09-24-vet-licence-token-match.md (reviewed clean over 4 rounds)
- plan_path: docs/superpowers/plans/2026-09-24-vet-licence-token-match.md
- author-leaf: claude unavailable; plan-author fallback (inline on sdd-executor-deep seat)
- context: ad-hoc (spec Evidence current; tools/vet_source.py L105-107 substring defect confirmed; tests/test_build_pack_scaffold.py sys.path pattern confirmed; docs/SOURCE-VETTING.md L33 family-only bullet confirmed)
- research: skipped (carried from spec)

## Approach

S-sized, three tasks, dependency order:

1. Replace the permissive substring branch in `tools/vet_source.py` with the boundary matcher plus negation guard from the spec implementation shape. Extend `_self_check` so the CLI gate locks SC1-SC5 and SC8 probes without needing pytest for the operator path.
2. Add `tests/test_vet_source_token_match.py` with classify-level cases mapping 1:1 to Success criteria 1-7 (pytest coverage the self-check does not own alone, plus the build_pack e2e for SC6).
3. Sync the SOURCE-VETTING.md Tier 2 bullet (SC8) and run the full verification suite.

Do not touch EXCLUDED, US_GOV, PD_LICENSE, the CC branch, verdict shape, or classify short-circuit order. Do not add dependencies. Do not invent GPL/MPL families. Transcribe the matcher from the spec; do not redesign it.

## Blocking-discovery rule

Before any product edit, run from the repo root in Git Bash:

```bash
python -m pytest -q 2>&1 | tail -12
python tools/vet_source.py --self-check
```

Baseline expectation from the package/spec era: **467 passed, 5 skipped**, and `vet_source --self-check` exits 0 on the current eight-row table. Use `python` locally when `python3` is absent; CI text stays `python3`.

If pytest is red, or self-check fails, on the current tree: **stop and report**. Do not silently patch product code to green the baseline. A Windows-only symlink `OSError` in `tests/test_output_dir_security.py` (Developer Mode missing) is the same documented environment carve-out as P1/P2; note it and continue. Any other red is a blocker for the controller.

Re-run pytest + self-check after Task 1 and after Task 2. Task 3 final verification requires green against the new baseline (467 + new tests).

## Task 1: Matcher + negation guard + self-check probes

**Files:** `tools/vet_source.py` only.

### 1a. Module-level compiled patterns

Place these next to the other module constants (after `PD_LICENSE`, before `classify`), so they compile once:

```python
_PERMISSIVE_FAMILY = re.compile(r"\b(?:mit|apache|(?:free\s*)?bsd)\b")
_NEGATION = re.compile(
    r"\bnon[\s_-]*commercial\b|\bno[\s_-]*commercial\b|\bnot\s+for\s+commercial\b"
    r"|\bcommercial\s+use\s+(?:is\s+)?(?:prohibited|restricted|forbidden|not\s+permitted|not\s+allowed)\b"
    r"|\bnc\b")  # boundary-anchored: the standalone token, never the nc inside licence
```

Word boundaries are Python `\b` (write them as backslash-b in the source). The optional `free\s*` prefix on BSD is what catches `FreeBSD license`. The trailing `\bnc\b` must stay boundary-anchored so `licence` / `license` do not demote true grants.

### 1b. Replace the defective branch

Current defect at L105-107:

```python
if any(k in lic for k in ("mit", "apache", "bsd")):
    return _verdict(tier=2, commercial_use=True, share_alike=False,
                    attribution_required=True)
```

Replace with exactly:

```python
# A negated grant ("non-commercial MIT variant") must NOT return
# commercial_use=True: it falls through to the step-4 caution path.
if _PERMISSIVE_FAMILY.search(lic) and not _NEGATION.search(lic):
    return _verdict(tier=2, commercial_use=True, share_alike=False,
                    attribution_required=True)
```

No other classify branches change. Order stays: Excluded → Tier 1 → CC → permissive → Tier 3 fallback.

### 1c. Extend `_self_check` cases

Keep the existing eight rows and the SEBoK NC+SA assert. Append new rows to the `cases` list. Shape stays `(title, publisher, license, expect_excluded, expect_tier)`.

Representative additions (transcribe all of these; title/publisher stay non-Excluded neutrals unless the row is an Excluded regression):

```python
# False positives / token-free (SC1, SC2) → tier 3
("Some Guide", "Author", "limitations of liability apply", False, 3),
("Some Guide", "Author", "reviewed by committee", False, 3),
("Some Guide", "Author", "may be distributed under site terms", False, 3),
# True grants (SC3) → tier 2
("Some Guide", "Author", "MIT", False, 2),
("Some Guide", "Author", "Apache 2.0", False, 2),
("Some Guide", "Author", "BSD 3-Clause", False, 2),
("Some Guide", "Author", "MIT-style", False, 2),
("Some Guide", "Author", "FreeBSD license", False, 2),
# Licence spelling must not trip \bnc\b (probe table / SC3)
("Some Guide", "Author", "MIT licence", False, 2),
("Some Guide", "Author", "Apache Licence 2.0", False, 2),
# Synthetic embedded bsd hosts (spec Goal 1 non-matches) → tier 3
("Some Guide", "Author", "xxbsdxx terms", False, 3),
("Some Guide", "Author", "bsdlike arrangement", False, 3),
# Negated grants (SC3b) → caution path tier 3
("Some Guide", "Author", "MIT for non-commercial use only", False, 3),
("Some Guide", "Author", "noncommercial MIT variant", False, 3),
("Some Guide", "Author", "MIT, commercial use prohibited", False, 3),
("Some Guide", "Author", "MIT; no commercial restrictions", False, 3),
("Some Guide", "Author", "MIT NC", False, 3),
("Some Guide", "Author", "licence nc only", False, 3),
("Some Guide", "Author", "MIT, commercial use not allowed", False, 3),
# Excluded unchanged (SC4) — reasons asserted separately below if needed
("AFOTEC CERT Guide", "AFOTEC", "", True, None),
("Defense Acquisition Guidebook", "DoD", "", True, None),
("SEI Technical Report", "Carnegie Mellon", "", True, None),
```

After the existing loop and the SEBoK assert, add a true-grant shape assert so commercial_use / share_alike / attribution_required lock beyond tier alone:

```python
mit = classify("Some Guide", "Author", "MIT")
assert (
    mit["license_tier"] == 2
    and mit["commercial_use"] is True
    and mit["share_alike"] is False
    and mit["attribution_required"] is True
), mit
neg = classify("Some Guide", "Author", "MIT for non-commercial use only")
assert neg["license_tier"] == 3 and neg["commercial_use"] is False, neg
```

Do not rewrite the print/return contract of `_self_check`. Exit 0 on PASS, 1 on FAIL.

**Check after Task 1:**

```bash
python tools/vet_source.py --self-check
python -m pytest -q 2>&1 | tail -12
```

Self-check must print `PASS` and exit 0. Existing pytest suite must stay green (no new module yet).

## Task 2: Pytest module for SC1-SC7

**Files:** create `tests/test_vet_source_token_match.py`.

Follow `tests/test_build_pack_scaffold.py` conventions:

- Module docstring naming the spec and the SC coverage.
- `REPO_ROOT = Path(__file__).resolve().parent.parent`
- `sys.path.insert(0, str(REPO_ROOT / "tools"))` before importing `vet_source` / `build_pack`.
- `tmp_path` for any scaffold; never write under real `packs/`.
- No network, no new deps.

### 2a. Classify-level cases (SC1-SC5, SC7 shape)

```python
# Copyright (c) 2026 JG Systems Consulting Ltd. See LICENSE.
# SPDX-License-Identifier: MIT
"""Token / boundary matcher for vet_source permissive-family branch.

Covers spec 2026-09-24-vet-licence-token-match Success criteria 1-7 at
classify level, plus a build_pack e2e for SC6.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_pack  # noqa: E402
import vet_source  # noqa: E402
from validate_pack import parse_simple_yaml  # noqa: E402

T2 = dict(license_tier=2, commercial_use=True, share_alike=False,
          attribution_required=True, excluded=False)


def _t2(v: dict) -> None:
    for k, exp in T2.items():
        assert v[k] is exp or v[k] == exp, (k, v[k], exp, v)


@pytest.mark.parametrize("lic", [
    "limitations of liability apply",
    "reviewed by committee",
    "may be distributed under site terms",
])
def test_sc1_sc2_false_positives_and_token_free(lic):
    v = vet_source.classify("Some Guide", "Author", lic)
    assert v["excluded"] is False
    assert v["license_tier"] == 3
    assert v["commercial_use"] is False


@pytest.mark.parametrize("lic", [
    "MIT",
    "Apache 2.0",
    "BSD 3-Clause",
    "MIT-style",
    "FreeBSD license",
    "MIT licence",
    "Apache Licence 2.0",
])
def test_sc3_true_grants(lic):
    _t2(vet_source.classify("Some Guide", "Author", lic))


@pytest.mark.parametrize("lic", [
    "MIT for non-commercial use only",
    "noncommercial MIT variant",
    "MIT, commercial use prohibited",
    "MIT; no commercial restrictions",
    "MIT NC",
    "licence nc only",
    "MIT, commercial use not allowed",
])
def test_sc3b_negated_grants(lic):
    v = vet_source.classify("Some Guide", "Author", lic)
    assert v["commercial_use"] is False
    assert v["license_tier"] == 3
    assert v["excluded"] is False


@pytest.mark.parametrize("title,publisher,lic", [
    ("AFOTEC CERT Guide", "AFOTEC", ""),
    ("Defense Acquisition Guidebook", "DoD", ""),
    ("DoD DAG summary", "OUSD", ""),
    ("SEI Technical Report", "Carnegie Mellon University", ""),
    ("CMU report", "Software Engineering Institute", ""),
])
def test_sc4_excluded_unchanged(title, publisher, lic):
    v = vet_source.classify(title, publisher, lic)
    assert v["excluded"] is True
    assert v["license_tier"] is None
    assert v["excluded_reason"]


def test_sc4_prior_self_check_rows_and_sebok():
    rows = [
        ("ISO/IEC/IEEE 15288", "ISO", "", True, None),
        ("SysML v2", "Object Management Group", "OMG Specification License", True, None),
        ("INCOSE SE Handbook", "Wiley", "", True, None),
        ("SE Handbook", "NASA", "Public Domain (US Government work)", False, 1),
        ("DoD SE Guidebook", "OUSD R&E", "Distribution A", False, 1),
        ("SEBoK", "BKCASE / Stevens", "CC BY-NC-SA 3.0", False, 2),
        ("Some Guide", "Author", "CC BY-ND 4.0", False, 3),
        ("Mystery Doc", "Random Blog", "freely available", False, 3),
    ]
    for title, pub, lic, exp_excl, exp_tier in rows:
        v = vet_source.classify(title, pub, lic)
        assert v["excluded"] is exp_excl and v["license_tier"] is exp_tier, (title, v)
    sebok = vet_source.classify("SEBoK", "Stevens", "CC BY-NC-SA 3.0")
    assert sebok["commercial_use"] is False and sebok["share_alike"] is True


def test_sc5_self_check_exit_zero():
    assert vet_source._self_check() == 0


def test_sc4_excluded_reasons_exact():
    from vet_source import classify
    # Frozen literals copied from tools/vet_source.py EXCLUDED at plan time.
    EXPECTED_REASONS = {
        ("Air Force Civil Engineering Center report", "AFOTEC"):
            "AFOTEC OT&E / CERT products are not a redistribution grant for this library",
        ("Defense Acquisition Guidebook", "DoD DAG"):
            "DAG is not packageable here",
        ("SEI handbook", "Carnegie Mellon Software Engineering Institute"):
            "SEI technical reports are not a blanket redistribution grant",
    }
    for title, publisher, license in [
        ("Air Force Civil Engineering Center report", "AFOTEC", "MIT"),
        ("Defense Acquisition Guidebook", "DoD DAG", "MIT"),
        ("SEI handbook", "Carnegie Mellon Software Engineering Institute", "MIT"),
    ]:
        v = classify(title, publisher, license)
        assert v["excluded"] is True
        # reason text frozen to the current strings (a swap between titles must fail)
        assert v["excluded_reason"] == EXPECTED_REASONS[(title, publisher)]


def test_sc7_stdlib_only():
    import ast, sys as _sys
    src = (REPO_ROOT / "tools" / "vet_source.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    stdlib = set(_sys.stdlib_module_names)
    local = {"vet_source"}
    assert imported <= stdlib | local, imported - stdlib - local
```

### 2b. build_pack e2e (SC6)

Mirror the scaffold helper style from `test_build_pack_scaffold.py`. Non-Excluded title/publisher, `--license MIT`, unique kebab slug, tmp out-dir, no `--tier` / `--commercial-use` overrides. Assert classify-derived fields land in PACK.yaml:

```python
def test_sc6_build_pack_mit_e2e(tmp_path):
    out_dir = tmp_path / "packs"
    slug = "mit-token-match-demo"
    argv = [
        "build_pack.py",
        "--slug", slug,
        "--out-dir", str(out_dir),
        "--title", "Token Match Handbook",
        "--publisher", "Example Press",
        "--version", "1st ed. (2026)",
        "--license", "MIT",
    ]
    rc = build_pack.main(argv)
    assert rc == 0
    meta = parse_simple_yaml((out_dir / slug / "PACK.yaml").read_text(encoding="utf-8"))
    # parse_simple_yaml returns strings only (no typed ints/bools), so compare as strings
    assert meta["commercial_use"] == "true"
    assert meta["license_tier"] == "2"
```

Do not write typed asserts (`== 2`, `is True`) against `parse_simple_yaml` output: it returns strings only.

**Check after Task 2:**

```bash
python -m pytest tests/test_vet_source_token_match.py -q
python tools/vet_source.py --self-check
python -m pytest -q 2>&1 | tail -12
```

New module green; full suite green at 467 + N new tests (N = parametrize expansion + the named tests above); self-check PASS.

## Task 3: Doc sync + final verification

**Files:** `docs/SOURCE-VETTING.md` (Tier 2 bullet only).

### 3a. Tier 2 permissive bullet (SC8)

Current L33:

```markdown
- Permissive licences (MIT/Apache/BSD) where they cover the text.
```

Replace with one short sentence that states the recognition rule without pasting the regex:

```markdown
- Permissive licences (MIT/Apache/BSD) where they cover the text. Recognition is
  case-insensitive token / word-boundary match on the family name (MIT, Apache,
  BSD), so accidental substrings in ordinary prose (for example "limitations" or
  "committee") do not count as a grant. A family token paired with a
  non-commercial restriction falls to Tier 3 caution instead of commercial true.
```

No other SOURCE-VETTING sections change. No SKILL.md edit (spec: no substring claim found). Written prose standard: no em dashes, staff-engineer voice.

### 3b. Final verification

From repo root:

```bash
python tools/vet_source.py --self-check
python -m pytest -q 2>&1 | tee /tmp/vet-token-match-pytest.txt | tail -20
```

Pass bar:

- self-check exits 0 and prints PASS (includes new false-positive, true-grant, negated, licence-spelling, synthetic bsd host `xxbsdxx`/`bsdlike`, Excluded rows).
- pytest: prior 467 passed / 5 skipped **plus** every new test from Task 2; zero failed except the documented Windows symlink carve-out (test_prepare_output_dir_rejects_symlink raises OSError without Developer Mode; note it and continue). Record the new total in the implementer report.
- Spot-check SC6 by reading the tmp PACK.yaml from the e2e test on a single rerun if needed:
  `python -m pytest tests/test_vet_source_token_match.py::test_sc6_build_pack_mit_e2e -q`.
- Confirm `docs/SOURCE-VETTING.md` Tier 2 bullet names boundary/token recognition (SC8).
- Confirm `tools/vet_source.py` has no new third-party imports (SC7).
- Optional prose check on the touched doc only:
  `python ~/.zcode/scripts/prose_check.py docs/SOURCE-VETTING.md` (fix residual flags or justify).

Do not commit unless the dispatch / parent explicitly asks; this plan's implementer seat commits when the controller says so under SDD norms.

## Acceptance criteria checklist

Mirror of Success criteria 1-8. Every box must be true before STATUS: DONE.

- [ ] **SC1.** `classify("Some Guide", "Author", "limitations of liability apply")` → `license_tier == 3`, `commercial_use is False` (self-check + pytest).
- [ ] **SC2.** Same caution path for `reviewed by committee` and `may be distributed under site terms`.
- [ ] **SC3.** `MIT`, `Apache 2.0`, `BSD 3-Clause`, `MIT-style`, `FreeBSD license` each → tier 2, `commercial_use=True`, `share_alike=False`, `attribution_required=True`.
- [ ] **SC3b.** Negated grants (`MIT for non-commercial use only`, `noncommercial MIT variant`, `MIT, commercial use prohibited`, `MIT; no commercial restrictions`, plus `MIT NC` / `licence nc only` / `MIT, commercial use not allowed`) do **not** return `commercial_use=True`; tier 3 caution path.
- [ ] **SC4.** AFOTEC / DAG / CMU-SEI Excluded rows still `excluded=True`, tier `None`, reasons unchanged; prior eight self-check rows still pass; SEBoK NC+SA assert still holds.
- [ ] **SC5.** `python tools/vet_source.py --self-check` exits 0 and includes the new probes.
- [ ] **SC6.** `build_pack` with non-Excluded title/publisher, `--license MIT`, tmp out-dir, fresh kebab slug, no tier overrides → exit 0; PACK.yaml has `license_tier: 2` and `commercial_use: true`.
- [ ] **SC7.** No new runtime dependencies; tools stay pure stdlib.
- [ ] **SC8.** SOURCE-VETTING.md Tier 2 permissive bullet states boundary/token recognition of MIT/Apache/BSD family tokens.

## Out of scope (do not do)

- Excluded-title token hygiene for `iec ` / `iso` (backlog).
- CI workflow edits (P1 done).
- build_pack path / YAML / template emission beyond consuming classify (P2 done).
- New licence families (GPL, MPL, proprietary parsers).
- Inspecting the licence field inside Excluded matching.
- `build_pack --self-check`.
- Rewriting SOURCE-VETTING tier policy, signpost mode, or PACK-SPEC fields.
