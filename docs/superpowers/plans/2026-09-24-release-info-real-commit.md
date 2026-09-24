# Release-Info Real Commit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the P6 residual by making `scripts/check_release.py` fail the RR-B-15 gate when `RELEASE-INFO.txt` pins a missing, malformed, non-commit, or non-ancestor `Source-Commit`, and deepen the integrity checkout so CI history is complete.

**Architecture:** One pure-stdlib helper `check_source_commit(root) -> list[str]` parses a line-anchored field, validates 7-40 hex form, probes `git rev-parse --git-dir`, peels with `rev-parse --verify <hash>^{commit}`, then requires `merge-base --is-ancestor` against `HEAD`. `main` extends errors after the required-file loop so a missing file is reported once. Integrity job checkout gains `fetch-depth: 0`. Tests drive a real temp git repo via subprocess (same posture as `tests/test_repo_hygiene.py`).

**Tech Stack:** Python 3 stdlib (`pathlib`, `re`, `subprocess`, `sys`), pytest, git CLI, GitHub Actions `actions/checkout@v4`.

**Spec:** `docs/superpowers/specs/2026-09-24-release-info-real-commit.md` (reviewed clean; residual scope locked).

## Global Constraints

- Integrity job checkout only: add `with: fetch-depth: 0`. Existing step otherwise untouched. Do not change the `tests` job checkout.
- Pure stdlib in `scripts/check_release.py`. `subprocess` argv lists only (no `shell=True`). Works on Windows dev and Linux CI.
- `RELEASE-INFO.txt` bytes unchanged by this package.
- No change to required-file list, forbidden-content patterns, header rules, success line `Release gate: OK`, `::error::` prefix, or `FAILED: N issue(s).` summary.
- Fail closed when git is missing or cwd is not a repository. Do not auto-skip on shallow clones; document only.
- Do not require `Source-Commit == HEAD` (ancestor is the bar).
- Regexes as raw strings. No em dashes in durable prose. No control characters in this plan or in committed sources.
- Written prose standard on the module docstring only durable touch beyond code/YAML/tests.

## File map

| Path | Action | Responsibility |
|---|---|---|
| `scripts/check_release.py` | Modify | Helper + main hook + docstring |
| `.github/workflows/validate.yml` | Modify | Integrity checkout `fetch-depth: 0` |
| `tests/test_release_info_commit.py` | Create | Temp-repo coverage of the helper |
| `RELEASE-INFO.txt` | **Do not touch** | Already truthful |

Test filename follows the controller dispatch (`tests/test_release_info_commit.py`). Spec draft SC5 named `test_check_release_source_commit.py`; coverage content is the binding bar, not the draft stem.

## Approach

S-sized, two tasks:

1. Product + CI: `check_source_commit` helper, `main` integration, module docstring, integrity `fetch-depth: 0`.
2. Tests for the helper (temp git repo) + full verification suite.

Transcribe the fix contract from the spec. Do not redesign messages, peel syntax, or ancestor semantics.

## Blocking-discovery rule

Before any product edit, run from the repo root in Git Bash:

```bash
python -m pytest -q 2>&1 | tail -12
python scripts/check_release.py
for t in vet_source check_overlap outline validate_pack pack_eval; do
  python tools/$t.py --self-check || echo "SELF-CHECK-FAIL $t"
done
```

Use `python` locally when `python3` is absent; CI and workflow command blocks stay `python3`.

Baseline expectation from the controller dispatch: **531 passed, 5 skipped**, plus five-tool self-checks green, and `scripts/check_release.py` printing `Release gate: OK` exit 0. Live collect-only on this tree may already be higher after prior packages; **record the actual pytest summary line** as the baseline and treat that count (not the dispatch figure) as the floor. Final verification must be baseline + new tests, still 5 skipped (unless a new skip is intentional for git-unavailable), five-tool self-checks unchanged green, release gate still OK on the current tree.

