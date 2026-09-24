---
date: 2026-09-24
project: jgs-reference-skill
mode: light
rounds: 1
input_digest: 5ba2da56a26588a24be5ca15d6dd84973a8be083144e286d9a0b214351003e61
open_objections: []
---

# Work packages: jgs-reference-skill (2026-09-24, light, round 1)

Three lenses (value, risk, cohesion) swept the ingest bundle: repo survey, the 2026-09-24 repo-review findings (I1-I10 plus advisories a-01..a-20 with an all-PASS triage log), and user-intent statements from the same-day session. Merge unioned 13 lens candidates into 6 packages; triage passed all 6 with no critical defects and ordered them P1 through P6. Two scope questions are escalated to the human fork at the proposal stop: X1 (whether `scan_generated_skill` joins the Step 9 gate set, inside P4) and X2 (whether P3 and P6 stay standalone or fold into P2 and the release procedure). Everything the lenses killed as out of scope is routed in `docs/superpowers/backlog.md`; nothing was dropped for missing evidence.

Execution order: P1, P2, P3, P4, P5, P6, P8, P9. Each package is sized for one `superpowers-process full` run. P7 (jgs-motion-pack) is user-scope work in a separate repository and runs outside this repo's drain.

Proposal-stop resolution (2026-09-24, user direction): the full cut P1-P6 was picked for execution in suggested order, plus two user-directed packages appended below (P8 website alignment to the jgs-archi-skills standard, P9 release-repo-standard pass). Fork X2 resolves to the documented recommendation: P3 and P6 stay standalone. Fork X1 resolves to option (a): wire `scan_generated_skill` into Step 9 as a fourth gate (P4).

Prose-check exception: residual `spaced-double-hyphen` flags are literal CLI option names (`--self-check`, `--slug`, `--force`, `--namespace`) quoted inside code spans; they are kept verbatim.

## P1 · ci-pytest-tool-gates

| Field | Value |
|---|---|
| id / name | P1 · ci-pytest-tool-gates |
| size | M |
| deps | none |
| status | done |
| corroboration | 3 (value, risk, cohesion) |
| provenance | value/ci-run-suite-and-tool-gates, risk/ci-run-pytest-and-tool-gates, cohesion/ci-pytest-contributor-loop |
| promoted_ids | (first run: none) |
| first_prompt | `/superpowers-process full "CI: run the pytest suite and tools self-checks in validate.yml; document the matching CONTRIBUTING runbook command"` |

**Problem.** The only CI job is a stdlib content-integrity gate that never installs deps, never runs the ~4.5k-line pytest suite (including the security regressions CHANGELOG 0.2.0 advertises), never runs the tools `--self-check` loop CONTRIBUTING requires, and never compile-checks the extract/pack pipeline. Green main cannot fail on broken extractors, weakened licence gates, or regressed security boundaries; CONTRIBUTING's PR checklist omits pytest, leaving two doors to green-on-broken.

**Evidence.**
- `.github/workflows/validate.yml:L3-5`: `# Self-contained content-integrity gate. Inline bash + python3 stdlib only.`
- `.github/workflows/validate.yml:L84-85`: release gate runs only `python3 scripts/check_release.py`
- `CONTRIBUTING.md:L28-34`: PR checklist is the five-tool self-check loop plus `py_compile`, no pytest
- `CHANGELOG.md:L17`: `- tests/: upstream suite carried over (452 passed, 5 skipped).`
- `tests/test_output_dir_security.py:L31-38`: `def test_prepare_output_dir_rejects_symlink(tmp_path):` (in-tree security suite CI never runs)
- Prior review triage: I1 PASS (HIGH), I10 PASS (MEDIUM, rides here as the docs half)

**In scope.** Wire pytest (with required extras) into `.github/workflows/validate.yml` on push/PR; run `tools/{vet_source,check_overlap,outline,validate_pack,pack_eval}.py --self-check` in CI; optional py_compile or smoke of extract/pack entrypoints; document the single CONTRIBUTING runbook command that mirrors CI.

**Out of scope.** Rewriting the content-integrity/leak-sentinel steps; coverage quotas or non-stdlib test frameworks; fixing individual product bugs the suite already catches; user-scope toolchain work; RELEASE-INFO rewrite unless the version job already touches the file.

**Why now.** Without a red signal on PR, every later scaffold, vet, and verify fix in P2-P4 can land and silently regress. This is the payoff lock for a public release-standard repo, which is why it precedes all of them.

**Triage notes.** PASS, size M, no open defects.

## P2 · pack-scaffold-provenance

