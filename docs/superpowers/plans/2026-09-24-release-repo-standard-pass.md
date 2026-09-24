# Plan: P9 release-repo-standard-pass

- date: 2026-09-24
- spec: docs/superpowers/specs/2026-09-24-release-repo-standard-pass.md (reviewed clean; audit gap table, Recorded RR-S-12 deviation, CITATION author note, and Success criteria are binding)
- plan_path: docs/superpowers/plans/2026-09-24-release-repo-standard-pass.md
- author-leaf: claude unavailable; plan-author fallback (inline on sdd-executor-deep seat)
- context: ad-hoc (spec audit table is the work list; live tree sampled 2026-09-24: CITATION.cff 0.2.0 + dual authors; README badge/prompt 0.2.0; SECURITY supported 0.1.x only; CHANGELOG top `## 0.2.1` with no Unreleased; check_release lacks forbidden-paths class and RR-B-37; no DISTRIBUTION.md / PR template / improvement form / SKILLS.md / .cursor-plugin / gemini-extension.json; landing `#use` only; packs/ untracked demo-contract; validate.yml version step omits CITATION/README)
- research: skipped (carried from spec)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close every in-repo MUST gap from the P9 audit table against release-repo-standard v1.16 (Base + RR-S), record SHOULD/N-A decisions in `docs/DISTRIBUTION.md`, leave version-bearing customer surfaces truthful at **0.2.1**, extend `scripts/check_release.py` with an explicit forbidden-paths class and RR-B-37 escape guard, and finish with a recorded de-slop pass plus CI-equivalent green gates. No version bump to 0.2.2, no push, no GitHub Release create, no P1-P8 redesign, no P7.

**Architecture:** Two tasks. Task 1 closes every in-repo gap from the audit table in the spec's closure order (version truth → ledger + keep/drop + gate → community surfaces → host manifests + SKILLS.md → landing micro-align + honesty docs → CHANGELOG Unreleased). Task 2 is the recorded Technical-Writer de-slop pass over every human-facing file Task 1 touched, then the full verification battery (check_release, pytest, five-tool self-check, compile, landing_taste, link check, greps). Publish-time MUSTs stay handoff-only.

**Tech stack:** Existing repo Python 3.9+ stdlib gates; Git Bash; optional copy of `~/.zcode/skills/release-repo-standard/tools/landing_taste.py` run in-place without vendoring; `gh` only for read-only About inspection and documented maintainer commands. No new project dependencies. No filter-repo.

**Version policy (normative, from spec):**

| Question | Answer |
|---|---|
| Release version under audit | **0.2.1** (tag exists; do not move) |
| Cut 0.2.2 in this package? | **No** |
| Post-tag hygiene vehicle | `## [Unreleased]` in CHANGELOG only |
| May RELEASE-INFO / tags / pyproject move off 0.2.1? | **No** |
| Missing GitHub Release v0.2.1 | Publish-time MUST; out of package |

**Pinned values already correct (confirm; do not "fix"):**

| Surface | Expected |
|---|---|
| `RELEASE-INFO.txt` Version / Tag | `0.2.1` / `v0.2.1` |
| `pyproject.toml` `[project].version` | `0.2.1` |
| `.claude-plugin/plugin.json` version | `0.2.1` |
| `docs/index.html` REV + JSON-LD `softwareVersion` | `0.2.1` |
| CHANGELOG top **released** heading | `## 0.2.1 - 2026-09-24` (Unreleased goes **above** it) |

**Drift to fix (must become 0.2.1):**

| Surface | Today |
|---|---|
| `CITATION.cff` `version` / `date-released` | `0.2.0` / `2026-09-23` |
| README version badge | `version-0.2.0` |
| README agent-install prompt | `v0.2.0` |

## Approach

Minimum diffs. Prefer standard templates under `~/.zcode/skills/release-repo-standard/templates/` as the source of shape, filled with this product's strings. Do not redesign landing, installer, or tools. Do not reopen P1-P8 product decisions. Customer-surface de-slop only (README, CHANGELOG, SECURITY, CONTRIBUTING, CITATION, DISTRIBUTION, docs/*.md, docs/*.html, new GitHub templates); `docs/superpowers/**` stays maintainer process history under the freeze decision and is excluded from customer em-dash grep.

## Blocking-discovery rule

Before any product edit, run from the repo root in Git Bash:

```bash
python scripts/check_release.py
python -m pytest -q 2>&1 | tail -20
for t in vet_source check_overlap outline validate_pack pack_eval; do
  python tools/$t.py --self-check || echo "SELF-CHECK-FAIL $t"
done
python -m py_compile tools/*.py scripts/extract.py scripts/check_release.py
```

Use `python` locally when `python3` is absent; CI and doc command blocks stay `python3`.

Baseline expectations at plan time: `check_release.py` prints `Release gate: OK` and exits 0; pytest is green aside from the documented Windows symlink `OSError` carve-out in `tests/test_output_dir_security.py` (Developer Mode missing) noted in CONTRIBUTING; five self-checks exit 0. Spec acceptance cites **pytest 543 passed / 5 skipped** when that is the local count; record the actual `N passed, M skipped` line you get and treat any new failure (other than the symlink carve-out) as a blocker.