If pytest is red, release gate is red, or any self-check fails on the current tree: **stop and report**. Do not silently patch product code to green the baseline. A Windows-only symlink `OSError` in `tests/test_output_dir_security.py` (Developer Mode missing) is the same documented environment carve-out as prior packages; note it and continue. Any other red is a blocker for the controller.

Re-run the helper-focused pytest after Task 1 smoke (if tests already exist mid-rebase, otherwise Task 1 ends with release-gate smoke only). Task 2 owns full suite verification.

---

### Task 1: Source-Commit helper + integrity fetch-depth

**Files:**
- Modify: `scripts/check_release.py`
- Modify: `.github/workflows/validate.yml` (integrity job checkout only)
- Test: deferred to Task 2 (Task 1 ends with live gate smoke on current tree)

**Interfaces:**
- Consumes: existing `ROOT`, `errors: list[str]`, `main() -> int`, required-file loop
- Produces: `check_source_commit(root: pathlib.Path) -> list[str]` (zero or more error strings; never `sys.exit`)

**Model:** standard

- [ ] **Step 1: Confirm baseline (blocking discovery)**

Run the blocking-discovery commands above. Record the pytest summary, release-gate line, and five self-check results in the work log. Stop on unexpected red.

- [ ] **Step 2: Replace the module docstring**

Replace the top docstring so it names the new duty and the shallow-clone operator note. Exact text:

```python
"""Release gate (RR-B-15): required files, forbidden content, headers
present on first-party .py files, and Source-Commit resolves to an
ancestor of HEAD. Exits non-zero on any failure.

Complements (does not replace) validate.yml's existing content-integrity,
SKILL.md frontmatter, and version-consistency steps.

Source-Commit ancestor check walks local git history. Shallow clones may
false-fail; run `git fetch --unshallow` (or deepen) before relying on this
gate locally. CI integrity checkout sets fetch-depth: 0.
"""
```

No em dashes. Keep the copyright/SPDX header lines above unchanged.

- [ ] **Step 3: Add imports and compiled patterns**

`subprocess` is imported inside `_tracked_py` today. Move (or duplicate at module level) so the helper can use it cleanly. Replacement for the module top (everything from the imports through the FORBIDDEN_CONTENT definition); do not append after the existing definitions or REQUIRED would be duplicated:

```python
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

REQUIRED = [
    "LICENSE", "COPYRIGHT", "NOTICE", "README.md", "CHANGELOG.md",
    "SECURITY.md", "CITATION.cff", "RELEASE-INFO.txt", "SKILL.md",
    "docs/index.html",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
]

# Assembled from parts so this file never self-matches the workflow's
# leak-sentinel grep (validate.yml), which excludes only .git/ and .github/.
# The variable name also avoids the contiguous word: the grep is -i.
_SENTINEL = "CONFID" + "ENTIAL"

FORBIDDEN_CONTENT = [
    re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
    re.compile(_SENTINEL),
]

_SOURCE_COMMIT_LINE = re.compile(r"^Source-Commit:\s*(\S+)\s*$", re.M)
_SOURCE_COMMIT_HEX = re.compile(r"^[0-9a-fA-F]{7,40}$")
```

Keep `FORBIDDEN_CONTENT` and `REQUIRED` byte-identical in behaviour. Drop the nested `import subprocess` inside `_tracked_py` once the module-level import exists (call sites stay the same).

- [ ] **Step 4: Add `check_source_commit` helper (exact behaviour)**

Place after `_tracked_py` (or immediately before `main`). Transcribe this implementation; message strings are normative from the spec table.