| Field | Value |
|---|---|
| id / name | P2 · pack-scaffold-provenance |
| size | M |
| deps | none |
| status | done |
| corroboration | 3 (value, risk, cohesion) |
| provenance | value/harden-build-pack-scaffold, risk/build-pack-path-yaml-harden, cohesion/pack-scaffold-provenance |
| promoted_ids | (first run: none) |
| first_prompt | `/superpowers-process full "harden build_pack scaffold: slug containment, safe YAML emit, single PACK.yaml template source, validate rejects TODO provenance"` |

**Problem.** build_pack is the entry to licence-clean pack production but joins raw `--slug` onto `--out-dir` with no kebab-case check, no `..` rejection, and no containment under the packs root (pathlib discards the left operand on an absolute right path), `.format`-injects title/publisher/version/license into double-quoted YAML with no escape, and emits TODO provenance that validate_pack never rejects, while templates/PACK.yaml is a second divergent shape and validate_pack's flat `parse_simple_yaml` mis-reads broken scalars. Uncontained or malformed scaffolds can write outside `./packs` (SECURITY.md names this in scope) and still pass structural gates.

**Evidence.**
- `tools/build_pack.py:L111-120`: `pack_dir = Path(args.out_dir) / args.slug` then immediate mkdir/writes
- `tools/build_pack.py:L117-120`: `PACK_YAML_TEMPLATE.format(...)` straight into `write_text`
- `tools/build_pack.py:L35-53`: embedded template carries `built_on: "TODO"` and TODO notes
- `templates/PACK.yaml:L7-20`: clean placeholder shape that already disagrees with the embed
- `tools/validate_pack.py:L33-49`: `REQUIRED_PACK_FIELDS` presence check only, flat scalar parser
- `SECURITY.md:L35-38`: `- any tool that writes outside the intended pack/skill directory;`
- Prior review triage: I2 PASS (HIGH), I6 PASS (MEDIUM, folded here per merge kill)

**In scope.** Contain pack_dir under resolved out-dir (reject absolute slug, `..`, non-kebab) before mkdir/write; escape or structured-dump YAML scalars; unify PACK.yaml shape to one source and delete the divergent embed; validate_pack rejects TODO/placeholder provenance tied to scaffold output; minimal regression tests for path escape and YAML-break cases.

**Out of scope.** Full YAML library migration or full rewrite of the validate_pack parser; PACK-SPEC field redesign; install.py payload/paths (P5); CI wiring (P1); Step 9 gate logic (P4); vendored book_to_skill/ engine changes.

**Why now.** Every licence-clean pack starts at scaffold. Uncontained or unvalidated scaffold output makes the downstream vet (P3) and verify (P4) gates moot, because they trust the files this writes.

**Triage notes.** PASS, size M, no open defects. X2 partially lands here: see the P3 and P6 notes on the fold-vs-standalone fork.

## P3 · vet-licence-token-match

| Field | Value |
|---|---|
| id / name | P3 · vet-licence-token-match |
| size | S |
| deps | P1 |
| status | done |
| corroboration | 2 (value, risk) |
| provenance | value/fix-vet-licence-token-match, risk/licence-and-verify-false-greens |
| promoted_ids | (first run: none) |
| first_prompt | `/superpowers-process full "vet_source boundary-aware licence family matching for Tier 2 commercial_use"` |

**Problem.** vet_source classifies any licence string containing the substrings mit, apache, or bsd as Tier 2 with `commercial_use=true`, so accidental hits inside words like "limitations", "committee", or "distributed" can mark non-grant prose packageable and commercially usable. That is the exact failure mode the licence-clean product exists to prevent.

**Evidence.**
- `tools/vet_source.py:L99-101`: `if any(k in lic for k in ("mit", "apache", "bsd")):`
- Prior review triage: I7 PASS (MEDIUM, "substring match over-matches non-grant licence prose")

**In scope.** Token or boundary-aware licence family matching so only real MIT/Apache/BSD grants become Tier 2 `commercial_use`; self-check or tiny tests covering the false-tier case.

**Out of scope.** Excluded-title heuristics (a-09/a-15, backlog b-05); full licence NLP or classifier redesign; SKILL copy rewrites; PACK.yaml emission (P2 owns the scaffold write).

**Why now.** False `commercial_use` is a direct product-goal miss; packs scaffolded from a bad vet bake the wrong licence grant into PACK.yaml before any later gate looks at it. Depends on P1 so the new matching has a red path that catches regressions.

