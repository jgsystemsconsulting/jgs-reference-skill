# Spec: P4 step9-verify-gates

- date: 2026-09-24
- project: jgs-reference-skill
- package: P4 (docs/superpowers/packages/2026-09-24-jgs-reference-skill-packages.md)
- author-leaf: fallback (inline); Claude-pinned leaf unavailable; constraints locked at the package proposal stop
- context: ad-hoc (P4 package section; findings I8 and I9; X1 resolved by user direction to wire `scan_generated_skill` into Step 9 as a fourth gate; current files read: SKILL.md Step 9 L202-215 and Signpost Workflow L225-237, README verify block L108-117 and tools table L133-142, tools/pack_eval.py 115 lines including total==0 early return and `--self-check`, tools/scan_generated_skill.py 361 lines CLI and exit codes, tools/validate_pack.py signpost reduced rubric, CHANGELOG 0.2.0 scan advisory entry, existing tests/test_scan_generated_skill.py library coverage)
- research: skipped (internal tool hardening; no external APIs, libraries, or version-sensitive choices)

## Research

research: skipped (internal tool hardening; no external APIs, libraries, or version-sensitive choices)

## Problem

SKILL.md Step 9 is the publish contract for a finished pack. It currently says three gates must all pass before the pack is done. Two independent holes make that contract false in practice.

### (a) pack_eval vacuous green (I8)

`tools/pack_eval.py` is the index-truth gate. For every parseable Topic Index line it checks that each `chNN` reference exists and that the term's key words appear in that chapter. When it finds nothing to evaluate, it still exits success:

```
# tools/pack_eval.py L105-107
if total == 0:
        print("No Topic Index entries found to evaluate.")
        return 0
```

`total == 0` covers three real failure modes that evaluate() currently collapses into the same green path:

1. SKILL.md has no `## Topic Index` section (the section search fails and evaluate falls back to scanning the whole file, then still finds zero `TOPIC_LINE` matches).
2. A Topic Index section exists but every line is malformed relative to `TOPIC_LINE` (`- **Term** → chNN` / `->` / `:` forms).
3. Lines match the bullet shape but yield zero parseable `chNN` refs, so the inner loop never increments `total`.

A pack with a missing or empty router therefore prints a polite note and returns 0. That contradicts the documented rule that the index-truth gate must pass, and it lets unfinished packs look publishable. Module docstring today documents exit 0 = all routes grounded, 4 = mis-route, 2 = usage; it does not describe a fail-closed empty-index path.

### (b) injection scan outside the gate set (I9, X1 = wire in)

`tools/scan_generated_skill.py` ships in-tree (CHANGELOG 0.2.0: vendored as an advisory prompt-injection / unsafe-authority scan). It walks generated skill markdown (SKILL.md, glossary/patterns/cheatsheet, chapters/), rejects symlinks and oversized trees, and flags instruction-override phrases, system tags, tool-call control tokens, exfiltration-shaped language, invisible Unicode, and frontmatter authority wideners.

Step 9's mandatory trio is only `check_overlap`, `validate_pack`, and `pack_eval`. The scanner is never required before reporting a pack done. Extraction already strips invisible code points; phrase-level injection in synthesised chapter and SKILL text is unchecked by the documented publish set. Operators who follow SKILL.md alone never run the tool that exists for that class.

Proposal-stop resolution (packages doc, 2026-09-24, user direction): fork X1 option (a). Wire `scan_generated_skill` into Step 9 as a fourth gate. Do not leave it advisory-only.

## Goals

### 1. pack_eval fails closed on empty or malformed Topic Index

For a **full pack** (PACK.yaml `kind` absent or not `signpost`):

1. SKILL.md **must** contain a `## Topic Index` section (same heading match evaluate already uses: `##\s*Topic Index`, case-insensitive). Missing section is a hard fail.
2. That section must yield **at least one** parseable topic entry: a line matching `TOPIC_LINE` with one or more `chNN` refs. Zero parseable entries after a present section is a hard fail (covers malformed bullets and bullets with no chapter refs).
3. On either hard fail, `main` prints a clear error to stdout or stderr naming the condition (missing section vs zero parseable entries), and returns a **non-zero** exit code.
4. When `total >= 1`, existing behaviour is unchanged: print each mis-route, print `passed/total`, exit 0 if no failures, exit 4 if any mis-route.

