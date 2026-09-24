# Spec: P6 release-info-real-commit (residual)

- date: 2026-09-24
- project: jgs-reference-skill
- package: P6 (docs/superpowers/packages/2026-09-24-jgs-reference-skill-packages.md)
- scope: residual only (stale pin already fixed by v0.2.1)
- author-leaf: fallback (inline); Claude-pinned leaf unavailable; residual scope locked by controller
- context: ad-hoc (P6 package section; findings I5; scripts/check_release.py full; RELEASE-INFO.txt; CHANGELOG 0.2.1; validate.yml RR-B-15 + RR-S-11; grep docs/ for RELEASE-INFO)
- research: skipped (internal tool hardening; no external APIs, libraries, or version-sensitive choices)

## Research

research: skipped (internal tool hardening; no external APIs, libraries, or version-sensitive choices)

## Premise (controller-verified, 2026-09-24)

Do not re-open the original I5 pin rewrite. Record and treat as closed:

1. `RELEASE-INFO.txt` is truthful today: `Version: 0.2.1`, `Source-Commit: ff4cb7360d4c8a24e7ddc5a7ea5a13dd22beb54f` (a real commit on main).
2. The old pin `1c8b781` is now an ancestor of main via the hyg-03 merge; the v0.2.1 release work already corrected the public provenance line (CHANGELOG 0.2.1 Fixed entry).
3. Residual gap only: `scripts/check_release.py` has **no** `Source-Commit` validation (confirmed by reading the full 88-line script). The RR-B-15 gate still stays green if a future release pins a phantom, malformed, or non-ancestor hash. That is this package's entire remaining scope.

## Problem

I5 (`release-info-stale-commit`) found that `RELEASE-INFO.txt` pinned `Source-Commit: 1c8b781`, a hash then absent from recorded history, while version and Built stamps had already moved. Public 0.2.0 provenance was a frozen lie: reproducibility and the audit trail failed the release-standard bar the tree claimed.

The data defect is fixed. The process defect is not.

`scripts/check_release.py` is the RR-B-15 release gate invoked by `.github/workflows/validate.yml` (`Release gate (RR-B-15)` step). Today it only:

1. Asserts a fixed list of required paths exist (including `RELEASE-INFO.txt` as a file).
2. Scans tracked text-ish files for forbidden content (private-key blocks, the split CONFIDENTIAL sentinel).
3. Requires `Copyright (c)` and `SPDX-License-Identifier` in the first 600 bytes of first-party tracked `*.py`.

It never opens `RELEASE-INFO.txt` for field content. A parallel integrity step (RR-S-11 version consistency) only regex-reads the `Version:` line and compares it to CHANGELOG / pyproject / plugin.json. Neither step looks at `Source-Commit:`.

Consequence: a future release can again ship a hash that is missing, malformed, not a git object, or not an ancestor of HEAD, and both the version job and the release gate stay green. The original failure mode returns the moment someone hand-edits the pin wrong.

## Goals

### 1. Source-Commit validation inside `check_release.py`

Add one validation step to the existing release gate. Behavior is normative.

#### 1.1 Parse

After the required-file loop (so a missing `RELEASE-INFO.txt` still reports `required file missing` and does not double-fault on parse), read `ROOT / "RELEASE-INFO.txt"` as UTF-8.

Extract the `Source-Commit` value with a line-anchored match equivalent to:

```text
^Source-Commit:\s*(\S+)\s*$
```

(multiline). Exactly one capturing group: the token after the label.

Parse failures that append to `errors` (same list / `::error::` reporting path as today):

| Condition | Error message (normative prefix) |
|---|---|
| File unreadable (`OSError`) | `RELEASE-INFO.txt: unreadable: <exc>` |
| No matching `Source-Commit:` line | `RELEASE-INFO.txt: missing Source-Commit field` |
| More than one `Source-Commit:` line | `RELEASE-INFO.txt: duplicate Source-Commit field` (exactly one match required) |
| Captured token empty after strip (should not happen with `\S+`, defensive) | `RELEASE-INFO.txt: empty Source-Commit value` |

#### 1.2 Accepted hash forms

Accept only a pure hexadecimal object name, length 7 to 40 inclusive, case-insensitive:

```text
^[0-9a-fA-F]{7,40}$
```

Reject (append error, do not call git):

| Condition | Error message |
|---|---|
| Token fails the hex/length regex | `RELEASE-INFO.txt: Source-Commit malformed (want 7-40 hex chars): <token>` |

Rationale: the truthful pin today is a full 40-hex SHA-1; the historical bad pin was a 7-hex short form. Both shapes are real git abbreviations. Reject anything with non-hex characters, whitespace inside the token, `g` prefixes, tags, branch names, or `HEAD` so the field stays a commit id, not a ref alias.

#### 1.3 Resolve + ancestor check

Work directory for every git call: `ROOT` (repo root, same as existing `_tracked_py`).

Steps, in order:

