<!-- Copyright (c) 2026 JG Systems Consulting Ltd. MIT License (see ../LICENSE). SPDX-License-Identifier: MIT -->

# Distribution ledger · jgs-reference-skill

One row per place this product is, or could be, distributed and discovered
(`RR-B-36`, release-repo-standard). Statuses: `submitted` (URL + date, filed by the
maintainer), `in progress`, `deferred`, `deliberate N/A`, `planned`. A non-submitted
row carries the decision and its date so the question stays closed until its
premises change. Revisit at every release: move statuses, re-date reasons whose
premises changed, never drop a row silently. **An agent never marks a row
`submitted`**; filing is the maintainer's action and this ledger records it.

Last reviewed: 0.2.1 / 2026-09-24

## In-host marketplaces (manifests shipped, RR-B-29a / RR-S-08)

| Channel | Manifest | Status | Decision / reason | Date |
|---|---|---|---|---|
| Claude Code: anthropics/claude-plugins-official | `.claude-plugin/` (shipped) | planned | Manifest shipped in repo. Directory submission after publish; curated review. Maintainer files it. | 2026-09-24 |
| Cursor: cursor.com/marketplace/publish, cursor.directory | `.cursor-plugin/` (shipped) | planned | `plugin.json` + `marketplace.json` shipped for in-repo install. Submission deferred until after the v0.2.1 GitHub Release exists. | 2026-09-24 |
| OpenAI Codex CLI: Plugin Directory | `.agents/plugins/marketplace.json` (shipped) | planned | Codex install today is the deliberate prompts path (see `docs/other-agents.md`); manifest ships so the native marketplace route is open. Submission after publish. | 2026-09-24 |
| Gemini CLI: geminicli.com/extensions gallery | `gemini-extension.json` (shipped) | planned | Manifest shipped; `gemini extensions install <REPO_URL>` verifiable. Gallery PR after publish. | 2026-09-24 |

Manifests satisfy RR-B-29a in-repo only. No directory submission has been filed.

## Web directories & catalogues

| Channel | Artifact | Status | Decision / reason | Date |
|---|---|---|---|---|
| Org catalogue (jgsystemsconsulting.com) | site entry | planned | RR-B-19. No live org catalogue entry exists today; a product entry is planned when the catalogue page next ships. | 2026-09-24 |
| GitHub About + topics + Release | maintainer `gh repo edit` / `gh release create` | planned | RR-B-21 / RR-B-22. Tag `v0.2.1` exists; the **GitHub Release object is missing and is a publish-time MUST**. About description keeps an em dash until the maintainer runs the commands below; add the `cursor` topic. | 2026-09-24 |
| Community directories / awesome-lists | PR or form entry | deferred | RR-B-29b. Assess each list's licence bar before submitting. Agents must not mark these submitted. | 2026-09-24 |

### Maintainer handoff commands (not run in this package)

```bash
# About description (README one-liner, em dash stripped) + homepage
gh repo edit jgsystemsconsulting/jgs-reference-skill \
  --description "Convert vetted authoritative sources into licence-clean, citable knowledge packs. Licence-vet gate, provenance, verbatim-overlap detection." \
  --homepage "https://jgsystemsconsulting.github.io/jgs-reference-skill/"
# topics (idempotent where gh supports)
gh repo edit jgsystemsconsulting/jgs-reference-skill --add-topic cursor
# Release object (body: CHANGELOG 0.2.1 section + licence-enquiry footer)
gh release create v0.2.1 --title "v0.2.1" --notes-file <release-notes.md>
```

Release notes body: the `## 0.2.1 - 2026-09-24` section of `CHANGELOG.md`, plus the
footer line "No purchase or licence key is needed to use this tooling; for
commercial licensing questions see
[labs.jgsystemsconsulting.com/licensing.html](https://labs.jgsystemsconsulting.com/licensing.html)."

## MCP aggregator directories

`RR-M-*`: N/A (not an MCP bridge).

## History policy (RR-B-27)

Inherited upstream (book-to-skill) and personal emails remain in `git log --all`;
that history is retained deliberately and is not rewritten in P9. **New commits
must** use `245595077+jgsystemsconsulting@users.noreply.github.com` (recorded in
[CONTRIBUTING.md](../CONTRIBUTING.md) under Commit identity). Reviewed 2026-09-24.

## Keep / drop decisions (RR-B-35, dated 2026-09-24)

- `docs/superpowers/`: **keep**, frozen process history for this cut. The tracked
  file list is pinned by a sha256 baseline in `scripts/check_release.py`
  (`FROZEN_TREES`); a deliberate change must update the baseline.
- `.zcode/`, `.superpowers/`: remain gitignored session dirs (never tracked).
- `packs/`: **gitignored** (local pack outputs and demos; never committed).

## Deferred standard items

- **RR-S-17 (SHOULD) in-pack feedback utility skill: deferred, 2026-09-24.**
  Reason: keep the P9 minimum; the tracker already has the Improvement issue form
  for feedback.
- **RR-S-12 CI deviation:** the standard CI verify line says no step executes
  checked-out repository code. Since P1 the `tests` job deliberately runs pytest,
  tool `--self-check`, and `py_compile` under `pull_request` semantics with
  `permissions: read-all` and no secrets. Full dated note: see the `## [Unreleased]`
  section of [CHANGELOG.md](../CHANGELOG.md).

## Diagram check (RR-B-26)

Met: the README ships a mermaid pipeline diagram (`flowchart LR` of
vet, extract, outline, build_pack, generate, verify, signpost). No second diagram
added. Reviewed 2026-09-24.
