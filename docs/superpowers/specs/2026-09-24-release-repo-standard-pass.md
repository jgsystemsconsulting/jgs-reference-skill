# Spec: P9 release-repo-standard-pass

**Date:** 2026-09-24  
**Repo:** jgs-reference-skill  
**Standard:** release-repo-standard v1.16 (user-scope skill)  
**Profile:** Base (`RR-B`) + Skills pack (`RR-S`)  
**Licence posture:** Open-source (MIT)  
**Build model:** Standalone  
**Version under audit:** 0.2.1 (tag `v0.2.1` exists locally and on origin; CHANGELOG top entry is 0.2.1)

## Problem

The last dedicated release-standard pass landed at `7110cd2` (v0.2.0-era). Today’s P1–P8 work plus a sibling-session 0.2.1 cut changed CI, tools, installer containment, RELEASE-INFO provenance, landing chrome, and docs. The tree must be re-audited against every applicable `RR-B` / `RR-S` item and the §5 checklist, then brought back to the standard without reopening P1–P8 product decisions.

This package is an audit-and-close pass, not a feature package. Publishing and pushing stay out of scope; the implementer leaves the working tree green against local gates and records platform-state work that only a human or a later publish step can finish.

## Research

research: skipped (internal audit against a locally-readable standard; no external APIs)

Audit method: read `~/.zcode/skills/release-repo-standard/SKILL.md` and `references/release-repo-standard.md`, walk the live tree, run `python scripts/check_release.py` (exit 0), and sample platform state with `gh` where available.

## Context (what changed today)

| Package | Effect on release surface |
|---|---|
| P1 | CI runs pytest + tools `--self-check` + compile; integrity job still owns leak/frontmatter/version/release-gate |
| P2 / P3 | Tool hardening (`vet_source`, scaffold/provenance) |
| P4 | Four verify gates in product docs and landing copy |
| P5 | Installer containment and multi-agent docs |
| P6 | RELEASE-INFO Source-Commit ancestor guard in `scripts/check_release.py` |
| P8 | Landing aligned to JGSC shell; shared `docs/site.css`; REV 0.2.1; favicons |
| Sibling 0.2.1 | Version already cut earlier today; tag `v0.2.1` on origin |

P7 (motion pack) is a separate repo and stays out of scope.

### CITATION.cff author note

During the RR-B-31 version edit, normalize the author list to the organization entry (JG Systems Consulting Ltd) per the standard's author convention; keep virgiliojr94 only where GitHub attribution requires it.

### Recorded deviation (RR-S-12, dated 2026-09-24)

The standard's CI verify line says no step executes checked-out repository code. Since P1, the `tests` job deliberately executes repo code (pytest, tools self-checks, py_compile) under `pull_request` semantics with `permissions: read-all` and no secrets. This is a recorded, dated deviation: the read-only integrity job still exists unchanged, fork PRs gain no write access, and the deviation is noted in the CHANGELOG Unreleased entry this package writes. Revisit only if GitHub changes pull_request token semantics.

## Goals (a recorded Technical-Writer de-slop pass over every human-facing doc this package touches is part of the closure bar: zero em dashes, no Tier-1 slop, per RR-B-28; the pass is recorded in the plan's verification notes)

1. Close every **MUST** gap found below that is fixable in-repo without a design change.
2. Record **SHOULD** gaps with a deliberate keep, fix, or N/A decision dated in-tree (ledger or release notes of this package).
3. Re-run `python scripts/check_release.py` and the CI-relevant local gates green (integrity-equivalent checks, pytest, tools self-check, compile as CI defines them).
4. Leave docs and version-bearing surfaces truthful for 0.2.1 (or for the Unreleased / next-patch vehicle chosen below).
5. Leave the tree at the JGSC release standard for a skills pack under the open-source posture, modulo platform actions explicitly deferred as publish-time.

## Constraints