```python
def check_source_commit(root: pathlib.Path) -> list[str]:
    """Return error strings for a bad or missing Source-Commit pin.

    Missing RELEASE-INFO.txt yields [] so the required-file loop owns that
    report (no double fault). Fail closed when git is missing. Shallow
    clones are not auto-skipped; see module docstring.
    """
    path = root / "RELEASE-INFO.txt"
    if not path.is_file():
        return []

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"RELEASE-INFO.txt: unreadable: {exc}"]

    matches = _SOURCE_COMMIT_LINE.findall(text)
    if len(matches) == 0:
        return ["RELEASE-INFO.txt: missing Source-Commit field"]
    if len(matches) > 1:
        return ["RELEASE-INFO.txt: duplicate Source-Commit field"]

    token = matches[0].strip()
    if not token:
        return ["RELEASE-INFO.txt: empty Source-Commit value"]

    if _SOURCE_COMMIT_HEX.fullmatch(token) is None:
        return [
            "RELEASE-INFO.txt: Source-Commit malformed "
            f"(want 7-40 hex chars): {token}"
        ]

    try:
        probe = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=root,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, OSError) as exc:
        return [f"RELEASE-INFO.txt: Source-Commit check requires git: {exc}"]

    if probe.returncode != 0:
        return ["RELEASE-INFO.txt: Source-Commit check: not a git repository"]

    # Peel to a commit object. Argv list keeps ^{commit} intact on Windows
    # (no shell). token + "^{commit}" avoids f-string brace escaping traps.
    try:
        resolved_proc = subprocess.run(
            ["git", "rev-parse", "--verify", token + "^{commit}"],
            cwd=root,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, OSError) as exc:
        return [f"RELEASE-INFO.txt: Source-Commit check requires git: {exc}"]

    resolved = (resolved_proc.stdout or "").strip()
    if resolved_proc.returncode != 0 or not resolved:
        return [
            "RELEASE-INFO.txt: Source-Commit does not resolve to a commit: "
            f"{token}"
        ]

    try:
        anc = subprocess.run(
            ["git", "merge-base", "--is-ancestor", resolved, "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, OSError) as exc:
        return [f"RELEASE-INFO.txt: Source-Commit check requires git: {exc}"]

    if anc.returncode == 0:
        return []
    if anc.returncode == 1:
        return [
            "RELEASE-INFO.txt: Source-Commit is not an ancestor of HEAD: "
            f"{resolved}"
        ]
    reason = (anc.stderr or anc.stdout or f"exit {anc.returncode}").strip()
    return [f"RELEASE-INFO.txt: Source-Commit ancestor check failed: {reason}"]
```

Normative failure message table (do not paraphrase prefixes):

| Condition | Error string |
|---|---|
| File unreadable | `RELEASE-INFO.txt: unreadable: <exc>` |
| No `Source-Commit:` line | `RELEASE-INFO.txt: missing Source-Commit field` |
| More than one match | `RELEASE-INFO.txt: duplicate Source-Commit field` |
| Empty token (defensive) | `RELEASE-INFO.txt: empty Source-Commit value` |
| Form fail | `RELEASE-INFO.txt: Source-Commit malformed (want 7-40 hex chars): <token>` |
| Git executable missing | `RELEASE-INFO.txt: Source-Commit check requires git: <exc>` |
| `rev-parse --git-dir` non-zero | `RELEASE-INFO.txt: Source-Commit check: not a git repository` |
| Peel fail / empty stdout | `RELEASE-INFO.txt: Source-Commit does not resolve to a commit: <token>` |
| `merge-base --is-ancestor` exit 1 | `RELEASE-INFO.txt: Source-Commit is not an ancestor of HEAD: <resolved>` |
| Ancestor check other non-zero | `RELEASE-INFO.txt: Source-Commit ancestor check failed: <stderr-or-reason>` |

Order is load-bearing: missing-file skip → read → exactly-one match → form → git-dir probe → peel → ancestor. Do not call git after a form failure. Do not run ancestor after a peel failure.

- [ ] **Step 5: Hook `main` after the required-file loop**

Exact insertion point: immediately after the `for rel in REQUIRED:` loop, before the forbidden-content walk.

```python
def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"required file missing: {rel}")

    errors.extend(check_source_commit(ROOT))

    for path in ROOT.rglob("*"):
        # ... unchanged from here ...
```