**Triage notes.** PASS, size S, no open defects. X2 fork: cohesion and risk both killed a standalone I7 package (classify() is stamped only on the scaffold write path, so folding into P2 was argued); the scope-signature test kept it separate because there is no shared dominant subsystem with P2. Human fork at the proposal stop: keep P3 standalone (recommended, it is a clean S) or fold into P2.

## P4 · step9-verify-gates

| Field | Value |
|---|---|
| id / name | P4 · step9-verify-gates |
| size | M |
| deps | P2, P1 |
| status | ready |
| corroboration | 3 (value, risk, cohesion) |
| provenance | value/pack-eval-fail-empty-topic-index, risk/licence-and-verify-false-greens, cohesion/step9-verify-gates |
| promoted_ids | (first run: none) |
| first_prompt | `/superpowers-process full "Step 9 verify gates: pack_eval fail-closed on empty Topic Index; decide scan_generated_skill gate membership"` |

**Problem.** SKILL.md Step 9 defines three verify gates that all must pass, but pack_eval returns 0 when total==0 (no or malformed Topic Index), so a pack with a missing router gets a green gate that contradicts the documented rule. scan_generated_skill ships in-tree (CHANGELOG 0.2.0) but sits outside the documented trio, so phrase-level injection in synthesised chapter and SKILL text never fails the publish gate set.

**Evidence.**
- `tools/pack_eval.py:L105-107`: `if total == 0: print("No Topic Index entries found to evaluate."); return 0`
- `SKILL.md:L199-207` (and L539-552 in the findings read): `## Step 9: VERIFY (three gates, all must pass)`
- `README.md:L108-111`: verify block mirrors the three-gate list
- `CHANGELOG.md:L990-991`: scan_generated_skill shipped as advisory, never required by Step 9
- Prior review triage: I8 PASS (MEDIUM), I9 PASS (MEDIUM)

**In scope.** pack_eval fail-closed (non-zero exit, clear error) on zero/malformed Topic Index; decide and wire scan_generated_skill into Step 9, or explicitly document advisory-only with matching README/SKILL gate lists; self-check or tiny tests covering the empty-index case.

**Out of scope.** Scoring quality thresholds beyond empty/malformed; scaffold path/YAML/template work (P2); validate_pack REQUIRED field policy except the gate-list doc touch; CI wiring (P1); check_overlap CJK tokenizer (backlog b-03); outline.py empty-outline exit (backlog b-04).

**Why now.** The publish contract is the shared consumer of pack output. A vacuous green lets unfinished packs look publishable, and a later CI-on-gates signal (P1) would lie about the same Step 9 flow. Needs P2 done so validate_pack's TODO rejection is in place before the gate list is re-cut.

**Triage notes.** PASS, size M, no open defects. X1 human fork (mandatory): the three lenses disagreed on scan_generated_skill gate membership. Value put wiring it in out of scope (advisory by design); cohesion put the decide-and-wire in scope; risk killed a standalone I9 package. The merged in_scope records the decide-or-document cut. The proposal stop must pick: (a) wire scan into Step 9 as a fourth gate, or (b) document it advisory-only and align the gate lists. Either resolves inside this package.

## P5 · install-containment-and-docs

| Field | Value |
|---|---|
| id / name | P5 · install-containment-and-docs |
| size | M |
| deps | none (order position 5 by triage) |
| status | ready |
| corroboration | 2 (risk, cohesion) |
| provenance | risk/install-force-path-containment, cohesion/install-path-docs-surface |
| promoted_ids | (first run: none) |
| first_prompt | `/superpowers-process full "install.py namespace containment under --force, pyproject payload gap, install-path and workdir doc consistency"` |

**Problem.** install.py builds native targets from raw `--namespace`/`CLAUDE_CONFIG_DIR` with no containment check, then under `--force` runs `shutil.rmtree(target)`, so absolute or `..` segments can point a destructive rmtree outside the skills directory. PAYLOAD omits pyproject.toml so the documented `pip install -e ".[all]"` fails in the installed tree. README and docs/skill-usage.md hard-code `/tmp/book_skill_work` while the engine writes `tempfile.gettempdir()/book_skill_work` overridable via `BOOK_SKILL_WORKDIR`, and README advertises a non-namespaced install path beside the correct one.

**Evidence.**
- `install.py:L103-104`: `if target.exists(): shutil.rmtree(target)`
- `install.py:L37-40`: PAYLOAD list without pyproject.toml
- `install.py:L45-54`: `claude_home()` from raw `CLAUDE_CONFIG_DIR`
- `SKILL.md:L379-380`: documented `pip install -e ".[all]"` prerequisite
- `book_to_skill/config.py:L5-10`: `OUTPUT_DIR` from `BOOK_SKILL_WORKDIR` or tempdir
- `README.md:L106-115` (and L291-294): `/tmp/book_skill_work` sequences and non-namespaced path
- Prior review triage: I4 PASS (MEDIUM), I3 PASS (MEDIUM, doc half rides here per merge kill)