**Exit-code contract (normative, update the module docstring to match):**

| Code | Meaning |
|---|---|
| 0 | Full pack: one or more routes evaluated and all grounded. Signpost short-circuit success (Goal 1 signpost clause). `--self-check` pass. |
| 2 | Usage error (`--pack` missing, argparse). Unchanged. |
| 3 | **New.** Full pack structural index failure: missing Topic Index section, or section present with zero parseable entries (`total == 0` after require-section). |
| 4 | At least one mis-route among evaluated entries. Unchanged. |
| 1 | `--self-check` failure only (existing convention shared with sibling tools). |

Do not reuse 0 for empty index. Do not silently fall back to scanning the whole SKILL.md body when the section is missing: missing section is already a fail, so the `region = m.group(1) if m else skill` fallback is removed or unreachable for the fail-closed path.

**Recommended shape (not sacred if behaviour holds):**

```python
m = re.search(r"##\s*Topic Index(.*?)(?:\n##\s|\Z)", skill, re.S | re.I)
if not m:
    print("ERROR: SKILL.md has no ## Topic Index section.", file=sys.stderr)
    return 3
region = m.group(1)
# ... evaluate region only ...
if total == 0:
    print("ERROR: Topic Index has no parseable entries to evaluate.", file=sys.stderr)
    return 3
```

### Signpost packs (stay consistent with validate_pack)

`validate_pack` already treats `kind: signpost` as a reduced rubric: SKILL.md + PACK.yaml only, no `chapters/`, no LICENSE, no TODO-scaffold checks on the full-pack path. The Signpost Workflow in SKILL.md only requires `validate_pack.py`. Signposts are citation-only, carry no chapter router, and must not be forced through full-pack index truth.

`pack_eval` must stay consistent:

1. If `packs/<slug>/PACK.yaml` parses with `kind: signpost` (same flat scalar style validate_pack uses is enough; reuse or copy the tiny parse, do not add a YAML dependency) **and** the pack has no `chapters/` directory containing chNN files, print a one-line skip note that index-truth eval does not apply to signposts, and exit **0**. The kind scalar alone is not trusted: a pack that carries chapters (or a SKILL.md with a Topic Index heading) is treated as a full pack regardless of the label and falls through to the full-pack rules, so the short-circuit cannot be used to smuggle an unindexed pack past the gate.
2. Do **not** require a Topic Index on signposts.
3. If PACK.yaml is missing or unreadable (signpost status is unknowable then), the full-pack rules apply: the existing evaluate path still runs against SKILL.md; missing Topic Index then fails closed under the full-pack rules. No new PACK.yaml hard requirement beyond the signpost short-circuit read.

`check_overlap` is unchanged by this package and remains inapplicable to signposts (no source extract). Document that only in Step 9 / Signpost prose if a single clarifying sentence is needed; do not redesign overlap.

### 2. scan_generated_skill joins Step 9 as gate (d)

Mandatory fourth gate for **full packs**. Exact invocation and semantics from the tool as it exists today (no CLI redesign in this package).

**Invocation (normative in SKILL.md and README):**

```bash
python3 <SKILL_DIR>/tools/scan_generated_skill.py packs/<slug>
```

Positional `path` argument: generated skill directory **or** its `SKILL.md`. Pack root `packs/<slug>` is the documented form (directory form).

**Exit-code semantics (actual CLI, treat non-zero as gate failure):**

| Code | When | Gate result |
|---|---|---|
| 0 | No findings in scanned scope | pass |
| 1 | One or more advisory findings printed (`WARN ...`) | **fail publish** |
| 2 | `ScanError` (missing dir, symlink skill tree, bad UTF-8, size limits, etc.), message on stderr | **fail publish** |