Do not change the error-print / exit-0/1 tail.

- [ ] **Step 6: Integrity checkout `fetch-depth: 0`**

In `.github/workflows/validate.yml`, integrity job only. Current:

```yaml
  integrity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
```

Replace with exact diff:

```yaml
  integrity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
```

Do **not** add `fetch-depth` to the `tests` job checkout. Do not touch other integrity steps (content integrity, frontmatter, RR-S-11, RR-B-15 command).

- [ ] **Step 7: Smoke the live gate on the current tree**

```bash
python scripts/check_release.py
echo exit:$?
```

Expected: prints `Release gate: OK`, exit 0 (current pin `ff4cb7360d4c8a24e7ddc5a7ea5a13dd22beb54f` is a real ancestor). If red, stop and diagnose; do not edit `RELEASE-INFO.txt`.

Optional manual phantom probe (restore after):

```bash
# optional; leave tree clean
cp RELEASE-INFO.txt /tmp/RELEASE-INFO.txt.bak
# edit Source-Commit to 40 hex zeros, run gate, expect non-zero + Source-Commit in ::error::
# restore from bak
```

- [ ] **Step 8: Commit Task 1**

```bash
git add scripts/check_release.py .github/workflows/validate.yml
git commit -m "$(cat <<'EOF'
fix(release): validate Source-Commit is an ancestor of HEAD

RR-B-15 reads RELEASE-INFO.txt, peels the pin to a commit, and requires
merge-base --is-ancestor against HEAD. Integrity checkout uses
fetch-depth: 0 so CI history is complete for the check.
EOF
)"
```

---

### Task 2: Temp-repo tests + final verification

**Files:**
- Create: `tests/test_release_info_commit.py`
- Test: that file + full suite + release gate + five-tool self-checks

**Interfaces:**
- Consumes: `check_source_commit(root: pathlib.Path) -> list[str]` from Task 1
- Produces: pytest module covering dispatch/spec cases; no product API changes

**Model:** standard

- [ ] **Step 1: Create the test module**

Follow `tests/test_repo_hygiene.py` conventions: real git via subprocess, `pytest.skip` when git cannot run, no monkeypatched fake git, no network, no new deps. Import the helper by putting `scripts/` on `sys.path` (same pattern as tools tests).

Exact file content to implement (adjust only if a local git default-branch quirk requires an extra `git checkout -b main` already present below):

