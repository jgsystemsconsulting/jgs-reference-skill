# Spec: P1 ci-pytest-tool-gates

- date: 2026-09-24
- project: jgs-reference-skill
- package: P1 (docs/superpowers/packages/2026-09-24-jgs-reference-skill-packages.md)
- author-leaf: fallback (inline); constraints locked at the package proposal stop, no open human questions
- context: ad-hoc (package-loop r1 artifacts supply repo context: the P1 package section, findings I1 and I10 in docs/superpowers/reviews/2026-09-24-jgs-reference-skill-findings.md)
- research: ad-hoc (see ## Research)

## Problem

The repository's only GitHub Actions workflow, `.github/workflows/validate.yml`, is a deliberately self-contained content-integrity gate: inline bash and python3 stdlib only, it never installs dependencies and never runs the test suite; apart from `scripts/check_release.py`, its steps read files only. It greps content, lints SKILL.md frontmatter, checks version-string consistency, and runs that release script. Consequences, verified in the repo review (findings I1 and I10, both PASS):

- The pytest suite in `tests/` (3,454 non-empty lines of 4,480 total; CHANGELOG.md:L34 says "452 passed, 5 skipped" at vendoring time), including the in-tree security regression suite (symlink and ownership locks, Unicode sanitization, injection scan, DOCX safety), cannot fail a pull request.
- The tools self-check loop CONTRIBUTING requires (`vet_source`, `check_overlap`, `outline`, `validate_pack`, `pack_eval`) never runs in CI.
- The extraction and pack pipeline is never compile-checked or imported by CI, so syntax and import breaks ship green.
- CONTRIBUTING's "Before you open a PR" checklist names self-checks and `py_compile` but never pytest, so contributors have no documented command that validates the engine.

Green main can therefore ship broken extractors, weakened licence gates, or regressed security boundaries with no red signal. Every later package (P2-P4 harden exactly those surfaces) depends on a CI fail path to stay fixed.

## Evidence

- `.github/workflows/validate.yml:L3-5`: `# Self-contained content-integrity gate. Inline bash + python3 stdlib only.` and `# Does NOT execute any checked-out repository code (reads files only)`
- `.github/workflows/validate.yml:L84-85`: the release gate step runs only `python3 scripts/check_release.py`
- `CONTRIBUTING.md:L26-34`: PR checklist is the five-tool self-check loop plus `py_compile`; pytest is absent
- `pyproject.toml:L16-25`: optional extras (`epub`, `pdf`, `docx`, `rtf`, `technical`, `all`); the tools are documented pure stdlib
- `CHANGELOG.md:L34`: `- tests/: upstream suite carried over (452 passed, 5 skipped).`
- `tests/test_output_dir_security.py:L31-38`: `test_prepare_output_dir_rejects_symlink`, representative of the security suite CI never runs

## Goals

1. A new CI job, `tests`, in `.github/workflows/validate.yml` that runs on push and pull_request and fails on: pytest failures, tools self-check failures, or pipeline compile breaks.
2. The job installs the project with its extras plus pytest itself (`pip install -e ".[all]" pytest`; pyproject declares pytest in no extra), runs `pytest`, runs the five-tool self-check loop, and runs `python3 -m py_compile tools/*.py scripts/extract.py` as a smoke.
3. CONTRIBUTING.md documents one runbook command sequence that mirrors the CI tests job, so a contributor can reproduce the gate locally; the block notes that the `.[all]` install needs Python >=3.10.
4. `actions/setup-python` provisions Python, with pip caching, per current GitHub guidance (see Research).

## Non-goals

- No rewrite of the content-integrity greps or the release gate step; they stay byte-identical in behavior.
- No new test frameworks, no coverage quotas, no matrix builds, no artifacts/reports upload.
- No fixes to product bugs the suite may reveal in P2-P4 territory; if the suite currently fails on main, that is a blocking discovery to report, not something this package silently patches beyond CI wiring.
- Out of scope (other packages): scaffold hardening (P2), vet licence matching (P3), Step 9 verify gates (P4), install/docs (P5), RELEASE-INFO commit pin (P6), user-scope toolchain (P7).

## Approach

Add a second job to the existing workflow rather than executing code inside the `integrity` job. The integrity job's security guarantee ("does NOT execute any checked-out repository code, so a fork PR cannot gain write access") is load-bearing; a separate `tests` job preserves it verbatim while still executing repo code on PRs. The `tests` job:

- `runs-on: ubuntu-latest`, `permissions: read-all`, no secrets. Fork-PR safety comes from the `pull_request` (not `pull_request_target`) trigger and the read-only token (`.github/workflows/validate.yml:L4-5, L11`), so fork-PR execution of repo code touches nothing sensitive (standard open-source pattern).
- Steps: checkout; `actions/setup-python` pinned to CPython 3.12 (tested floor: the docling extra requires >=3.10; the repo's `requires-python` floor is 3.9), with `cache: pip` and `cache-dependency-path: pyproject.toml` (the repo ships no requirements.txt or lock file); `pip install -e ".[all]" pytest`; `pytest`; the self-check loop from CONTRIBUTING; the `py_compile` smoke.
- Job order does not gate on `integrity` (independent jobs, faster feedback; both must pass before merge).

CONTRIBUTING.md gains a short "Run the CI gate locally" block under the existing PR checklist with the same commands in the same order.

## Constraints (locked)

1. Existing workflow steps stay byte-identical; the changes are an additive `tests` job, an updated fork-PR safety header comment, and an additive CONTRIBUTING block.
2. The three CI surfaces: pytest, self-check loop, py_compile smoke.
3. One runbook command sequence in CONTRIBUTING that mirrors CI.
4. Windows dev box, Linux runners: the runbook block notes any bash-specific syntax; the plan verifies the suite passes locally on Windows before relying on it as the gate. The suite's symlink test needs Windows Developer Mode; the runbook notes it, and a documented environment failure there is acceptable for the local-green check.
5. Written prose standard for all edited docs: no em dashes, staff-engineer voice.

## Success criteria

- `tests` job exists, runs on push and pull_request, and is green on the current tree (if it is red, the finding is reported and handled as a blocking discovery, not hidden).
- `integrity` job unchanged: same steps, same read-only guarantee.
- CONTRIBUTING documents the runbook; the runbook was executed once locally on this Windows box with output kept.
- All existing workflow-level properties hold: `permissions: read-all`, `on: push/pull_request`, fork-PR safety commentary updated to reflect the second job.

## Research

- research: ad-hoc (GitHub Actions Python/pytest wiring is an external platform choice)
- https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-python ("Building and testing Python": running pytest with actions/setup-python; fetched and verified 2026-09-24)
- https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows (caching dependencies: setup-python `cache: 'pip'`; fetched and verified by the correspondent lens, 2026-09-24)
- Two URLs from the initial search (realpython.com/github-actions-python, pytest-with-eric.com) returned 403/404 on fetch and were dropped as unverifiable.