1. **Resolve to a commit object.**
   ```bash
   git rev-parse --verify <token>^{commit}
   ```
   - Success: stdout is the full 40-hex object name (use stripped stdout as `resolved`).
   - Non-zero exit, or empty stdout: append
     `RELEASE-INFO.txt: Source-Commit does not resolve to a commit: <token>`
     and stop this check (do not run the ancestor step).

2. **Require ancestor of HEAD.**
   ```bash
   git merge-base --is-ancestor <resolved> HEAD
   ```
   - Exit 0: pass (no error).
   - Exit 1: append
     `RELEASE-INFO.txt: Source-Commit is not an ancestor of HEAD: <resolved>`
   - Any other non-zero (git failure): append
     `RELEASE-INFO.txt: Source-Commit ancestor check failed: <stderr-or-reason>`

Rationale for ancestor-of-HEAD (not mere `cat-file -e`):

- `git cat-file -e <hash>^{commit}` only proves the object exists in the local object database. A commit from an unrelated fetch, a replaced object, or another branch tip can exist and still be absent from the line of history this tree claims to release.
- I5's blast was "hash that does not appear in the recorded git history" / frozen provenance for the published line. Ancestor-of-HEAD is the check that matches that intent on a github-hosted full checkout and on a normal local clone of main.
- CI reality: `actions/checkout@v4` defaults to `fetch-depth: 1`, a shallow clone, so the ancestor check WOULD false-fail on every runner run unless the checkout is deepened. This package therefore adds `with: fetch-depth: 0` to the integrity job's checkout step in `.github/workflows/validate.yml` (the one additive workflow line, existing step otherwise untouched). The module docstring documents that shallow local clones may false-fail the ancestor check and operators must `git fetch --unshallow` (or deepen) before relying on the gate locally. Do not auto-skip on shallow.

Do **not** require that `Source-Commit == HEAD`. A release pin may intentionally name the commit that produced the tagged artefact while later docs-only commits land on main; ancestor is the honesty bar, equality is not.

#### 1.4 Git unavailable

If invoking git raises `FileNotFoundError` / `OSError` (executable missing) or `subprocess` cannot start:

- Append `RELEASE-INFO.txt: Source-Commit check requires git: <exc>`
- Fail the gate (non-zero exit via the existing errors path).

Do **not** skip. Rationale: `_tracked_py` already calls `git ls-files` with `check=True` and will crash the process if git is missing; the workflow runs on `ubuntu-latest` with git present; local release checks also have git. Skipping would re-open the hole this package closes. Failing closed is correct.

If git runs but the cwd is not a git work tree (`rev-parse` fails before resolve), treat it as a resolve/ancestor failure with a clear message, same fail-closed path.

#### 1.5 Integration shape

Recommended (not sacred if behaviour holds):

- Extract a helper `check_source_commit(root: pathlib.Path) -> list[str]` that returns zero or more error strings and never calls `sys.exit`.
- `main` does `errors.extend(check_source_commit(ROOT))` after the required-file loop and before or after the forbidden-content / header loops (order among those three is not load-bearing; required-file-before-parse is).
- Keep using `subprocess.run` with `capture_output=True`, `text=True`, `cwd=root`. Pure stdlib only (already true: the file imports subprocess inside `_tracked_py` today; a top-level or helper-level import is fine).
- Do not change the success line `Release gate: OK`, the `::error::` prefix, or the `FAILED: N issue(s).` summary.
- Update the module docstring one line to name the new duty: required files, forbidden content, first-party headers, **and Source-Commit resolves to an ancestor of HEAD**.

### 2. Tests

Add pytest coverage in the existing suite style (`tests/`, stdlib + pytest, no new frameworks).

**Chosen approach: temp git repository via subprocess** (not monkeypatched fake git). Matches `tests/test_repo_hygiene.py`'s real-git posture and exercises `rev-parse` / `merge-base` for real; also specify: a missing RELEASE-INFO.txt is reported once by the required-file check and the commit validation is then skipped (no double fault); a checkout that is not a git work tree at all gets a dedicated not-a-repository message via a `git rev-parse --git-dir` probe; follow that file's convention of `pytest.skip` when git is unavailable so git-less dev boxes skip rather than error.

File: `tests/test_check_release_source_commit.py` (new).

Fixture pattern (normative intent):

1. `tmp_path` git repo: `git init`, set user.name/email locally, one or more commits on the default branch, `HEAD` at the tip.
2. Write a minimal `RELEASE-INFO.txt` into that repo with a controllable `Source-Commit` line (other fields may be stubs; the helper only reads Source-Commit).
3. Call `check_source_commit(tmp_path)` (import the helper from `scripts/check_release.py`; add `scripts/` to `sys.path` or import via path hook the way other tool tests do if needed). Prefer testing the helper directly so tests do not need the full REQUIRED file tree.

Cases that must exist (names indicative):