If check_release is red, or pytest is red beyond the symlink carve-out, or any of the five self-checks fails on the **current** tree before your edits: **stop and report**. Do not silently patch product code to green an unrelated baseline.

**Release / publish stop rule:** if any standard MUST cannot be closed without creating a GitHub Release, pushing to origin, force-pushing, rewriting history, cutting 0.2.2, changing branch protection via API write, or submitting a marketplace web form: **stop and report** that item as publish-time / maintainer-only. Do not invent a local substitute that claims the MUST met. Record the handoff in `docs/DISTRIBUTION.md` and in the package notes list (Success criterion 14).

Re-run check_release after the gate extension lands. Re-run pytest + five-tool self-check after any Python change. Task 2 owns the final full battery.

---

## Task 1: Close in-repo audit gaps

**Files (create / modify; no deletes of shippable product):**

| Action | Path |
|---|---|
| Modify | `CITATION.cff` |
| Modify | `README.md` |
| Modify | `SECURITY.md` |
| Modify | `CHANGELOG.md` |
| Modify | `scripts/check_release.py` |
| Modify | `.gitignore` |
| Modify | `.github/workflows/validate.yml` (version-consistency step only) |
| Modify | `docs/index.html` (`#usage` compatibility only) |
| Modify | `docs/other-agents.md` (Codex path honesty) |
| Modify | `CONTRIBUTING.md` (commit-identity policy + optional test list pointer) |
| Create | `docs/DISTRIBUTION.md` |
| Create | `.github/pull_request_template.md` |
| Create | `.github/ISSUE_TEMPLATE/improvement.yml` |
| Create | `SKILLS.md` |
| Create | `.cursor-plugin/plugin.json` |
| Create | `.cursor-plugin/marketplace.json` |
| Create | `gemini-extension.json` |
| Create | `.agents/plugins/marketplace.json` (Codex native marketplace file) |
| Optional create | `scripts/configure_repo.sh` only if you document exact `gh repo edit` commands there; else put commands in DISTRIBUTION only |

Do **not** modify: `RELEASE-INFO.txt`, `pyproject.toml` version, `.claude-plugin/plugin.json` version, landing REV/JSON-LD version strings (already 0.2.1), `book_to_skill/`, tool behaviour, install.py targets (docs honesty only for Codex), P7 repos, git history.

### 1.1 Version truth (RR-B-09 / RR-B-05 / RR-B-16 / RR-B-31 / RR-S-09 / RR-S-11)

- [ ] **CITATION.cff** set exactly:

```yaml
cff-version: 1.2.0
message: "If you use this software, please cite it as below."
title: "jgs-reference-skill"
version: 0.2.1
date-released: 2026-09-24
url: "https://github.com/jgsystemsconsulting/jgs-reference-skill"
repository-code: "https://github.com/jgsystemsconsulting/jgs-reference-skill"
license: MIT
type: software
authors:
  - name: "JG Systems Consulting Ltd"
    website: "https://www.jgsystemsconsulting.com"
```

Author list is **organization only** (spec CITATION author note). Keep virgiliojr94 credit in `ATTRIBUTION.md` / `NOTICE` only; do not re-add that person as a CITATION.cff author.

- [ ] **README.md** badge line (currently L6): replace
  `version-0.2.0-informational` with `version-0.2.1-informational`.
- [ ] **README.md** agent-install block (currently L64): replace
  `(v0.2.0)` with `(v0.2.1)`.
- [ ] Confirm no other customer-facing `0.2.0` version claims remain outside CHANGELOG historical sections and `docs/superpowers/**`:

```bash
rg -n "0\.2\.0" README.md CITATION.cff SECURITY.md RELEASE-INFO.txt pyproject.toml \
  docs/index.html docs/skill-usage.md docs/other-agents.md docs/PACK-SPEC.md \
  docs/SOURCE-VETTING.md SKILL.md SKILLS.md .claude-plugin/ .cursor-plugin/ \
  gemini-extension.json .agents/ 2>/dev/null
```

Historical CHANGELOG `## 0.2.0` section stays. Fix any unexpected live drift.

- [ ] **validate.yml** version-consistency step: extend the inline Python so the agreed set includes at least:
  - existing: CHANGELOG top **released** semver (must still ignore a leading `## [Unreleased]`), RELEASE-INFO, pyproject, `.claude-plugin/plugin.json`
  - **add:** `CITATION.cff` `^version:\s*` value
  - **add:** README badge version via regex on `version-(\d+\.\d+\.\d+)-informational`
  - **add:** README agent-install `(v(\d+\.\d+\.\d+))` near `jgs-reference-skill`
  - **add when files exist:** `.cursor-plugin/plugin.json` `version`, `gemini-extension.json` `version`
  - **add:** landing `softwareVersion` from `docs/index.html` JSON-LD (and/or `REV <b>…</b>`) so REV cannot drift silently

  Keep exit-on-mismatch behaviour. Do not require CHANGELOG Unreleased to parse as a version.