Skipped out-of-scope markdown notes (files outside SKILL.md / supporting trio / chapters/) stay advisory notes only and do not change the exit code; that behaviour is kept.

**Order in Step 9 (normative):**

```bash
# (a) licence-safety + quality
python3 <SKILL_DIR>/tools/check_overlap.py --source <full_text.txt> --pack packs/<slug>
# (b) structure + provenance
python3 <SKILL_DIR>/tools/validate_pack.py packs/<slug>
# (c) index truth
python3 <SKILL_DIR>/tools/pack_eval.py --pack packs/<slug>
# (d) generated-skill injection / unsafe-authority scan
python3 <SKILL_DIR>/tools/scan_generated_skill.py packs/<slug>
```

Rationale for order: keep the existing trio intact, append the new gate. Operators already scripted for (a)-(c) only grow by one line. Fail-fast order is not required; any non-zero fails publish.

**Heading and copy:**

- SKILL.md: `## Step 9: VERIFY (four gates, all must pass)`
- Body: replace "all three are green" / "the three gate results" with four-gate wording in Step 9 and Step 10 report line.
- README verify block: `# 4. Verify before publishing: all four must pass` plus the four commands (README paths stay `tools/...` as today).
- README tools table: add a row for `tools/scan_generated_skill.py` (prompt-injection / unsafe-authority scan over generated skill markdown) **and** reword the table heading so it no longer claims every tool has `--self-check` (scan does not have one; the five-tool CONTRIBUTING loop stays as P1 locked it).
- Nearby README phrases that say the skill "runs the three gates" (agent blurb) and the mermaid verify node text update to four so the file does not disagree with itself.
- Module docstring of `scan_generated_skill.py` may keep "advisory" in the sense that rules are intentionally broad and findings need human review in context. Step 9 still **requires exit 0** before publish. One short note in the tool docstring or a comment near `main` is enough: gate-required in SKILL Step 9; non-zero fails publish. Do not rebrand the scanner into a different product.

**Remediation contract for gate (d):** the scanned text is generated by the operator's own agent, so every finding is fixable by rewording the flagged passage; that is the primary and default remediation. There is no automated bypass flag. Where a finding is genuinely benign topical text that cannot be reworded without losing meaning, the operator records the rule and justification on a `scan-waiver:` line in the pack's PACK.yaml notes, Waivers never narrow the scan scope and never change the scanner's exit code; they are audit artifacts, not silencers: validate_pack does not read them, the scanner still reports what it reports, and a waivered finding still means gate (d) fails until the text is reworded. In practice the waiver line documents why a known rule fired and what the operator accepted.

**Signpost + scan:**

- Signpost workflow: keep `validate_pack.py` required. **Also** run `scan_generated_skill.py` on the signpost directory (citation SKILL.md is still agent-loaded text). Do not require pack_eval or check_overlap on signposts.
- Full-pack Step 9 remains the four-gate block; signpost section lists its reduced pair explicitly so agents do not apply check_overlap/pack_eval to cite-only packs.

### 3. Self-check coverage for pack_eval empty-index fail-closed

`pack_eval` already has `--self-check` (temp pack with three topic lines, expects total==3, passed==2, one Wrongness mis-route). Extend it, same flag, pure stdlib tempfile style:

1. **Keep** the existing grounded/mis-route assertion (still must pass).
2. **Add** a missing-section case: SKILL.md with chapters but no `## Topic Index` heading. Calling the same path `main` uses for empty detection (evaluate + main logic, or a small helper both call) must produce non-zero exit **3** behaviour; self-check fails if that path returns 0.
3. **Add** a zero-parseable case: SKILL.md with `## Topic Index` and only non-matching lines (plain prose or bullets without `**Term** → chNN`). Must fail closed the same way.
4. Optional third probe: signpost short-circuit returns 0 when PACK.yaml has `kind: signpost` and SKILL.md has no index.

Self-check still exits 0 on full pass, 1 on any failed probe. No new CLI flags.

