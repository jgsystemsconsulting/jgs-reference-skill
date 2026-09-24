# Plan: P1 ci-pytest-tool-gates

- date: 2026-09-24
- spec: docs/superpowers/specs/2026-09-24-ci-pytest-tool-gates.md (review pair clean)
- plan_path: docs/superpowers/plans/2026-09-24-ci-pytest-tool-gates.md
- author-leaf: fallback (inline); Opus spawn refused twice on account rate limit
- context: ad-hoc (spec Evidence section, current tree at v0.2.1)
- research: ad-hoc (spec ## Research; actions/setup-python@v5 per the fetched docs pages, same major as shown there; repo already uses actions/checkout@v4)

## Approach

One additive CI job plus one CONTRIBUTING block, with a local baseline run first so a red suite surfaces before CI wiring, not after. Two files change: `.github/workflows/validate.yml` (new `tests` job, updated header comment) and `CONTRIBUTING.md` (runbook block). The integrity job's steps stay byte-identical.

## Task 1: Local baseline (run before anything is wired)

Execute from the repo root in Git Bash and keep the output:

```bash
python -m pip install -e ".[all]" pytest
python -m pytest -q 2>&1 | tail -5
for t in vet_source check_overlap outline validate_pack pack_eval; do python tools/$t.py --self-check || echo "SELF-CHECK-FAIL $t"; done
python -m py_compile tools/*.py scripts/extract.py && echo COMPILE_OK
```

Check first whether `python3` exists on this box (`command -v python3`); use `python` locally where `python3` is absent. CI text stays `python3`.

**Blocking-discovery rule:** if pytest is red or a self-check fails on the current tree, stop this plan, report the failing tests as a finding to the user. Do not patch product code inside P1; CI wiring proceeds only on a locally green baseline (or on explicit user direction otherwise). One carve-out, matching Task 4: a failure of the Windows symlink security test (`tests/test_output_dir_security.py`, Developer Mode missing) is a documented environment limitation; note it in the baseline and continue.

## Task 2: Additive `tests` job in .github/workflows/validate.yml

Update the header comment block (lines 3-5; line 2 of the file is blank) to reflect the second job: the `integrity` job still reads files only apart from `scripts/check_release.py` (`.github/workflows/validate.yml:L84-85`); the new `tests` job executes repository code, read-only, on `pull_request` (not `pull_request_target`), with no secrets, so fork PRs gain no write access. Then append the new job at the end of the file:

```yaml
  tests:
    runs-on: ubuntu-latest
    permissions: read-all

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: pyproject.toml

      - name: Install package and pytest
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[all]" pytest

      - name: Pytest suite
        run: pytest -q

      - name: Tools self-check
        run: |
          for t in vet_source check_overlap outline validate_pack pack_eval; do
              python3 tools/$t.py --self-check
          done

      - name: Compile smoke
        run: python3 -m py_compile tools/*.py scripts/extract.py
```

Constraints while editing: every existing step under the `integrity` job stays byte-identical; indentation matches the file's two-space style; the new job sits after the `integrity` job with no other reordering.

Check: `git diff .github/workflows/validate.yml` shows only the header comment and the appended job.

## Task 3: CONTRIBUTING runbook block

In `CONTRIBUTING.md`, directly under the existing "Before you open a PR" checklist, add a short block:

```markdown
## Run the CI gate locally

CI (`.github/workflows/validate.yml`, `tests` job) runs the same checks:
`pip install -e ".[all]" pytest`, then `pytest -q`, then the self-check loop
above, then `python3 -m py_compile tools/*.py scripts/extract.py`.
Notes: the `.[all]` install needs Python >=3.10 (docling declares `requires_python: <4.0,>=3.10` on PyPI); the symlink
security test (`tests/test_output_dir_security.py:L35` calls `symlink_to`, which raises OSError without the Windows
symlink privilege) needs Windows Developer Mode, so a failure of that one test on
Windows is an environment limitation, not a code defect.
```

(Match the file's heading style and fence widths.)

Check: the block renders as part of CONTRIBUTING.md and names the same four command groups in the same order as the CI job.

## Task 4: Final verification

```bash
python -m pytest -q 2>&1 | tail -3
for t in vet_source check_overlap outline validate_pack pack_eval; do python tools/$t.py --self-check; done
python -m py_compile tools/*.py scripts/extract.py && echo COMPILE_OK
git diff --stat
```

Expected: suite green (or the one documented Windows symlink environment failure, reported as such), all self-checks pass, compile passes, diff touches exactly two files.

## Acceptance criteria

- [ ] `tests` job present in validate.yml, running on push and pull_request, `permissions: read-all`, CPython 3.12, cache keyed on pyproject.toml
- [ ] Integrity job steps byte-identical to before
- [ ] Header comment accurately describes both jobs' security posture
- [ ] CI steps: install `.[all]` + pytest, pytest, five-tool self-check loop, py_compile smoke
- [ ] CONTRIBUTING runbook mirrors CI, notes >=3.10 and the Windows symlink caveat
- [ ] Local baseline captured; any red suite reported as a blocking discovery, not silently patched
- [ ] Diff touches exactly .github/workflows/validate.yml and CONTRIBUTING.md

## Research

- research: ad-hoc (carried from the spec; URLs fetched and verified there)
- https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-python
- https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows
- https://github.com/actions/setup-python (action README; source for the `cache` and `cache-dependency-path` inputs)
- https://pypi.org/pypi/docling/json (docling `requires_python: <4.0,>=3.10`, fetched 2026-09-24)