- [ ] **check_release.py** (same task as 1.3): add a version-agreement helper or inline checks for CITATION.cff + README badge (and prompt if cheap) against RELEASE-INFO `Version:`, so local gate catches the same class of drift without waiting for CI. Prefer one small function `check_version_agreement(root) -> list[str]` rather than a second script.

### 1.2 SECURITY supported versions (RR-S-10)

- [ ] **SECURITY.md** supported-versions table becomes the 0.2.x line. Exact target:

```markdown
## Supported versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | yes |
| 0.1.x   | no |

Only the latest released `0.x` line receives security fixes.
```

Prefer plain `yes`/`no` over emoji if editing the cell (de-slop-friendly). Do not change the advisory reporting route.

### 1.3 Distribution ledger + keep/drop + escape guard (RR-B-36 / RR-B-35 / RR-B-37 / RR-B-15 / RR-B-19 / RR-B-27 / RR-B-29b / RR-S-17)

- [ ] **Create `docs/DISTRIBUTION.md`** from the standard tmpl shape, filled for this product. Required content:

  - HTML copyright comment naming JG Systems Consulting Ltd + MIT / LICENSE pointer (match other docs/`*.md` headers).
  - Title: `Distribution ledger · jgs-reference-skill`
  - `Last reviewed: 0.2.1 / 2026-09-24`
  - Agent rule restated: an agent never marks a row `submitted`.
  - **In-host marketplaces** table with rows at minimum:
    - Claude Code / `.claude-plugin/` → status reflecting manifest shipped; directory submission `planned` or `deferred` with reason/date (not submitted).
    - Cursor / `.cursor-plugin/` → manifest ships this package; marketplace submission deferred/planned with date.
    - OpenAI Codex / `.agents/plugins/` → manifest ships; submission planned/deferred with date.
    - Gemini CLI / `gemini-extension.json` → manifest ships; gallery submission planned/deferred with date.
  - **Web directories & catalogues** table:
    - Org catalogue (RR-B-19): `deliberate N/A` or `planned` with dated reason (no live org catalogue entry today).
    - GitHub About + topics + Release (RR-B-21 / RR-B-22): record current state; Release v0.2.1 **missing** as publish-time MUST; About description em-dash strip + topic polish as maintainer `gh repo edit` handoff (no push in package).
    - Community awesome-lists / directories (RR-B-29b): deferred with date; agent must not mark submitted.
  - **No MCP aggregator section** (not an MCP bridge); one line `RR-M-*: N/A (not an MCP bridge)`.
  - **RR-B-27 history policy:** inherited upstream + personal emails retained; **new commits MUST** use `245595077+jgsystemsconsulting@users.noreply.github.com`. No filter-repo in P9.
  - **RR-B-35 keep/drop (dated 2026-09-24):**
    - `docs/superpowers/`: **keep**, frozen process history for this cut.
    - `.zcode/`, `.superpowers/`: remain gitignored session dirs (never track).
    - `packs/`: **gitignore** (local pack outputs / demos; do not commit).
  - **RR-S-17:** feedback utility skill **deferred** (SHOULD), dated 2026-09-24, reason: keep P9 minimum; tracker already has improvement form.
  - **RR-S-12 deviation** cross-link: point at CHANGELOG Unreleased note (full text lives in CHANGELOG).
  - **RR-B-26:** README already ships a mermaid pipeline diagram; record as met (or explicit defer if you judge it insufficient). Do not add a second diagram unless free.
  - **Publish-time handoff list** (mirrors Success criterion 14): GitHub Release `v0.2.1` body from CHANGELOG 0.2.1 + licence-enquiry URL footer; optional About description em-dash removal; optional topics (`cursor`, host tags); directory submissions.

- [ ] **`.gitignore`:** append a clear block:

```gitignore
# Local generated / demo packs (never commit pack outputs)
packs/
```

Confirm `.zcode/` and `.superpowers/` rules remain. Do not delete on-disk `packs/` or `docs/superpowers/`.