`scan_generated_skill` has no `--self-check` today and this package does not add one. Its gate requirement is enforced by Step 9 docs plus pytest CLI coverage (Goal 4). Existing library tests stay.

### 4. Regression tests

Pure pytest, stdlib + existing suite style. Prefer one focused module (e.g. `tests/test_pack_eval_fail_closed.py`) plus a thin CLI gate test for scan if not already expressed as exit-code tests.

**pack_eval (required cases):**

| Case | Setup | Expect |
|---|---|---|
| valid pack still passes | Topic Index with grounded routes, chapters present | `main([...])` or evaluate path → exit 0, total >= 1 |
| no Topic Index section | SKILL.md without the heading, chapters optional | non-zero, specifically 3 |
| malformed / zero parseable entries | `## Topic Index` present, no `TOPIC_LINE`+chNN lines | non-zero, specifically 3 |
| mis-route still 4 | grounded + one wrong route (existing self-check shape) | exit 4, not 3 |
| signpost short-circuit | PACK.yaml `kind: signpost`, minimal SKILL.md, no `chapters/` with chNN files, no Topic Index heading | exit 0 |
| labelled full pack (smuggling) | PACK.yaml `kind: signpost` but `chapters/ch01-*.md` present or Topic Index heading in SKILL.md | full-pack rules: exit 3/4, never 0 |

Drive tests through `main(argv)` (or the public helper main calls) so the exit code contract is what CI sees, not only evaluate tuple internals. argv convention: `pack_eval.main` parses `argv[1:]`, so tests pass a program-name placeholder first (`main(["pack_eval", "--pack", str(path)])`).

**scan gate invocation (required cases):**

| Case | Setup | Expect |
|---|---|---|
| clean pack dir | minimal SKILL.md + chapter without injection phrases | subprocess or `main([str(path)])` → 0 |
| crafted injection | same tree with a known rule hit (e.g. `ignore previous instructions` or `SYSTEM:` prefix in chapter body) | exit 1 |

Reuse fixtures/patterns from `tests/test_scan_generated_skill.py` where useful. Do not delete existing scanner unit tests. The new requirement is explicit **exit-code / gate invocation** coverage for publish semantics.

**Unchanged green path:** a valid full pack that already passes today's three gates must still pass (a)(b)(c) after the pack_eval change, and must pass (d) when its generated text is clean.

### 5. Doc sync (mandatory surfaces only)

| File | Change |
|---|---|
| `SKILL.md` Step 9 | Four-gate heading, four-command block, four-green prose |
| `SKILL.md` Step 10 | Report four gate results |
| `SKILL.md` Signpost Workflow | validate_pack + scan; pack_eval/check_overlap not required |
| `README.md` verify block | Four must pass + four commands |
| `README.md` tools table | Add scan_generated_skill row **and** reword the all-self-check heading |
| `README.md` other in-file "three gates" / mermaid verify label | Align to four |