- **No version bump unless the standard requires one for post-0.2.1 tree drift.** Decision: **do not cut 0.2.2 in this package.** 0.2.1 already shipped today. Post-tag hygiene fixes (version-string drift, missing ledger, gate hardening, docs truth) land under a new `## [Unreleased]` CHANGELOG section that becomes 0.2.2 only when a later release is deliberately cut. Rationale: RR-B-08/09 demand agreement and honesty, not a new tag for every audit fix; cutting another patch the same day without a product change confuses provenance. If an implementer finds a change that *must* ship as a new published Release to satisfy RR-B-22 on origin, stop and treat that as a publish step outside this package rather than silently bumping.
- **No publishing / pushing** in this package (no `gh release create`, no force-push, no Pages reconfigure beyond documenting current state).
- Written Prose Standard on durable docs this package touches: no em dash in customer-facing prose; staff-engineer voice.
- Do not reopen P1–P8 design choices; only close standard gaps those packages left or created.
- Prefer minimum diffs: fix drift and missing artifacts; do not redesign the landing page or installer.

## Out of scope

- P7 motion pack (separate repo).
- Re-opening P1–P8 decisions or re-litigating their ARL/IVL outcomes.
- New product features, new skills, new hosts beyond what RR-S already requires for manifests already targeted.
- Full history rewrite for RR-B-27 (vendored upstream authors and personal emails in inherited history). Record the gap; do not filter-repo in this package unless the controller explicitly expands scope.
- Submitting marketplace / directory web forms (RR-B-29b human-only).
- Cutting and publishing GitHub Release `v0.2.1` notes (publish-time; see gap RR-B-22).

## Profile and applicability

| Axis | Value |
|---|---|
| Product type | Skills pack (root `SKILL.md` single-skill-as-repo) + pack-builder tooling |
| Profile | Base + `RR-S` |
| RR-M | N/A (not an MCP bridge) |
| RR-R | N/A (not a research instrument) |
| Licence | MIT OSS; `CONTRIBUTING` + `CODE_OF_CONDUCT` are MUST under RR-B-12 flip |
| Generator model | N/A; standalone (RR-B-00 satisfied by construction) |

---

## Audit result table

Status values: **met** | **gap** | **n/a**.  
Severity: **MUST** blocks release-ready; **SHOULD** needs a dated decision; **MAY** optional.

### Base legal and identity

| ID | Sev | Status | Evidence / gap | Closing action |
|---|---|---|---|---|
| RR-B-00 | MUST | n/a | Standalone repo | None |
| RR-B-01 | MUST | met | Root `LICENSE` is canonical MIT; org + 2026 | None |
| RR-B-02 | MUST | met | `COPYRIGHT`, `NOTICE`, `ATTRIBUTION.md` name JGSC + upstream | None |
| RR-B-03 | MUST | gap (narrow) | First-party shippable files largely headed; root `SKILL.md` body header is HTML-comment copyright after frontmatter, acceptable pattern, but gate only checks tracked `.py` | Extend header sweep only if audit.py/manual fails; optional: ensure SKILL.md comment block stays SPDX-true. No mass rewrite. |
| RR-B-04 | MUST | met | SPDX MIT on first-party sources sampled | None |
| RR-B-05 | MUST | gap | README has Install, Usage, Licence (with licence-enquiry URL), Support. **Version badge and agent-install prompt still say 0.2.0** | Update badge + agent-install embedded version to **0.2.1**; keep licence-enquiry link |
| RR-B-06 | MUST | met | Install + usage paths in README and `docs/skill-usage.md` | None |
| RR-B-07 | MUST | met | `SECURITY.md` advisory route; no email | None (see RR-S-10 note on supported-versions table) |
| RR-B-16 | SHOULD | gap | Agent-install block present; **embeds v0.2.0** | Same fix as RR-B-05: bump embedded version to 0.2.1 |
| RR-B-17 | MAY | n/a | No `llms.txt` / root `AGENTS.md` required | None |

### Versioning