- [ ] **`scripts/check_release.py`:** extend to the standard RR-B-15 / RR-B-37 shape while keeping existing Source-Commit ancestor logic and current REQUIRED list (extend REQUIRED as files land). Concrete requirements:

  1. Module docstring mentions forbidden paths + escape guard.
  2. **`FORBIDDEN_PATH_PARTS`** list exists as an explicit named class (required even if you start from the template defaults). Use at least:

     ```python
     FORBIDDEN_PATH_PARTS = [
         "__pycache__", ".venv", ".worktrees", ".pytest_cache",
         ".ruff_cache", ".bak",
     ]
     ```

     Judge the **tracked** tree via `git ls-files` (local gitignored dirs are fine). Fail with `forbidden tracked path: …`.

  3. **RR-B-37 escape guard** constants (edit from keep/drop):

     ```python
     NEVER_TRACK = (".zcode/", ".superpowers/")
     IGNORE_RULES: tuple[str, ...] = (".zcode/", ".superpowers/", "packs/")
     FROZEN_TREES: dict[str, str] = {
         # filled in step below after intentional superpowers set is final
         # "docs/superpowers/": "<sha256>",
     }
     ```

     - Fail if any tracked path `startswith` a `NEVER_TRACK` prefix.
     - Fail if `.gitignore` text lacks each `IGNORE_RULES` entry (substring match is enough, matching the standard template).
     - For each `FROZEN_TREES` prefix: `files = sorted(f for f in tracked if f.startswith(prefix))`; `hashlib.sha256("\n".join(files).encode()).hexdigest()` must equal baseline; on mismatch fail with a message that says to update `FROZEN_TREES` if deliberate.

  4. **Compute the freeze hash only after** all intentional paths under `docs/superpowers/` for this package are already on disk and will be committed together (this plan + spec (freeze the hash only after `git add` of every intentional superpowers artifact, then recompute) already count). Implementer procedure at end of Task 1 (or end of package before final gate):

     ```bash
     python - <<'PY'
     import hashlib, subprocess
     files = sorted(
         subprocess.check_output(["git","ls-files","docs/superpowers"], text=True)
         .splitlines()
     )
     # include untracked-but-about-to-add paths by also listing via git status -z if needed;
     # final baseline MUST match exactly what `git ls-files docs/superpowers` returns AFTER git add
     print(len(files))
     print(hashlib.sha256("\n".join(files).encode()).hexdigest())
     PY
     ```

     After `git add` of any new superpowers paths this package owns, recompute and set `FROZEN_TREES["docs/superpowers/"]` in the same commit. If Task 2 adds no superpowers files, one baseline at end of Task 1 is enough. Do not freeze an empty dict and claim RR-B-37 met.

  5. Keep existing: REQUIRED loop, `check_source_commit`, forbidden-content scan, headers-on-tracked-py. Add new required files once created:

     - `docs/DISTRIBUTION.md`
     - `SKILLS.md`
     - `.github/pull_request_template.md`
     - `.github/ISSUE_TEMPLATE/improvement.yml`
     - `.cursor-plugin/plugin.json`
     - `gemini-extension.json`

     (marketplace JSON files optional in REQUIRED if you prefer; plugin.json + gemini-extension.json are the hard RR-B-29a pair with Claude already covered.)

  6. Preserve `::error::` + `FAILED: N issue(s).` / `Release gate: OK` output style already used by CI.

  7. Do **not** remove the Source-Commit ancestor check (P6).

### 1.4 Community / feedback surfaces (RR-B-12 OSS, RR-B-32, README Support)

- [ ] **Create `.github/pull_request_template.md`** from the standard OSS scaffold, filled for this repo:

```markdown
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
```

- [ ] **Create `.github/ISSUE_TEMPLATE/improvement.yml`** from the standard template (name Improvement, labels `[improvement]`, fields: version, skill/component, outcome blocked, proposed change, hygiene checkbox `required: true`). Productize labels to this repo; keep hygiene required.

- [ ] **README Support** section: name three channels distinctly. Target shape:

```markdown
## Support

- **Bugs:** use the [Bug report](https://github.com/jgsystemsconsulting/jgs-reference-skill/issues/new?template=bug_report.yml) form.
- **Improvements / product gaps:** use the [Improvement](https://github.com/jgsystemsconsulting/jgs-reference-skill/issues/new?template=improvement.yml) form.
- **Security issues:** do **not** open a public issue. Report privately via a
  [GitHub security advisory](https://github.com/jgsystemsconsulting/jgs-reference-skill/security/advisories/new);
  see [SECURITY.md](SECURITY.md).
- **Contributing:** see [CONTRIBUTING.md](CONTRIBUTING.md).
```

- [ ] **CONTRIBUTING.md:** add a short **Commit identity** subsection stating new commits must use `245595077+jgsystemsconsulting@users.noreply.github.com` (RR-B-27 forward policy). Optionally point bug vs improvement forms at the new templates. Do not rewrite tone beyond what de-slop needs.

### 1.5 Host manifests + skills index (RR-B-29a / RR-S-08 / RR-S-04)

Product strings (reuse Claude plugin description where possible):

| Field | Value |
|---|---|
| name | `jgs-reference-skill` |
| version | `0.2.1` |
| description | REUSE the README one-liner verbatim (the `Turn a vetted authoritative source ... loads on demand.` sentence; copy it exactly, do not compress into a third phrasing) |
| author / org | `JG Systems Consulting Ltd` (or `JG Systems Consulting Ltd.` to match existing plugin.json) |
| homepage | `https://jgsystemsconsulting.github.io/jgs-reference-skill/` |
| repository | `https://github.com/jgsystemsconsulting/jgs-reference-skill` |
| license | `MIT` |

- [ ] **Create `.cursor-plugin/plugin.json`:**

```json
{
  "name": "jgs-reference-skill",
  "description": "Turn a vetted authoritative source (a standard, handbook, guidebook, or framework) into a licence-clean, citable knowledge pack your agent loads on demand.",
  "version": "0.2.1",
  "author": "JG Systems Consulting Ltd",
  "homepage": "https://jgsystemsconsulting.github.io/jgs-reference-skill/",
  "repository": "https://github.com/jgsystemsconsulting/jgs-reference-skill",
  "license": "MIT"
}
```