**In scope.** Resolve and contain the install target under the skills root before mkdir/rmtree and reject absolute/`..` namespace escape; add pyproject.toml to PAYLOAD (or retarget the docs) so editable install matches documentation; README/docs/skill-usage/other-agents install-path and `BOOK_SKILL_WORKDIR` consistency; regression test or assertion for containment on `--force`.

**Out of scope.** Transform-agent install formats (a-20, already documented); build_pack scaffold safety (P2); CI workflow (P1); Step 9 gate logic (P4); user-scope toolchain work.

**Why now.** A public install entrypoint with `--force` rmtree is a one-shot data-loss path, and wrong-tree or half-installed copies make every other package's fixes unreachable for the operators who hit them.

**Triage notes.** PASS, size M, no open defects.

## P6 · release-info-real-commit

| Field | Value |
|---|---|
| id / name | P6 · release-info-real-commit |
| size | S |
| deps | none |
| status | ready |
| corroboration | 1 (value) |
| provenance | value/refresh-release-info-source-commit |
| promoted_ids | (first run: none) |
| first_prompt | `/superpowers-process full "RELEASE-INFO.txt real Source-Commit and a release-procedure guard against phantom hashes"` |

**Problem.** RELEASE-INFO.txt pins `Source-Commit: 1c8b781`, a hash absent from recorded git history, while HEAD is 7110cd2 and Built (UTC) is already 2026-09-23. Public 0.2.0 provenance is a frozen lie: reproducibility and the audit trail fail the release-standard bar the recent commits claim to meet.

**Evidence.**
- `RELEASE-INFO.txt:L2-5`: `Source-Commit:  1c8b781`
- Git log (bundle): `7110cd2 fix(release): bring repo up to release-repo-standard`
- Prior review triage: I5 PASS (MEDIUM)

**In scope.** Rewrite RELEASE-INFO.txt Source-Commit (and Built stamp if needed) to the real release commit; add a guard to check_release or the release procedure so a phantom hash cannot ship again.

**Out of scope.** Changelog archaeology; tag rewrites; full release-standard checklist expansion.

**Why now.** One-file honesty fix that restores the release-standard claim already paid for in 7f64c1d, ca684af, and 7110cd2, and blocks shipping another public line with fake provenance.