```python
# Copyright (c) 2026 JG Systems Consulting Ltd. See LICENSE.
# SPDX-License-Identifier: MIT
"""Source-Commit ancestor gate for scripts/check_release.py (P6 residual).

Temp git repos via subprocess (not monkeypatched git). Skips when git is
unavailable, matching tests/test_repo_hygiene.py.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_release  # noqa: E402


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            timeout=30,
            text=True,
            encoding="utf-8",
            errors="surrogateescape",
        )
    except (OSError, subprocess.SubprocessError) as exc:
        pytest.skip(f"git unavailable: {exc}")


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    init = _git(repo, "init")
    if init.returncode != 0:
        pytest.skip(f"git init failed: {init.stderr}")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "user.email", "test@example.com")
    # Normalize branch name across git defaults (master vs main).
    _git(repo, "checkout", "-b", "main")
    (repo / "README").write_text("one\n", encoding="utf-8")
    _git(repo, "add", "README")
    commit = _git(repo, "commit", "-m", "c1")
    if commit.returncode != 0:
        pytest.skip(f"git commit failed: {commit.stderr}")
    return repo


def _head(repo: Path) -> str:
    proc = _git(repo, "rev-parse", "HEAD")
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.strip()


def _write_info(repo: Path, body: str) -> None:
    (repo / "RELEASE-INFO.txt").write_text(body, encoding="utf-8")


def test_ancestor_full_hash_passes(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    full = _head(repo)
    _write_info(repo, f"Version: 0.0.0\nSource-Commit: {full}\n")
    assert check_release.check_source_commit(repo) == []


def test_ancestor_short_hash_passes(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    full = _head(repo)
    short = full[:7]
    _write_info(repo, f"Version: 0.0.0\nSource-Commit: {short}\n")
    assert check_release.check_source_commit(repo) == []


def test_phantom_hash_fails(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    phantom = "a" * 40
    _write_info(repo, f"Version: 0.0.0\nSource-Commit: {phantom}\n")
    errs = check_release.check_source_commit(repo)
    assert len(errs) == 1
    assert "does not resolve to a commit" in errs[0]
    assert phantom in errs[0]


def test_real_but_unrelated_non_ancestor_fails(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    # Second lineage not merged into main; pin that tip while HEAD stays on main.
    _git(repo, "checkout", "-b", "other")
    (repo / "README").write_text("other\n", encoding="utf-8")
    _git(repo, "add", "README")
    c2 = _git(repo, "commit", "-m", "c2-other")
    assert c2.returncode == 0, c2.stderr
    other = _head(repo)
    _git(repo, "checkout", "main")
    assert _head(repo) != other
    _write_info(repo, f"Version: 0.0.0\nSource-Commit: {other}\n")
    errs = check_release.check_source_commit(repo)
    assert len(errs) == 1
    assert "not an ancestor of HEAD" in errs[0]
    assert other in errs[0]


def test_malformed_token_fails(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_info(repo, "Version: 0.0.0\nSource-Commit: not-a-hash\n")
    errs = check_release.check_source_commit(repo)
    assert len(errs) == 1
    assert "malformed" in errs[0]
    assert "not-a-hash" in errs[0]


def test_too_short_hex_fails(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_info(repo, "Version: 0.0.0\nSource-Commit: abc\n")
    errs = check_release.check_source_commit(repo)
    assert len(errs) == 1
    assert "malformed" in errs[0]


def test_duplicate_field_fails(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    full = _head(repo)
    _write_info(
        repo,
        f"Source-Commit: {full}\nVersion: 0.0.0\nSource-Commit: {full}\n",
    )
    errs = check_release.check_source_commit(repo)
    assert len(errs) == 1
    assert "duplicate Source-Commit field" in errs[0]


def test_missing_field_fails(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_info(repo, "Version: 0.0.0\n")
    errs = check_release.check_source_commit(repo)
    assert len(errs) == 1
    assert "missing Source-Commit field" in errs[0]


def test_empty_file_missing_field(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_info(repo, "")
    errs = check_release.check_source_commit(repo)
    assert len(errs) == 1
    assert "missing Source-Commit field" in errs[0]


def test_missing_file_skips_validation(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    assert not (repo / "RELEASE-INFO.txt").exists()
    assert check_release.check_source_commit(repo) == []


def test_not_a_git_repository_message(tmp_path: Path) -> None:
    bare = tmp_path / "not-repo"
    bare.mkdir()
    _write_info(bare, "Source-Commit: " + ("b" * 40) + "\n")
    # git may be present but cwd is not a work tree
    try:
        subprocess.run(
            ["git", "--version"],
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        pytest.skip(f"git unavailable: {exc}")
    errs = check_release.check_source_commit(bare)
    assert len(errs) == 1
    assert "not a git repository" in errs[0]
```

Coverage map (dispatch + spec SC5):

| Case | Test |
|---|---|
| Ancestor full hash | `test_ancestor_full_hash_passes` |
| Ancestor short hash | `test_ancestor_short_hash_passes` |
| Phantom hash | `test_phantom_hash_fails` |
| Real-but-unrelated (non-ancestor) | `test_real_but_unrelated_non_ancestor_fails` |
| Malformed | `test_malformed_token_fails` / `test_too_short_hex_fails` |
| Duplicate field | `test_duplicate_field_fails` |
| Missing field | `test_missing_field_fails` / `test_empty_file_missing_field` |
| Missing file skips | `test_missing_file_skips_validation` |
| Not a repository | `test_not_a_git_repository_message` |
| Git unavailable | `_git` / version probe → `pytest.skip` |