| ID | Sev | Status | Evidence / gap | Closing action |
|---|---|---|---|---|
| RR-B-08 | MUST | met (top entry) / watch | CHANGELOG top is `## 0.2.1 - 2026-09-24` | Add `## [Unreleased]` for P9 hygiene fixes; do not invent 0.2.2 entry until a real bump |
| RR-B-09 | MUST | gap | Agree: `RELEASE-INFO.txt`, `pyproject.toml`, `.claude-plugin/plugin.json`, landing REV/JSON-LD, CHANGELOG top = **0.2.1**. Drift: **`CITATION.cff` = 0.2.0**, **README badge = 0.2.0**, **README agent prompt = 0.2.0**. CI version step does not check CITATION/README | Set CITATION.cff `version` (+ `date-released` if needed) to 0.2.1; fix README strings; extend CI version-consistency (or check_release) to include CITATION.cff and README badge/prompt version |
| RR-B-10 | MUST | met | RELEASE-INFO has product, version, UTC, Tag, real Source-Commit; P6 gate enforces ancestor | None |

### Structure and hygiene

| ID | Sev | Status | Evidence / gap | Closing action |
|---|---|---|---|---|
| RR-B-11 | MUST | gap (soft) | Layout mostly clean; untracked `packs/` at root; `__pycache__` may exist on disk; tracked `docs/superpowers/` is large process tree | Confirm `packs/` gitignored or removed from publish intent; keep/drop decision under RR-B-35. Do not commit local pack outputs |
| RR-B-12 | MUST (OSS flip) | gap (narrow) | `CONTRIBUTING.md` + `CODE_OF_CONDUCT.md` present. **No** `.github/pull_request_template.md` | Add OSS PR template from standard scaffold (one concern, type checklist, guardrails, no-secrets, rights grant, real test commands: pytest, tools self-check, `scripts/check_release.py`) |
| RR-B-13 | MUST | met | Root `.gitignore` present; ignores `.zcode/`, `.superpowers/`, work products | Optionally add `packs/` if pack outputs are local-only |

### Security and gate

| ID | Sev | Status | Evidence / gap | Closing action |
|---|---|---|---|---|
| RR-B-14 | MUST | met | Leak scan posture in CI; check_release forbidden-content | Spot-check remains green |
| RR-B-15 | MUST | gap | `scripts/check_release.py` has required-files, forbidden-content, headers-on-py, Source-Commit. **Missing explicit forbidden-paths class** and **RR-B-37 escape guard** (session-state prefixes, frozen-tree baseline, gitignore-rule presence) | Extend check_release: (1) forbidden path prefixes if any; (2) fail if tracked files under `.zcode/` or `.superpowers/`; (3) if docs/superpowers is kept frozen, pin sorted `git ls-files docs/superpowers` hash baseline; (4) assert `.gitignore` still contains decided rules for `.zcode/` and `.superpowers/` | (a forbidden-paths class must exist explicitly, even if currently empty)
| RR-B-33 | MUST | met | BOM scan on parser-critical files clean at audit time | Keep in gate or CI if cheap |
| RR-B-34 | MUST | met (customer surface) | No machine-local profile paths in customer-facing tracked text at audit sampling; install dry-run prints local paths only at runtime | Re-run tree scan excluding exempt binaries; fix any hit in tracked text |

### Distribution and discoverability