**Triage notes.** PASS, size S, no open defects. X2 fork: cohesion killed this as below package grain (one-file pin fix) and value proposed it standalone. Triage confirmed PASS as an S. Human fork at the proposal stop: run standalone, fold into the next release-procedure touch (possibly inside P1's version-job path), or drop to backlog.

## P7 · jgs-motion-pack

| Field | Value |
|---|---|
| id / name | P7 · jgs-motion-pack |
| size | M |
| deps | none (independent, user-scope) |
| status | ready |
| corroboration | user direction at the 2026-09-24 proposal stop (all three lenses had killed it as out-of-repo; the user picked it anyway, so it lands here as a package) |
| provenance | backlog b-01 (user intent, package-loop r1 §3) |
| promoted_ids | b-01 |
| first_prompt | `/superpowers-process full "jgs-motion-pack: jgs-video-gen agent + jgs-motion-teaser skill in a new private repo, installed to user scope"` |

**Problem.** The user-scope toolchain has no video capability: jgs-image-gen does stills only, jgs-announce ships text plus typed poster, and the release standard has no motion gate. The Higgsfield CLI (v1.1.26, installed) and MCP endpoint (configured) cover video; nothing wraps them as a repeatable skill.

**Evidence.**
- `.zcode/context-state.md` (user-scope session state): items 1-6 of the Higgsfield integration plan
- `docs/superpowers/backlog.md`: b-01
- Session transcript: `higgsfield` CLI v1.1.26 installed; `~/.zcode/cli/config.json` has the higgsfield MCP server

**In scope.** New private repo `jgsystemsconsulting/jgs-motion-pack` holding `agents/jgs-video-gen.md` (Bash to the higgsfield CLI, cost preflight, cap 2 clips, brand bans mirroring jgs-image-gen) and `skills/jgs-motion-teaser/` (10-15s teaser plus poster frame into the announce draft folder); README and install script; install to `~/.zcode/agents` and `~/.zcode/skills` on this machine; integration edits to user-scope `jgs-announce` (optional teaser.mp4) and `release-repo-standard` (motion checklist item) when those skills have no source repo, otherwise documented follow-ups.

**Out of scope.** This repo's code; phase-2 items (soul-id mascot, voices TTS, marketing-studio); public release of the new repo.

**Why now.** The user asked for it at the proposal stop, the CLI is installed, and the brand rules are already codified in jgs-image-gen, so the agent is a mirror job.

**Triage notes.** Not triaged by pkg-triage (added at the proposal stop by user direction). Size M by inspection: one new repo, two artifacts, install script.

## P8 · website-align-jgs-archi-standard

| Field | Value |
|---|---|
| id / name | P8 · website-align-jgs-archi-standard |
| size | M |
| deps | P1-P6 (runs after the functional fixes so the site documents final behavior) |
| status | ready |
| corroboration | user direction, 2026-09-24 superpowers-process invoke |
| provenance | user direction at proposal stop ("ensure website aligns to standard of jgs-archi-skills") |
| promoted_ids | (none) |
| first_prompt | `/superpowers-process full "align docs/index.html website to the jgs-archi-skills site standard"` |

**Problem.** The repo ships a landing page at docs/index.html (published via GitHub Pages, .nojekyll present) whose structure, styling, and conventions were authored ad hoc during the release-standard pass. The sibling repo jgs-archi-skills ships a website that defines the de facto JGSC site standard (layout, nav, styling, fonts, footer, OG/meta conventions). This repo's site has not been checked against that standard and drifts where the two disagree.

**Evidence.**
- `docs/index.html` (14,141 bytes) plus `docs/fonts/` (inter-400/600, jetbrains-mono-400/700 woff2) and `docs/.nojekyll` in the tracked tree
- Sibling repo jgs-archi-skills website (its docs/ site) is the named standard; no cross-check exists in this repo
- Release commits 7f64c1d, ca684af, 7110cd2 built the current page without a sibling-standard comparison

**In scope.** Survey the jgs-archi-skills site (structure, CSS conventions, fonts, nav, footer, meta/OG, accessibility basics); diff this repo's docs/index.html against it; align structure and conventions where they diverge, keeping this repo's own content and brand accuracy; keep the page self-contained and GitHub Pages-compatible.

**Out of scope.** New site frameworks or build tooling; content rewrites beyond what alignment requires; jgs-archi-skills repo changes; motion or video assets (P7 territory).

**Why now.** The site is the public face for the licence-clean pack tool and already serves; aligning it after the functional packages (P1-P6) means it documents the final gate behavior, and before the release-standard pass (P9) which audits the finished tree.

**Triage notes.** Added at the proposal stop by user direction; size M by inspection (one HTML file plus assets, standard survey + alignment edits).

## P9 · release-repo-standard-pass

| Field | Value |
|---|---|
| id / name | P9 · release-repo-standard-pass |
| size | M |
| deps | P1-P8 (audits the finished tree) |
| status | ready |
| corroboration | user direction, 2026-09-24 superpowers-process invoke |
| provenance | user direction at proposal stop ("also run release stand on repo") |
| promoted_ids | (none) |
| first_prompt | `/superpowers-process full "run the release-repo-standard skill against the repo and close the gaps it finds"` |

**Problem.** The repo was last brought to the JGSC release standard in 7110cd2, but every package in this cut (P1-P8) changes the tree afterwards: new CI behavior, hardened scaffold and vet tools, installer changes, doc drift fixes, a refreshed RELEASE-INFO, and an aligned website. The release standard must be re-run against the finished tree so the repo ships at the standard, not at the standard as of yesterday.

**Evidence.**
- Git log: 7f64c1d, ca684af, 7110cd2 are the prior release-standard passes (v0.1.0, v1.2 de-slop, fix(release))
- This cut modifies CI, tools/, install.py, README/docs, RELEASE-INFO.txt, and docs/index.html after the last pass
- RELEASE-INFO.txt:L2-5 still pins a phantom Source-Commit until P6 lands

**In scope.** Run the release-repo-standard skill (user scope) against the repo; close every gap it finds that P1-P8 did not already close; re-verify the standard checklist end-state.

**Out of scope.** Re-litigating scope P1-P8 already closed; version bump decisions beyond what the standard requires; publishing or pushing.

**Why now.** Last: the standard audits the tree all other packages finished; running it earlier would audit a moving target.

**Triage notes.** Added at the proposal stop by user direction; size M by inspection (standard run + gap closure across the whole tree).