**Untouched by design:** `docs/SOURCE-VETTING.md`, CONTRIBUTING self-check tool list (scan has no `--self-check`; P1 already locked the five-tool loop), CI workflow contents (P1), install paths (P5), RELEASE-INFO (P6). Known drift may remain in `docs/skill-usage.md`, `docs/PACK-SPEC.md`, and `docs/index.html` (the landing page's verify cell still says three gates) blurbs; fixing those is **out of scope** unless a one-line touch is required to avoid a false instruction inside a file this package already edits (it should not edit them). The landing page is P8-owned (website alignment package): P8's doc sync carries the index.html verify-cell correction.

CHANGELOG: optional short Unreleased / next-version note that Step 9 is four gates and pack_eval fails closed on empty index. Not a success-criterion blocker.

## Non-Goals (out of scope)

- Pack scaffold path/YAML/template work (P2, done)
- Vet licence token matching (P3, done)
- CI wiring of pytest or tool self-checks (P1)
- install.py containment and payload (P5)
- RELEASE-INFO real commit (P6)
- check_overlap CJK tokenizer (backlog b-03)
- outline.py empty-outline exit (backlog b-04)
- discovery_tax.py gate membership
- Adding `--self-check` to scan_generated_skill
- Scoring quality thresholds beyond empty/malformed index (no minimum route count above 1, no new grounding heuristics)
- validate_pack REQUIRED field policy changes beyond reading `kind: signpost` from pack_eval's own short-circuit
- Rewriting scan rule regexes or scope bounds
- Non-stdlib dependencies

## Constraints

- Pure Python stdlib only (re, argparse, pathlib, tempfile, subprocess in tests as today).
- Existing gate behaviours unchanged for **valid** full packs: overlap, validate_pack, pack_eval-with-real-index, and clean scan still exit 0 the same way.
- Mis-route exit stays 4; usage exit stays 2.
- No new YAML library; flat PACK.yaml scalar read for signpost kind only.
- Written prose standard on touched docs (SKILL.md / README gate copy): staff-engineer voice, no em dashes, no Tier-1 slop. CLI flags in code spans may contain double hyphens.
- Do not widen into book_to_skill/ engine changes.

## Success criteria

1. `python tools/pack_eval.py --pack <full-pack-without-Topic-Index>` exits non-zero (3) with an error that names the missing section.
2. `python tools/pack_eval.py --pack <full-pack-with-empty-or-malformed-Topic-Index>` exits non-zero (3) with an error that names zero parseable entries.
3. `python tools/pack_eval.py --pack <valid-full-pack-with-grounded-index>` still exits 0 and prints `passed/total`.
4. `python tools/pack_eval.py --pack <pack-with-mis-routes>` still exits 4.
5. `python tools/pack_eval.py --pack <signpost-pack>` exits 0 with an explicit signpost skip note (no Topic Index required).
6. `python tools/pack_eval.py --self-check` covers empty-index fail-closed (missing section and zero-parseable) and still covers the grounded/mis-route case; exits 0 only when all probes pass.
7. SKILL.md Step 9 heading reads four gates; command block lists (a)-(d) in the order above; "all must pass" / done prose refers to four.
8. README verify block mirrors the same four commands and "all four must pass"; tools table lists `scan_generated_skill.py`.
9. Signpost Workflow documents validate_pack + scan_generated_skill; does not require pack_eval or check_overlap.
10. Running `python tools/scan_generated_skill.py packs/<slug>` is mandatory in the full-pack publish path; exit 1 (findings) or 2 (ScanError) fails publish.
11. Regression tests exist and pass for: pack_eval no-section, malformed/zero-parseable, valid pass, mis-route 4, signpost skip; scan CLI/main clean → 0 and injection fixture → 1.
12. Baseline suite plus new tests green; no new runtime deps; SOURCE-VETTING.md unmodified.

## Implementation notes (for the plan author)

- Smallest diff wins: change pack_eval `main`/`evaluate` contract, extend `_self_check`, edit SKILL Step 9/10 + Signpost + README verify/tools, add focused tests.
- Prefer importing `main` in pytest over shelling out, except where subprocess better matches operator invocation; either is acceptable if exit codes are asserted.
- parse_simple_yaml lives in validate_pack; pack_eval may duplicate a five-line scalar read or import from validate_pack. Import is fine if it does not create a circular dependency (today there is none). Duplication is fine for ponytail minimalism.
- Do not change scan rule IDs or messages in this package; only gate membership and docs.
- Quality rule 7 in SKILL.md ("Topic Index is the router, and it must be true") stays true; optional one-line cross-reference to the four-gate Step 9 is enough if edited at all.

## Verification (when implemented)

```bash
python tools/pack_eval.py --self-check
python -m pytest tests/test_pack_eval_fail_closed.py tests/test_scan_generated_skill.py -q
# plus any new scan CLI exit-code test module added by the plan
python tools/pack_eval.py --pack packs/<valid-slug>    # expect 0 on a real grounded pack if present
```

Manual doc check: SKILL.md Step 9 and README verify block list the same four tools in the same order.