| Case | Setup | Expect |
|---|---|---|
| current-style full hash ancestor | Source-Commit = full 40-hex of an ancestor (or HEAD) | `[]` |
| short hash ancestor | Source-Commit = unique 7+ hex prefix of an ancestor | `[]` |
| missing field | file without Source-Commit line | one error, mentions `missing Source-Commit` |
| malformed token | `Source-Commit:  not-a-hash` or `zzzzzzz` | one error, mentions `malformed` |
| too short | `Source-Commit: abc` (3 hex) | malformed |
| phantom hash | well-formed 40-hex that is not any object | does not resolve |
| non-ancestor | second branch commit not merged; pin that tip while HEAD stays on mainline | not an ancestor |
| empty / whitespace-only file | no field | missing field |

Git-unavailable: optional if hard to force portably; the fail-closed contract is specified above and may be left to manual/CI reality. Do not skip the ancestor cases.

Do **not** require a full `main()` integration test that materializes every REQUIRED path unless it is cheap; helper-level coverage is the bar.

### 3. Docs touch (minimal)

- Module docstring only, as in Goal 1.5.
- No `RELEASE-INFO.txt` content change.
- No CHANGELOG entry required by this residual package unless the implementer is already cutting a release note for the gate hardening; if a CHANGELOG line is added, keep it one bullet under Fixed or Added naming the Source-Commit ancestor check in `check_release.py`. Prefer deferring CHANGELOG to the next version cut if the tree is not otherwise releasing (ponytail: do not invent a version bump for a gate-only fix unless the release procedure already demands it). P9 owns full release-standard expansion.

No dedicated release-procedure markdown exists under `docs/` today (grep: RELEASE-INFO appears in CHANGELOG, validate.yml, bug_report template, and superpowers artifacts; scripts/check_release.py's own REQUIRED list also names it, which is the gate being extended here). Do not create a new procedure doc in P6.

## Non-goals

- Rewriting or restamping `RELEASE-INFO.txt` (already truthful).
- Built (UTC) stamp semantics, freshness, or timezone rules.
- Tag creation, tag moving, or verifying `Tag:` against `git describe`.
- Changelog archaeology or rewriting past 0.2.0 notes.
- Expanding RR-S-11 to cross-check Source-Commit (stays version-only).
- Full release-repo-standard checklist expansion (P9).
- Changing forbidden-content, required-file list (beyond reading the existing RELEASE-INFO entry), or licence-header checks.
- Shallow-clone auto-detection with skip (fail closed instead; document only).
- Requiring Source-Commit == HEAD.

## Constraints (locked)

1. The integrity job's checkout step gains `with: fetch-depth: 0`, the one additive line in `.github/workflows/validate.yml`, existing step otherwise untouched. Pure stdlib in `scripts/check_release.py`. `subprocess` to git is allowed and already used.
2. `RELEASE-INFO.txt` bytes unchanged by this package.
3. No other check_release behaviours altered: same required list, same forbidden patterns, same header rules, same exit 0/1 contract, same `::error::` reporting.
4. Written prose standard on any durable prose touched (module docstring is short; no em dashes).
5. Windows dev + Linux CI: git invocations must work on both; avoid shell `True` and rely on `subprocess` argument lists (already the file's style).

## Success criteria

1. `scripts/check_release.py` reads `Source-Commit` from `RELEASE-INFO.txt` and fails the gate when the field is missing, malformed (not 7-40 hex), non-resolvable as a commit, or not an ancestor of `HEAD`.
2. On the current tree (truthful full-hash pin that is an ancestor of HEAD), `python scripts/check_release.py` still prints `Release gate: OK` and exits 0.
3. A deliberate local edit of `Source-Commit` to a well-formed phantom hash makes the gate exit non-zero with an error that names Source-Commit; restoring the file returns green. (Manual or test-proven.)
4. When git cannot be executed, the new check fails closed with an explicit error (does not skip).
5. `tests/test_check_release_source_commit.py` covers at least: good ancestor (full and short), missing field, malformed token, non-resolvable hash, non-ancestor hash; suite green under the existing pytest job.
6. No modification to `RELEASE-INFO.txt`, and no change to required-file / forbidden-content / header-check outcomes on the current tree.
7. Module docstring names the Source-Commit ancestor duty.

## Evidence (residual)

- `scripts/check_release.py`: 88 lines; REQUIRED includes `RELEASE-INFO.txt`; no `Source-Commit` string anywhere in the file; git used only in `_tracked_py` via `git ls-files`.
- `RELEASE-INFO.txt:L5`: `Source-Commit:  ff4cb7360d4c8a24e7ddc5a7ea5a13dd22beb54f` (truthful).
- `CHANGELOG.md` 0.2.1 Fixed: names the real reachable Source-Commit and v0.2.1 tag.
- `.github/workflows/validate.yml`: RR-S-11 reads only `Version:`; RR-B-15 runs `python3 scripts/check_release.py`.
- Findings I5 and package P6 original in-scope text required both a real pin **and** a guard so a phantom cannot ship again; residual scope is the guard alone.
- Docs grep: no release-procedure runbook under `docs/` currently instructs how to refresh RELEASE-INFO; P9 remains the expansion vehicle.