- [ ] **Create `.cursor-plugin/marketplace.json`** (repo exposing one plugin):

```json
{
  "name": "jgs-reference-skill",
  "owner": {"name": "JG Systems Consulting Ltd"},
  "metadata": {
    "description": "Turn a vetted authoritative source (a standard, handbook, guidebook, or framework) into a licence-clean, citable knowledge pack your agent loads on demand."
  },
  "plugins": [
    {
      "name": "jgs-reference-skill",
      "source": ".",
      "description": "Turn a vetted authoritative source (a standard, handbook, guidebook, or framework) into a licence-clean, citable knowledge pack your agent loads on demand."
    }
  ]
}
```

- [ ] **Create root `gemini-extension.json`:**

```json
{
  "name": "jgs-reference-skill",
  "version": "0.2.1",
  "description": "Turn a vetted authoritative source (a standard, handbook, guidebook, or framework) into a licence-clean, citable knowledge pack your agent loads on demand."
}
```

- [ ] **Create `.agents/plugins/marketplace.json`** (Codex-oriented native marketplace file; path per standard):

```json
{
  "plugins": [
    {
      "name": "jgs-reference-skill",
      "source": {"path": "./"},
      "interface": {"displayName": "jgs-reference-skill"},
      "description": "Turn a vetted authoritative source (a standard, handbook, guidebook, or framework) into a licence-clean, citable knowledge pack your agent loads on demand."
    }
  ]
}
```

Do not claim directory submission done. Manifests satisfy RR-B-29a only.

- [ ] **Create root `SKILLS.md`** with one entry derived from root `SKILL.md` frontmatter. Exact minimal shape:

```markdown
<!-- Copyright (c) 2026 JG Systems Consulting Ltd. MIT License (see LICENSE). SPDX-License-Identifier: MIT -->

# Skills

| Name | Description |
|------|-------------|
| jgs-reference-skill | Converts an authoritative reference document (standard, handbook, guidebook, framework: PDF/EPUB/DOCX/HTML/MD/RTF) into a licence-clean, citable knowledge pack: a progressive-disclosure agent skill with SKILL.md + chapters + glossary + patterns + cheatsheet, plus PACK.yaml provenance and a per-pack LICENSE. Use when you want a trustworthy reference oracle over a vetted open source (not study notes). Vets the source's licence FIRST and refuses to package non-redistributable (paywalled/all-rights-reserved) sources, routing them to a citation-only signpost instead. |
```

Description text may be shortened to one sentence if the table cell is unwieldy, but the **name** must be exactly `jgs-reference-skill` and entry count must be 1. Prefer generating from frontmatter rather than inventing a second description.

- [ ] Prefer thin SKILLS.md over a check_release exemption. Do not add a single-skill exemption path unless SKILLS.md is rejected for a documented reason (then encode exemption in check_release + README and stop that sub-item only after recording it).

### 1.6 Landing micro-align + Codex honesty (RR-B-20 / RR-B-30 / RR-S-15)

- [ ] **`docs/index.html`:** keep section body and copy. Add org `#usage` compatibility **without redesign**. Preferred minimal fix (dual identity):

  - Change `<section id="use">` to `<section id="use">` remaining as-is **and** add a sibling anchor, **or** set `id="usage"` and keep a named anchor `id="use"` via:

    ```html
    <section id="usage"><div class="wrap">
      <span id="use"></span>
    ```

    Better single-attribute approach allowed by HTML: one id only. Spec allows `id="usage"` **or** dual. Cleanest minimal nav fix:

    1. Change nav link `href="#use"` to `href="#usage"` and label may stay `Use it`.
    2. Change `<section id="use">` to `<section id="usage">`.

  Either dual-id pattern or rename-both is fine. Do not restyle. Confirm favicon link tags remain (already present).

- [ ] **`docs/other-agents.md`:** state that the Codex install target `~/.codex/prompts/jgs-reference-skill.md` is the **deliberate supported alternative** today; native `~/.agents/skills/...` folder install is a possible follow-up, not required to block P9. One short paragraph under the Codex row or in the transform-agents section. Do not change `install.py` behaviour in this package.

- [ ] **RR-B-21 About metadata:** do **not** push. In `docs/DISTRIBUTION.md` record exact maintainer commands, for example:

  ```bash
  gh repo edit jgsystemsconsulting/jgs-reference-skill \
    --description "Convert vetted authoritative sources into licence-clean, citable knowledge packs. Licence-vet gate, provenance, verbatim-overlap detection."
  # add topics if missing (idempotent where gh supports):
  gh repo edit jgsystemsconsulting/jgs-reference-skill --add-topic cursor
  ```

  Strip any em dash from the live About string when the maintainer runs this; the About description reuses the same README one-liner (host: github.com/jgsystemsconsulting/jgs-reference-skill; pages host: jgsystemsconsulting.github.io/jgs-reference-skill). Manifests and About all carry the identical one-liner: one positioning sentence everywhere. Optional only inside the package: add `scripts/configure_repo.sh` wrapping those commands; default is DISTRIBUTION prose only (ponytail).