Do not require a full `main()` materialization of every REQUIRED path. Helper-level coverage is the bar.

- [ ] **Step 2: Run the new module**

```bash
python -m pytest -q tests/test_release_info_commit.py
```

Expected: all new tests PASS (or skip only if git truly unavailable, in which case report that environment limit). Any FAIL: fix product or test; do not weaken message contracts.

- [ ] **Step 3: Full verification**

```bash
python scripts/check_release.py
python -m pytest -q 2>&1 | tee /tmp/pytest-p6-final.txt | tail -20
for t in vet_source check_overlap outline validate_pack pack_eval; do
  python tools/$t.py --self-check || echo "SELF-CHECK-FAIL $t"
done
```

Expected:

1. `Release gate: OK`, exit 0 on the current tree (SC2).
2. Pytest: baseline recorded in Task 1 + new tests green; still 5 skipped unless git-unavailable added skips in this module only on git-less boxes. Controller dispatch floor was 531 passed / 5 skipped plus new tests; honor the **live** Task 1 baseline + new count.
3. Five-tool self-checks unchanged and green.
4. `RELEASE-INFO.txt` git status clean (no content change).
5. `git diff -- scripts/check_release.py` still shows Source-Commit duty in the docstring (SC7).

- [ ] **Step 4: Acceptance checklist (mirror spec Success criteria)**

Tick only with evidence from Step 3:

- [ ] SC1: Gate fails on missing / malformed (not 7-40 hex) / non-resolvable / non-ancestor `Source-Commit` (tests prove each).
- [ ] SC2: Current tree `python scripts/check_release.py` → `Release gate: OK`, exit 0.
- [ ] SC3: Phantom well-formed hash fails with Source-Commit in the error (test_phantom; optional manual restore probe).
- [ ] SC4: Git cannot execute → fail closed with `Source-Commit check requires git:` (product contract; tests skip when git missing rather than inventing a fake missing binary).
- [ ] SC5: New test module covers good ancestor (full + short), missing field, malformed, non-resolvable, non-ancestor; suite green.
- [ ] SC6: No `RELEASE-INFO.txt` modification; required-file / forbidden / header outcomes unchanged on current tree (gate still OK).
- [ ] SC7: Module docstring names Source-Commit ancestor duty (+ shallow note).
- [ ] Constraint: integrity checkout has `fetch-depth: 0`; tests job checkout untouched.
- [ ] Constraint: pure stdlib; argv-list git only.

- [ ] **Step 5: Commit Task 2**

```bash
git add tests/test_release_info_commit.py
git commit -m "$(cat <<'EOF'
test(release): cover Source-Commit ancestor gate

Temp-repo pytest for phantom, non-ancestor, malformed, duplicate,
missing field, missing file skip, and short/full ancestor pins.
EOF
)"
```

---

## Out of scope (do not do)

- Restamping `RELEASE-INFO.txt` or CHANGELOG (defer version cut; P9 owns release-standard expansion).
- Tag verification, Built stamp rules, RR-S-11 expansion.
- Shallow-clone auto-skip.
- Requiring pin == HEAD.
- New procedure docs under `docs/`.

## Executor notes

- `token + "^{commit}"` is mandatory on Windows-friendly argv lists; never pass through a shell where `^` is escape.
- `findall` + length checks implement exactly-one-match; do not use a silent `search` that ignores duplicates.
- `_SOURCE_COMMIT_LINE` uses `re.M` so `^` / `$` are line-anchored.
- If `git init` default branch already is `main`, `checkout -b main` may fail; in that case use `checkout main` or `init -b main` (`git init -b main` preferred when available). Keep tests green on both git 2.28+ and older.
- Ponytail ceiling: one helper, one YAML key, one test module. No framework, no fixture file factory beyond the local `_init_repo`.