| ID | Sev | Status | Evidence / gap | Closing action |
|---|---|---|---|---|
| RR-B-18 | MUST | met (git) | Tag `v0.2.1` local + origin; RELEASE-INFO `Tag: v0.2.1` | None in-repo |
| RR-B-19 | SHOULD | gap | No org catalogue entry recorded | Record deliberate N/A or planned row in `docs/DISTRIBUTION.md` with date |
| RR-B-20 | MUST | gap (narrow) | `docs/index.html` + `.nojekyll`; self-contained site.css + fonts; favicons present; Pages **built** from `main` `/docs`; licence-enquiry in footer. Usage section id is `#use` not `#usage` (org SHOULD vocabulary). Nav lacks explicit `#usage` label | Prefer minimal: add `id="usage"` (or dual id) on the use section and/or nav anchor `#usage` to match org site pattern without redesign. Confirm every shipped HTML has icon links (only `index.html` ships) |
| RR-B-21 | MUST | gap (narrow) | About description + homepage set; ≥6 topics including hosts. **Description contains an em dash** (platform About string). Topics use `codex` not `openai-codex`; no explicit `cursor` topic | Edit About description via documented configure step (or note for maintainer): remove em dash; align host topic names to standard list where cheap (`cursor`, keep existing host tags). **No push in this package** if edit requires remote; prepare `scripts/configure_repo.sh` or document exact `gh repo edit` commands in Unreleased notes for maintainer |
| RR-B-22 | MUST | gap | Tag exists; **no GitHub Release for v0.2.1** (`gh release list` shows only v0.1.0). Notes would need licence-enquiry URL | **Out of package publish step:** draft release notes from CHANGELOG 0.2.1 + licence footer template; maintainer runs `gh release create`. Spec records this as remaining MUST for “published release-ready,” not as an in-branch silent claim of done |
| RR-B-23 | SHOULD | met | `main` protection: PR required, `integrity` check, force-push/delete off, enforce_admins false | Optionally add `tests` job to required checks (SHOULD strengthen); not blocking if integrity alone was the prior contract |
| RR-B-24 | SHOULD/MUST-new | gap (process) | Landing redesigned in P8; mechanical taste/Playwright evidence not re-verified in this audit | Run `landing_taste` equivalent if tool available; Playwright desktop+mobile screenshots under `.playwright-mcp/` (gitignored); fix only mechanical fails. Do not restyle for taste alone |
| RR-B-25 | MUST | gap (verify) | Not re-run end-to-end in this audit | Run link check over README + docs/** after edits; fix breaks; record pass in package EXECUTED notes |
| RR-B-26 | SHOULD | gap (soft) | Docs use tables; multi-step pipeline may still be prose/ASCII rather than mermaid | Add one mermaid pipeline diagram to README or skill-usage only if cheap; else dated SHOULD defer in DISTRIBUTION or Unreleased |
| RR-B-27 | MUST | gap (historical) | `git log --all` includes many non-canonical emails (upstream book-to-skill + personal). Canonical JGSC noreply also present | **Do not rewrite history in P9.** Document deliberate exception: inherited upstream history retained; new commits MUST use `245595077+jgsystemsconsulting@users.noreply.github.com`. Record in DISTRIBUTION or CONTRIBUTING |
| RR-B-28 | MUST | gap (narrow) | Customer README/docs/CHANGELOG/landing: no em dash at audit. `docs/superpowers/**` review files still contain em dashes (process tree) | If superpowers stays tracked, either de-slop those files or accept as maintainer-only and exclude from customer grep; prefer RR-B-35 freeze + customer-surface-only verify |
| RR-B-29a | MUST | gap | Claude: `.claude-plugin/marketplace.json` + `plugin.json` (version 0.2.1) present. **No** `.cursor-plugin/`, **no** `gemini-extension.json`, **no** `.agents/plugins/marketplace.json`. Codex baseline via legacy Claude marketplace may count; Cursor/Gemini manifests missing for hosts install.py advertises | Ship minimal manifests for hosts the product targets via install.py: at least `.cursor-plugin/plugin.json` (+ marketplace if required), `gemini-extension.json`, and optionally `.agents/plugins/marketplace.json`. Versions from 0.2.1. README already documents per-host install |
| RR-B-29b | SHOULD | gap | No submission ledger | Capture per-host submitted/deferred/N-A in `docs/DISTRIBUTION.md` (agent must not mark submitted) |
| RR-B-30 | MUST assess | met / soft | Single landing page + shared css; multi-page not required. Assessment: one hub page is enough for this product | Record one-page assessed outcome in P9 EXECUTED notes. Optional: rename `#use` → `#usage` for org pattern |
| RR-B-31 | MUST | gap | `CITATION.cff` exists, CFF 1.2.0, org author, MIT; **version 0.2.0** and date-released 2026-09-23 | Bump version to 0.2.1; set date-released to 2026-09-24 (release day) |
| RR-B-32 | MUST | gap | bug_report.yml + config.yml good (blank issues off, advisory link, hygiene required). **No improvement form (SHOULD).** README Support names bugs + security but not improvement channel distinctly | Add `.github/ISSUE_TEMPLATE` improvement/enhancement form (version field, outcome, proposed change, hygiene). Update README Support to name bug form vs improvement form vs security advisory |
| RR-B-35 | MUST assess | gap | Tracked `docs/superpowers/` (~60 files: specs/plans/reviews/packages/backlog). Session dirs `.zcode/`/`.superpowers/` already gitignored. Untracked `packs/` | **Present keep/drop to maintainer (default gitignore).** Recommended: **keep** `docs/superpowers/` as frozen process history for this cut (baseline hash in check_release); **gitignore** `packs/`; confirm `.zcode/`/`.superpowers/` stay ignored. Do not delete disk copies |
| RR-B-36 | MUST | gap | **`docs/DISTRIBUTION.md` missing** | Create ledger covering: GitHub About/topics, Pages, Claude marketplace manifest, Cursor/Gemini/Codex manifests, org catalogue, community awesome-lists, directory submissions. Statuses with dates; last-reviewed 0.2.1 / 2026-09-24 |
| RR-B-37 | MUST where 35 decides | gap | check_release does not enforce escape guard | Implement per RR-B-15 closing action once 35 decisions recorded |

### Skills-pack profile (`RR-S`)

| ID | Sev | Status | Evidence / gap | Closing action |
|---|---|---|---|---|
| RR-S-01 | MUST | met | Root `SKILL.md` with name + description frontmatter (single-skill-as-repo) | None |
| RR-S-02 | MUST | met | `install.py`, `install.sh`, `install.ps1`; dry-run works | None |
| RR-S-03 | MUST | met | Namespaced default under `jgs`; flat documented | None |
| RR-S-04 | MUST | gap / n/a-shape | No root `SKILLS.md`. Single-skill-as-repo: index may be satisfied by root SKILL.md alone under standalone note, but Verify line still asks for SKILLS.md entry count | Add thin root `SKILLS.md` generated from frontmatter (one entry) **or** document single-skill exemption in check_release + README. Prefer thin `SKILLS.md` for mechanical verify |
| RR-S-05 | MUST | met | `docs/skill-usage.md` linked from README and landing | None |
| RR-S-06 | SHOULD | met | Single skill name coherent | None |
| RR-S-07 | MAY | n/a | No companion MCP tool reference required | None |
| RR-S-08 | MUST new-pack | gap | Claude plugin metadata present; Cursor parallel missing (see RR-B-29a) | Same manifest work as RR-B-29a |
| RR-S-09 | MUST new-pack | gap | Badge cluster present; **version badge 0.2.0** | Bump to 0.2.1 |
| RR-S-10 | MUST new-pack | gap (narrow) | SECURITY.md advisory OK; **Supported versions table still shows only 0.1.x** | Update supported table to current 0.2.x line |
| RR-S-11 | MUST | gap | Tag + most artifacts 0.2.1; drift listed under RR-B-09 | Same version-propagation fix list |
| RR-S-12 | MUST | met / watch | `validate.yml`: permissions read-all; push+PR; integrity does not execute random repo code except check_release; tests job runs pytest/tools/compile (P1). Frontmatter lint does not yet enforce When-to-use / prerequisites (RR-S-13) | Optionally tighten frontmatter/body lint; not strictly failing if SKILL.md already complies |
| RR-S-13 | MUST | met | SKILL.md has `## When to use` and `## Prerequisites` | None |
| RR-S-14 | MUST | met | agentskills.io-shaped frontmatter | None |
| RR-S-15 | MUST | gap (narrow) | install.py multi-agent works; docs/other-agents.md present. **Codex target is still `~/.codex/prompts/*.md` transform**, while current standard prefers native `~/.agents/skills/...` SKILL.md folder (prompts path remains allowed alternative) | Prefer doc honesty first: state prompts path as deliberate alternative. Optional follow-up (not required to block): add native codex agents-skills target. Gemini remains transform TOML, not full extension tree; pair with `gemini-extension.json` for RR-B-29a |
| RR-S-16 | MUST if signpost | met posture | Skill documents signpost mode; gates exist in product tools | Ensure CI/file gate still exempt `kind: signpost` packs; no change unless tests fail |
| RR-S-17 | SHOULD | gap | No in-pack feedback utility skill | Dated defer in DISTRIBUTION.md (SHOULD), unless cheap to add a tiny skill; default **defer** to keep P9 minimum |

### Research / MCP

| ID | Sev | Status | Notes |
|---|---|---|---|
| RR-M-* | | n/a | Not an MCP bridge |
| RR-R-* | | n/a | Not a research instrument |

### §5 checklist roll-up (quick)

| # | Item | Result |
|---|---|---|
| 1 | Release gate exit 0 | met now; must stay green after extensions |
| 2–3 | Applicable RR-B / RR-S MUSTs | **fail until gaps closed** |
| 5 | Version agreement | **fail** (CITATION + README) |
| 6 | Agent-install prompt | **fail** (0.2.0) |
| 7 | Tagged release | met (git); Release object missing (#13) |
| 8 | Catalogue | record in ledger |
| 9 | Multi-agent install | met with Codex-path honesty gap |
| 10 | Landing + Pages | met core; pattern id soft gap |
| 11 | About metadata | met with em-dash / topic polish |
| 12 | Marketplace manifests | **partial** (Claude only) |
| 13 | GitHub Release v0.2.1 | **fail** (publish-time) |
| 14 | Branch protection | met |
| 15–18 | Taste / links / mermaid / de-slop | verify after edits |
| 19 | Commit identity | historical fail; policy going forward |
| 19a | Multi-page assessment | one-page OK; record |
| 23 | CITATION.cff version | **fail** |
| 24 | Bug channel | met core; improvement form missing |
| 25 | BOM | met |
| 27–28 | Paths / keep-drop | keep-drop **open** |
| 29 | RR-S-17 feedback skill | defer SHOULD |
| 30 | DISTRIBUTION.md | **fail missing** |
| 31 | Favicon | met |
| 32 | Escape guard | **fail missing** |

---

## Implementation plan (gap closure order)

Work stays in-repo, minimum files, no publish.

1. **Version truth (RR-B-09 / RR-S-11 / RR-B-05 / RR-B-16 / RR-S-09 / RR-B-31)**  
   Align to 0.2.1: `CITATION.cff`, README badge, README agent-install prompt. Confirm landing/plugin/pyproject/RELEASE-INFO/CHANGELOG already 0.2.1. Extend version-consistency check to CITATION + README badge (and prompt version if easy).

2. **Distribution ledger (RR-B-36) + related SHOULD rows**  
   Add `docs/DISTRIBUTION.md` with dated statuses for every applicable channel, including RR-B-19, RR-B-29b, RR-S-17 deferral, RR-B-27 history policy.

3. **Keep/drop + escape guard (RR-B-35 / RR-B-37 / RR-B-15)**  
   Record decision: freeze-keep `docs/superpowers/`; gitignore `packs/` if local outputs; enforce in `scripts/check_release.py`.

4. **Community / feedback surfaces (RR-B-12 OSS, RR-B-32)**  
   PR template; improvement issue form; README Support channel list; SECURITY supported-versions table → 0.2.x.

5. **Host manifests (RR-B-29a / RR-S-08)**  
   Minimal Cursor + Gemini (+ Codex native marketplace file if required) manifests at 0.2.1.

6. **Skills index (RR-S-04)**  
   Add root `SKILLS.md` with the one skill entry.

7. **Landing micro-align (RR-B-20 / RR-B-30 SHOULD)**  
   `#usage` anchor compatibility without redesign.

8. **Verify**  
   `python scripts/check_release.py`  
   CI-equivalent: integrity checks, `pytest -q`, tools `--self-check`, compile  
   Link check customer surface  
   Em-dash grep on README, docs/*.md, docs/*.html, CHANGELOG (exclude or clean superpowers per 35)  
   BOM scan  

9. **CHANGELOG**  
   Under `## [Unreleased]`, list hygiene fixes (version drift, ledger, manifests, gate escape, issue forms). Do **not** open `## 0.2.2` in this package.

10. **Publish-time handoff (not done here)**  
    Maintainer: GitHub Release v0.2.1 with licence-enquiry footer; About description em-dash strip if not applied; optional topic adds; directory submissions.

## Version policy (normative for this package)

| Question | Answer |
|---|---|
| Is 0.2.1 already the release version? | Yes |
| Does P9 require bumping to 0.2.2? | **No**, unless the controller later decides the Unreleased hygiene set deserves its own tag |
| How are post-tag fixes recorded? | `## [Unreleased]` in CHANGELOG |
| May RELEASE-INFO / tags move to 0.2.2 here? | **No** |
| What about missing GitHub Release for 0.2.1? | Publish-time MUST remains open; creating the Release does not require a version bump |

## Success criteria

1. Audit table items marked **gap** with in-repo closing actions are **met**, or reclassified with a written dated N/A/defer in `docs/DISTRIBUTION.md` / package notes (SHOULD/MAY only for defer).
2. All version-bearing customer artifacts that CI or the standard names agree on **0.2.1**: at minimum RELEASE-INFO, CHANGELOG top released entry, pyproject, plugin.json, CITATION.cff, README badge, README agent-install prompt, landing REV + JSON-LD `softwareVersion`.
3. `docs/DISTRIBUTION.md` exists, tracked, with last-reviewed version/date and rows for applicable channels.
4. `python scripts/check_release.py` exits 0 and enforces RR-B-37 decisions made in this package.
5. Local CI-equivalent gates green: integrity class checks, pytest, tools self-check, compile (as `validate.yml` defines).
6. `.github/pull_request_template.md` present (OSS). Improvement issue form present or explicitly deferred with reason (default: present).
7. Host manifests exist for Claude (already) plus Cursor and Gemini at minimum; versions match 0.2.1.
8. Root `SKILLS.md` lists the one skill **or** an explicit single-skill exemption is encoded in the release gate and documented.
9. Customer-facing em-dash grep clean on README, CHANGELOG, `docs/*.md`, `docs/*.html`.
10. SECURITY supported-versions table reflects the 0.2.x line.
11. README Support names bug vs improvement vs security channels.
12. CHANGELOG has `## [Unreleased]` describing P9 hygiene; no surprise 0.2.2 release metadata.
13. Docs remain truthful about four verify gates, installer behavior, and Codex install path.
14. Package notes list remaining **publish-time** MUSTs: GitHub Release v0.2.1 body with licence-enquiry URL; optional About description polish if still remote-only.
15. No push, no new version tag, no P7 work, no P1–P8 redesign.

## Non-goals reminder

Do not treat `audit.py` PASS alone as release-ready if MANUAL items (keep/drop confirmation, taste, live Release) remain. Do not claim RR-B-29b submissions done. Do not rewrite vendored history for RR-B-27 in this pass.

## References

- Standard: `C:\Users\gower\.zcode\skills\release-repo-standard\references\release-repo-standard.md` (v1.16)
- Skill apply guide: `C:\Users\gower\.zcode\skills\release-repo-standard\SKILL.md`
- Packages doc: `docs/superpowers/packages/2026-09-24-jgs-reference-skill-packages.md` (P9)
- Prior standard-era commit named in package brief: `7110cd2`