- [ ] **RR-B-22 GitHub Release:** do **not** run `gh release create`. Draft notes belong in DISTRIBUTION publish-time handoff (CHANGELOG 0.2.1 body + licence-enquiry URL `https://labs.jgsystemsconsulting.com/licensing.html`).

- [ ] **RR-B-03 / RR-B-14 / RR-B-33 / RR-B-34:** no mass header rewrite. Spot-check only; fix a tracked customer-facing hit if the tree scan finds a machine-local profile path or a BOM on a parser-critical file. Do not expand scope.

### 1.7 CHANGELOG Unreleased (RR-B-08 vehicle + RR-S-12 deviation)

- [ ] Insert **above** `## 0.2.1 - 2026-09-24`:

```markdown
## [Unreleased]

Release-standard hygiene after the 0.2.1 cut (P9). No product version bump.

### Added
- `docs/DISTRIBUTION.md` channel ledger (last reviewed 0.2.1 / 2026-09-24).
- Root `SKILLS.md` (single skill index).
- Host manifests: `.cursor-plugin/`, root `gemini-extension.json`, `.agents/plugins/marketplace.json`.
- `.github/pull_request_template.md` and `.github/ISSUE_TEMPLATE/improvement.yml`.

### Fixed
- Version drift: `CITATION.cff`, README badge, and agent-install prompt now agree at 0.2.1 with RELEASE-INFO / pyproject / plugin / landing.
- `SECURITY.md` supported-versions table tracks the 0.2.x line.
- `scripts/check_release.py`: explicit forbidden-paths class, RR-B-37 escape guard (never-track, gitignore rules, frozen `docs/superpowers/` baseline), version agreement for CITATION/README.
- Landing `#usage` anchor compatibility; README Support names bug vs improvement vs security channels.
- Codex install path documented as the deliberate prompts-path alternative.

### Notes
- **RR-S-12 deviation (dated 2026-09-24):** the standard CI verify line says no step executes checked-out repository code. Since P1, the `tests` job deliberately runs pytest, tools `--self-check`, and `py_compile` under `pull_request` semantics with `permissions: read-all` and no secrets. The read-only `integrity` job is unchanged. Fork PRs gain no write access. Revisit only if GitHub changes pull_request token semantics.
- P1-P8 product work is already on the tree around the 0.2.1 cut; this Unreleased section records post-tag standard hygiene only. Publish-time remains open: GitHub Release object for `v0.2.1` (tag exists), optional About/topic polish, directory submissions (see `docs/DISTRIBUTION.md`).
```

Do **not** open `## 0.2.2`. Do not edit RELEASE-INFO.

### 1.8 Task 1 self-check (before Task 2)

- [ ] `python scripts/check_release.py` exits 0 with freeze baseline filled.
- [ ] `git check-ignore -v packs/demo-contract 2>/dev/null || git check-ignore -v packs/` shows packs ignored.
- [ ] `test -f SKILLS.md && test -f docs/DISTRIBUTION.md && test -f .cursor-plugin/plugin.json && test -f gemini-extension.json`
- [ ] Quick version probe:

```bash
python - <<'PY'
import re, pathlib
root = pathlib.Path('.')
assert '0.2.1' in (root/'CITATION.cff').read_text(encoding='utf-8')
readme = (root/'README.md').read_text(encoding='utf-8')
assert 'version-0.2.1-informational' in readme
assert 'v0.2.1' in readme
print('version surfaces OK')
PY
```

---

## Task 2: De-slop pass + final verification

**Files:** every human-facing path Task 1 created or modified (README, CHANGELOG, SECURITY, CONTRIBUTING, CITATION.cff, DISTRIBUTION.md, SKILLS.md, docs/other-agents.md, docs/index.html customer copy if touched, GitHub templates). Do not bulk-edit `docs/superpowers/**` for em dashes (freeze + customer-surface-only verify per RR-B-28 / RR-B-35).

### 2.1 Recorded Technical-Writer de-slop (RR-B-28, Success criterion 9)

- [ ] Apply Written Prose Standard to touched customer docs:
  - Zero em dashes (`—`) and zero spaced `--` used as dash in prose.
  - No Tier-1 slop constructions ("it's not X, it's Y", hedge stacks, "robust/seamless/leverage" filler).
  - Staff-engineer voice; short sentences fine.
- [ ] Run customer-surface em-dash grep; must be empty:

```bash
rg -n "—" README.md CHANGELOG.md SECURITY.md CONTRIBUTING.md CITATION.cff \
  SKILLS.md docs/DISTRIBUTION.md docs/*.md docs/*.html \
  .github/pull_request_template.md .github/ISSUE_TEMPLATE/*.yml \
  --glob '!docs/superpowers/**'
```

- [ ] Optional: `python ~/.zcode/scripts/prose_check.py` on the same file list if the script exists; fix or justify residuals.
- [ ] Record in the package verification notes (EXECUTED or commit message body): "P9 de-slop pass completed on touched customer docs; customer em-dash grep clean; superpowers process tree excluded per RR-B-35 freeze."

### 2.2 Landing taste + link integrity (RR-B-24 / RR-B-25)

- [ ] Run landing taste from the standard skill tool **without vendoring** into this repo:

```bash
python "$HOME/.zcode/skills/release-repo-standard/tools/landing_taste.py" \
  docs/index.html docs/site.css
```

Expect `PASS` / no hits. Fix only mechanical fails the tool reports. Do not restyle for subjective taste. If the tool is missing on disk: note BLOCKED-soft, take desktop+mobile screenshots under `.playwright-mcp/` when Playwright MCP is available (gitignored), and still fix any obvious broken chrome. Do not commit screenshots.

- [ ] Link check over README + customer docs (zero broken local targets). Minimal stdlib checker acceptable:

```bash
python - <<'PY'
import pathlib, re, sys
root = pathlib.Path('.')
targets = [root/'README.md', *root.glob('docs/*.md'), *root.glob('docs/*.html')]
# skip superpowers
targets = [p for p in targets if 'superpowers' not in p.parts]
md_link = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
html_href = re.compile(r'href=["\']([^"\']+)["\']', re.I)
broken = []
for p in targets:
    text = p.read_text(encoding='utf-8', errors='ignore')
    urls = md_link.findall(text) if p.suffix == '.md' else []
    hrefs = [u for _, u in urls] if p.suffix == '.md' else html_href.findall(text)
    if p.suffix == '.md':
        hrefs = [u for _, u in md_link.findall(text)]
    for href in hrefs:
        if href.startswith(('http://','https://','mailto:','#')):
            continue
        path = href.split('#',1)[0].split('?',1)[0]
        if not path:
            continue
        cand = (p.parent / path).resolve()
        try:
            cand.relative_to(root.resolve())
        except ValueError:
            continue
        if not cand.exists():
            broken.append(f'{p}: {href}')
if broken:
    print('BROKEN'); print('\n'.join(broken)); sys.exit(1)
print(f'OK: link check clean on {len(targets)} files')
PY
```

Fix breaks in-repo. External http(s) links are not fetched in this package (record "local targets only").

### 2.3 Final gate battery (Success criteria 2-5, 9-13)

Run from repo root:

```bash
# 1. Release gate
python scripts/check_release.py

# 2. Pytest (record full summary line)
python -m pytest -q 2>&1 | tail -30

# 3. Five-tool self-check (scan_generated_skill has no --self-check; not in this loop)
for t in vet_source check_overlap outline validate_pack pack_eval; do
  python tools/$t.py --self-check || echo "SELF-CHECK-FAIL $t"
done

# 4. Compile smoke (CI-equivalent)
python -m py_compile tools/*.py scripts/extract.py scripts/check_release.py

# 5. Stale version grep (live surfaces; CHANGELOG historical 0.2.0 section allowed)
rg -n "0\.2\.0" README.md CITATION.cff SECURITY.md RELEASE-INFO.txt \
  pyproject.toml docs/index.html SKILL.md SKILLS.md \
  .claude-plugin/plugin.json .cursor-plugin/plugin.json gemini-extension.json \
  docs/skill-usage.md docs/other-agents.md || true

# 6. Three-gates wording must not reappear outside declared historical drift
rg -n "three gates|three-gate|3 gates" README.md SKILL.md docs/skill-usage.md \
  docs/index.html docs/other-agents.md CONTRIBUTING.md || true

# 7. Four-gates truth still present where product docs state verify
rg -n "four gates|four verification gates|check_overlap|scan_generated_skill" \
  README.md SKILL.md docs/skill-usage.md docs/index.html | head -20

# 8. Customer em-dash grep (repeat)
rg -n "—" README.md CHANGELOG.md SECURITY.md CONTRIBUTING.md \
  docs/DISTRIBUTION.md docs/*.md docs/*.html SKILLS.md \
  --glob '!docs/superpowers/**' || true

# 9. BOM spot-check on parser-critical files
python - <<'PY'
from pathlib import Path
files = ['CITATION.cff','RELEASE-INFO.txt','pyproject.toml',
         '.claude-plugin/plugin.json','.cursor-plugin/plugin.json',
         'gemini-extension.json','docs/index.html']
bad=[]
for f in files:
    p=Path(f)
    if not p.is_file():
        continue
    b=p.read_bytes()
    if b.startswith(b'\xef\xbb\xbf'):
        bad.append(f)
print('BOM_CLEAN' if not bad else bad)
PY
```

**Pass bar:**

| Check | Pass |
|---|---|
| check_release.py | exit 0, prints OK |
| pytest | green; prefer **543 passed, 5 skipped** when that is the suite size; accept equal-or-better; Windows symlink carve-out only |
| five-tool self-check | all five exit 0 |
| compile | exit 0 |
| stale 0.2.0 on live surfaces | none (CHANGELOG historical section exempt) |
| three-gates wording | none on customer product docs |
| four-gates / scan gate truth | still present |
| customer em dash | none |
| BOM | none on listed files |
| FROZEN_TREES | matches current `git ls-files docs/superpowers` after final add |

### 2.4 Acceptance checklist (mirrors spec Success criteria)

Mark each only when evidence exists in the tree or verification output:

- [ ] **SC1** Audit table in-repo MUST gaps closed, or SHOULD/MAY deferred with dated rows in `docs/DISTRIBUTION.md`.
- [ ] **SC2** Version agreement at **0.2.1**: RELEASE-INFO, CHANGELOG top released entry, pyproject, plugin.json, CITATION.cff, README badge, README agent-install prompt, landing REV + JSON-LD `softwareVersion`, new host manifest versions.
- [ ] **SC3** `docs/DISTRIBUTION.md` tracked; last-reviewed 0.2.1 / 2026-09-24; applicable channels listed.
- [ ] **SC4** `python scripts/check_release.py` exit 0; enforces forbidden-paths + RR-B-37 decisions.
- [ ] **SC5** Local CI-equivalent green: integrity-class checks, pytest, tools self-check, compile.
- [ ] **SC6** `.github/pull_request_template.md` present; improvement issue form present.
- [ ] **SC7** Host manifests: Claude (pre-existing) + Cursor + Gemini at 0.2.1; Codex `.agents/plugins/marketplace.json` present.
- [ ] **SC8** Root `SKILLS.md` lists the one skill.
- [ ] **SC9** Customer-facing em-dash grep clean (README, CHANGELOG, docs/*.md, docs/*.html, new ledger).
- [ ] **SC10** SECURITY supported-versions reflects 0.2.x.
- [ ] **SC11** README Support names bug vs improvement vs security.
- [ ] **SC12** CHANGELOG has `## [Unreleased]` for P9 hygiene + RR-S-12 deviation note; no `## 0.2.2`.
- [ ] **SC13** Docs stay truthful on four verify gates, installer behaviour, Codex prompts path.
- [ ] **SC14** Package notes / DISTRIBUTION list remaining publish-time MUSTs (Release v0.2.1 body + licence-enquiry URL; optional About polish).
- [ ] **SC15** No push, no new version tag, no P7 work, no P1-P8 redesign.

### 2.5 Standard §5 checklist end-state (quick)

After Task 2, the §5 roll-up in the spec should read as:

| # | End-state |
|---|---|
| 1 Release gate | met |
| 2-3 RR-B / RR-S MUSTs in-repo | met (publish-time called out) |
| 5 Version agreement | met |
| 6 Agent-install prompt | met |
| 7 Tagged release | met (git); Release object still publish-time |
| 8 Catalogue | recorded in ledger |
| 9 Multi-agent install | met + Codex honesty |
| 10 Landing + Pages | met + `#usage` |
| 11 About metadata | in-repo handoff recorded |
| 12 Marketplace manifests | Claude+Cursor+Gemini (+Codex file) |
| 13 GitHub Release v0.2.1 | still publish-time (not claimed done) |
| 14 Branch protection | met (unchanged) |
| 15-18 Taste / links / mermaid / de-slop | verified this package |
| 19 Commit identity | forward policy recorded |
| 19a Multi-page | one-page assessed OK (note in DISTRIBUTION or EXECUTED) |
| 23 CITATION.cff | met 0.2.1 |
| 24 Bug + improvement channels | met |
| 25 BOM | met |
| 27-28 Keep-drop + escape | met |
| 29 RR-S-17 | deferred in ledger |
| 30 DISTRIBUTION.md | met |
| 31 Favicon | met (pre-existing) |
| 32 Escape guard | met |

### 2.6 Commit guidance (when the executor commits)

Prefer a small stack over one megacommit if SDD task reviews need isolation, for example:

1. `fix(release): align CITATION/README/SECURITY to 0.2.1`
2. `feat(release): DISTRIBUTION ledger, keep/drop, check_release escape guard`
3. `feat(release): PR template, improvement form, host manifests, SKILLS.md`
4. `docs(release): Unreleased hygiene + RR-S-12 deviation; de-slop`

Or one commit if the controller asks for a single package commit. Message body must mention RR-S-12 deviation and "no 0.2.2 bump". Author email should be the JGSC noreply, set repo-locally via `git config user.email` in the task steps before any commit (RR-B-27 MUST, no hedge).

Do not `git push`. Do not `gh release create`. Do not retag.

---

## Out of scope (hard)

- Cutting or publishing `v0.2.2` / moving RELEASE-INFO off 0.2.1
- `gh release create` for v0.2.1 (handoff only)
- History rewrite (RR-B-27)
- Marketplace / awesome-list web form submissions (RR-B-29b)
- P7 motion pack; P1-P8 redesign; install.py Codex native path rewrite
- Vendoring `landing_taste.py` into this repo
- De-slop of entire `docs/superpowers/**` tree

## Risks / concerns

- **Frozen tree churn:** any later commit under `docs/superpowers/` without updating `FROZEN_TREES` fails the gate by design. That is intended.
- **validate.yml Unreleased:** changelog_top regex must continue to skip `[Unreleased]` and read `0.2.1`; cover this in the version-step edit and with a quick mental check of the regex against both headings.
- **Windows pytest symlink carve-out:** do not "fix" security tests by weakening them; note environment limitation only.
- **About/topics/Release:** easy to over-claim; DISTRIBUTION must keep status honest (`planned` / publish-time), never `submitted` or "Release exists" until a human does it.
