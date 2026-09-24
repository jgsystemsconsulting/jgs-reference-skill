---
date: 2026-09-24
project: jgs-reference-skill
mode: light
rounds: 1
slice: []   # whole repo
input_digest: 8cb6bdd6be4ae6bf7a314f0469f52483f67f49bab2b2153a64cf51db6baa062d
open_objections: []
---

# Repository review findings: jgs-reference-skill (2026-09-24, light)

Four read-only lenses (rot, defect, guard, operate) swept the whole repo in one round. Merge unioned 16 lens findings into 10 issues; triage passed all 10, found no defects, and issued no downgrades, leaving two HIGH findings. Evidence quotes below are verbatim from the surveyed files; line numbers come from the lenses' reads. Verbatim quotes keep their original punctuation, including em dashes and CLI flags that a prose check would otherwise flag.

## I1 · ci-blind-to-tests-and-gates

**Severity:** HIGH | **Corroboration:** 3 (defect, guard, operate) | **Lenses:** defect, guard, operate | **Deps:** none
**Provenance:** defect/ci-blind-to-tests-and-gates (HIGH), guard/ci-skips-security-regression-suite (HIGH), operate/ci-skips-runtime-checks (HIGH)

The only CI workflow (.github/workflows/validate.yml) runs content-integrity greps, SKILL.md frontmatter lint, version-string consistency, and scripts/check_release.py. It never installs deps, never runs the ~4.5k-line pytest suite, never executes the tools self-check licence/structure checks CONTRIBUTING.md requires, and never compile-checks the extraction or pack pipeline. The in-tree security regression suite (output-dir symlink/ownership locks, Unicode sanitization, injection scan coverage, DOCX safety) that CHANGELOG 0.2.0 advertises as shipped therefore cannot fail a PR, and neither can extraction, Excluded-hard-stop, or overlap-detection regressions. Green main can ship broken extractors, weakened licence gates, or regressed security boundaries with no red signal.

Evidence:

- `.github/workflows/validate.yml:L3-5`: `# Self-contained content-integrity gate. Inline bash + python3 stdlib only.`
- `.github/workflows/validate.yml:L19-85`: `- name: Content integrity check`
- `.github/workflows/validate.yml:L84-85`:
  ```
  - name: Release gate (RR-B-15)
          run: python3 scripts/check_release.py
  ```
- `CONTRIBUTING.md:L28-32`:
  ```
  1. Run every tool's self-check; all must pass:
     ```bash
     for t in vet_source check_overlap outline validate_pack pack_eval; do
         python3 tools/$t.py --self-check
  ```
- `CHANGELOG.md:L987`: `- tests/: upstream suite carried over (452 passed, 5 skipped).`
- `CHANGELOG.md:L982-991`:
  ```
  - `book_to_skill/`: +963/−126 across 12 files, new `sanitize.py`
    (invisible/bidi Unicode scrubbing), DOCX XXE/Billion-Laughs hardening,
    subprocess argument-injection hardening
  ```
- `tests/test_output_dir_security.py:L31-38`:
  ```
  def test_prepare_output_dir_rejects_symlink(tmp_path):
      real_dir = tmp_path / "real"
      real_dir.mkdir()
      link = tmp_path / "work"
      link.symlink_to(real_dir)

      with pytest.raises(ExtractionError, match="symbolic link"):
          prepare_output_dir(link)
  ```

Blast radius: broken extractors, weakened licence gates, failing unit tests, or regressed security boundaries (prepare_output_dir, sanitize_extracted_text, scan_generated_skill, DOCX validation) merge on main with a green workflow; the runnable product is never exercised by the only automated gate.

## I2 · build-pack-scaffold-unsafe-and-unvalidated

**Severity:** HIGH | **Corroboration:** 3 (rot, defect, guard) | **Lenses:** rot, defect, guard | **Deps:** I6
**Provenance:** rot/scaffold-todo-unvalidated (MEDIUM), defect/build-pack-unescaped-yaml-fields (MEDIUM), guard/build-pack-unvalidated-slug-path (HIGH)

tools/build_pack.py has three compounding problems on the scaffold boundary. (1) It joins `--out-dir` with a raw `--slug` and immediately mkdir/writes PACK.yaml and LICENSE with no kebab-case check, no `..` rejection, and no resolve-and-containment check under the packs root; pathlib also discards the left operand on an absolute right path, so `--slug /tmp/evil` or `../../outside` writes outside `./packs`, which SECURITY.md explicitly scopes as in-scope. (2) It writes user-supplied title, publisher, version, and license into double-quoted YAML scalars via str.format with no escaping, so a quote, colon-newline, or `#` breaks the file shape or injects keys, and validate_pack's flat parse_simple_yaml then mis-reads mandatory fields. (3) It deliberately emits literal TODO markers into PACK.yaml (built_on, notes) and the LICENSE stub, while validate_pack only checks that fields are present and never rejects TODO text, so incomplete scaffolds pass the structural gate and ship with invisible provenance debt.

Evidence:

- `tools/build_pack.py:L111-120`: `pack_dir = Path(args.out_dir) / args.slug`
- `tools/build_pack.py:L115-120`: `(pack_dir / "chapters").mkdir(parents=True)`
- `tools/build_pack.py:L35-40`:
  ```
  PACK_YAML_TEMPLATE = """\
  slug: {slug}
  title: "{title}"
  publisher: "{publisher}"
  source_version: "{version}"
  license: "{license}"
  ```
- `tools/build_pack.py:L117-120`:
  ```
  (pack_dir / "PACK.yaml").write_text(PACK_YAML_TEMPLATE.format(
          slug=args.slug, title=args.title, publisher=args.publisher, version=args.version,
          license=args.license, tier=tier, commercial_use=commercial,
          share_alike=share_alike, attribution_required=attribution), encoding="utf-8")
  ```
- `tools/build_pack.py:L49-L52`:
  ```
    built_on: "TODO"
  notes: >
    TODO: record how the source licence's conditions (attribution / non-commercial /
  ```
- `tools/build_pack.py:L66-L68`:
  ```
  TODO: reproduce the source's full licence text / terms here. For public-domain
  (US Government) works, state that and keep an attribution courtesy note. For CC
  ```
- `tools/build_pack.py:L90-96`:
  ```
  v = classify(args.title, args.publisher, args.license)
      if v["excluded"]:
          print(f"🔴 REFUSED — source is Excluded: {v['excluded_reason']}", file=sys.stderr)
  ```
- `SKILL.md:L151-L153`:
  ```
  from the licence), and a `LICENSE` stub to complete. Fill the `PACK.yaml` TODOs
  (`source_pages`, `chapters`, `built_on`, `notes`) and reproduce the source's terms
  in `LICENSE`.
  ```
- `tools/validate_pack.py:L33`: `REQUIRED_PACK_FIELDS = ("slug", "title", "publisher", "license", "license_tier", "commercial_use")`
- `tools/validate_pack.py:L37-49`:
  ```
  def parse_simple_yaml(text: str) -> dict:
      """Flat top-level `key: value` scalars only — enough to check mandatory fields."""
      out: dict[str, str] = {}
      for line in text.splitlines():
          if not line or line[0] in " \t#":
              continue
          m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
  ```
- `SECURITY.md:L35-38`: `- any tool that writes outside the intended pack/skill directory;`
- `templates/PACK.yaml:L1073`: `slug: <slug>                                  # = folder name, kebab-case`

Blast radius: a crafted or mistaken `--slug` creates directories and writes LICENSE/PACK.yaml outside the packs tree (including absolute paths) on an agent-driven run; real-world titles with quotes yield corrupt PACK.yaml; and TODO-laden scaffolds with stub licences pass validate_pack as done. Provenance and licence debt ships invisibly while the write boundary the SECURITY policy names stays open.

## I3 · readme-doc-path-drift

**Severity:** MEDIUM | **Corroboration:** 2 (rot, operate) | **Lenses:** rot, operate | **Deps:** none
**Provenance:** rot/readme-install-path-drift (MEDIUM), operate/workdir-path-doc-drift (MEDIUM)

The primary onboarding docs drift from what the code actually does in two ways. Install paths: README's Install section correctly describes the namespaced `~/.claude/skills/jgs/` layout matching install.py, but a later README paragraph still points at `~/.claude/skills/jgs-reference-skill/` with no vendor namespace (docs/other-agents.md documents the correct namespaced form). Work-dir paths: README and docs/skill-usage.md hard-code `/tmp/book_skill_work/...` CLI sequences, while the engine writes to `tempfile.gettempdir()/book_skill_work` (overridable via `BOOK_SKILL_WORKDIR`, which no doc mentions), i.e. `%TEMP%` on Windows. Copy-paste installers land the skill in the wrong tree and copy-paste CLI runs chase a missing full_text.txt on non-Unix hosts.

Evidence:

- `README.md:L228`: `python install.py                 # Claude Code (default), namespaced under ~/.claude/skills/jgs/`
- `README.md:L291-L294`:
  ```
  As an agent skill, install it where your host discovers skills (e.g.
  `~/.claude/skills/jgs-reference-skill/`) and drive it conversationally (see
  [SKILL.md](SKILL.md)). It vets, extracts, outlines, scaffolds, generates, and runs
  the three gates for you.
  ```
- `docs/other-agents.md:L747`: `| Claude Code | `claude` (default) | `~/.claude/skills/<ns>/jgs-reference-skill/` (honours `$CLAUDE_CONFIG_DIR`) | native |`
- `README.md:L282-286`: `python3 scripts/extract.py path/to/source.pdf --mode technical`
- `README.md:L283`: `python3 tools/outline.py --source /tmp/book_skill_work/full_text.txt --out outline.json`
- `docs/skill-usage.md:L841`: `python tools/outline.py --source /tmp/book_skill_work/full_text.txt --out outline.json`
- `book_to_skill/config.py:L5-10`: `OUTPUT_DIR = Path(`
- `SKILL.md:L455-456`: `` `<tempdir>/book_skill_work/{full_text.txt,metadata.json}`. Read `metadata.json` ``

Blast radius: manual and agent-driven installs follow the wrong skills tree, and Windows/non-Unix users cannot follow the documented CLI sequence; onboarding and support repro steps diverge from what install.py and the engine actually write.

## I4 · install-path-and-payload-gaps

**Severity:** MEDIUM | **Corroboration:** 2 (guard, operate) | **Lenses:** guard, operate | **Deps:** I2
**Provenance:** guard/install-unvalidated-namespace-path (MEDIUM), operate/install-payload-blocks-editable-extras (MEDIUM)

install.py has an unsanitized-path hazard and a payload gap. Paths: native targets are built as `claude_home()/skills/<namespace>/jgs-reference-skill` and, with `--force`, `shutil.rmtree(target)` runs before rewriting; `--namespace` and `CLAUDE_CONFIG_DIR` are taken raw with no containment check, so absolute segments or `..` can point the install (and the destructive rmtree) outside the intended skills directory. Payload: the native PAYLOAD copies SKILL.md, scripts, tools, book_to_skill, docs, templates, and licence files but omits pyproject.toml, so the documented prerequisite `pip install -e ".[all]"` (SKILL.md, docs/skill-usage.md) fails in the installed skill tree, leaving only per-package `--install-missing` as a working path.

Evidence:

- `install.py:L45-54`:
  ```
  def claude_home() -> Path:
      cfg = os.environ.get("CLAUDE_CONFIG_DIR")
      return Path(cfg) if cfg else HOME / ".claude"
  ```
- `install.py:L52-54`:
  ```
  "claude":  dict(kind="native",    in_all=True,
                      target=lambda ns: claude_home() / "skills" / ns / SKILL),
  ```
- `install.py:L103-104`:
  ```
  if target.exists():
          shutil.rmtree(target)
  ```
- `install.py:L37-40`: `PAYLOAD = ["SKILL.md", "scripts", "tools", "book_to_skill", "docs", "templates",`
- `SKILL.md:L379-380`: `(`pip install -e ".[all]"` for every format; plain text/Markdown/HTML need none).`
- `docs/skill-usage.md:L792-793`: `(`pip install -e ".[all]"` for every format).`
- `pyproject.toml:L863-869`: `[project.optional-dependencies]`

Blast radius: a hostile or mistaken `--namespace`/`CLAUDE_CONFIG_DIR` can delete or overwrite unrelated trees the process can write via `--force`; and the default install cannot satisfy the documented multi-format extraction prerequisite without recloning the repo, so agents following SKILL.md hit a dead end after a "successful" install.

## I5 · release-info-stale-commit

**Severity:** MEDIUM | **Corroboration:** 1 (rot) | **Lenses:** rot | **Deps:** none
**Provenance:** rot/release-info-stale-commit (MEDIUM)

RELEASE-INFO.txt still pins Source-Commit to 1c8b781, a hash that does not appear in the recorded git history, while HEAD on main is 7110cd2 (2026-09-23 release-standard work) and Built (UTC) is already 2026-09-23. Release provenance is a frozen lie: anyone reproducing a build or tying the 0.2.0 artefact to a tree cannot trust the commit field, and it will keep drifting while version stays 0.2.0 and the tree moves.

Evidence:

- `RELEASE-INFO.txt:L2-L5`:
  ```
  Version:        0.2.0
  Tag:            v0.2.0
  Built (UTC):    2026-09-23T00:00:00Z
  Source-Commit:  1c8b781
  ```
- git log (bundle): `7110cd2 2026-09-23 fix(release): bring repo up to release-repo-standard`

Blast radius: broken reproducibility and audit trail for the published 0.2.0 line; release gates that only compare version strings stay green while the commit pointer rots.

## I6 · pack-yaml-dual-template

**Severity:** MEDIUM | **Corroboration:** 1 (rot) | **Lenses:** rot | **Deps:** I2
**Provenance:** rot/pack-yaml-dual-template (MEDIUM)

Pack provenance shape is defined twice: templates/PACK.yaml (the file docs/PACK-SPEC.md points operators at) and an independent PACK_YAML_TEMPLATE string embedded in tools/build_pack.py. build_pack never reads the template file, and the two sources already disagree (clean placeholder notes vs TODO markers; date placeholder vs "TODO"). Schema or wording changes must be hand-mirrored; drift is the default failure mode.

Evidence:

- `docs/PACK-SPEC.md:L653`: `See [`../templates/PACK.yaml`](../templates/PACK.yaml). Mandatory fields:`
- `templates/PACK.yaml:L20-L24`:
  ```
    built_on: "<YYYY-MM-DD>"
  notes: >
    How the source licence's conditions (attribution / non-commercial / share-alike /
    trademark) are carried forward. Synthesised reference notes only; no long verbatim
    passages (verified with tools/check_overlap.py). For multi-source packs, record
  ```
- `tools/build_pack.py:L35-L53`:
  ```
  PACK_YAML_TEMPLATE = """\
  slug: {slug}
  ...
    built_on: "TODO"
  notes: >
    TODO: record how the source licence's conditions (attribution / non-commercial /
  ```

Blast radius: future PACK.yaml field or wording changes will update one path and leave the other stale; agents following SKILL/build_pack and humans following PACK-SPEC/templates will generate different provenance shapes.

## I7 · vet-mit-substring-false-tier

**Severity:** MEDIUM | **Corroboration:** 1 (defect) | **Lenses:** defect | **Deps:** none
**Provenance:** defect/vet-mit-substring-false-tier (MEDIUM)

tools/vet_source.classify treats any licence string containing the substrings mit, apache, or bsd as Tier 2 open/permissive with commercial_use=true, matching accidental substrings such as "limitations", "committee", or "distributed". Combined with Excluded matching only title|publisher (not the licence field), a non-grant licence prose line can be classified packageable Tier 2 and then scaffolded by build_pack into PACK.yaml as commercially usable.

Evidence:

- `tools/vet_source.py:L99-101`:
  ```
  if any(k in lic for k in ("mit", "apache", "bsd")):
          return _verdict(tier=2, commercial_use=True, share_alike=False,
                          attribution_required=True)
  ```
- `tools/vet_source.py:L74-76`:
  ```
  for kw, reason in EXCLUDED.items():
          if kw in hay:
              return _verdict(excluded=True, reason=reason, tier=None)
  ```
- `tools/build_pack.py:L90-96`:
  ```
  v = classify(args.title, args.publisher, args.license)
      if v["excluded"]:
          print(f"🔴 REFUSED — source is Excluded: {v['excluded_reason']}", file=sys.stderr)
  ```

Blast radius: wrong tier/commercial_use written into PACK.yaml; packs may be published under an incorrect redistribution grant that validate_pack will still accept if fields are filled.

## I8 · pack-eval-vacuous-pass

**Severity:** MEDIUM | **Corroboration:** 1 (defect) | **Lenses:** defect | **Deps:** none
**Provenance:** defect/pack-eval-vacuous-pass (MEDIUM)

pack_eval is the Step 9 "index truth" gate: every Topic Index route must be grounded. evaluate() simply skips non-matching lines; if the pack has no Topic Index section, a malformed index, or zero parseable entries, main() prints "No Topic Index entries found to evaluate." and exits 0. That is a green gate for a missing router, the opposite of the SKILL.md rule that all three verify steps must pass before the pack is done.

Evidence:

- `tools/pack_eval.py:L105-107`:
  ```
  if total == 0:
          print("No Topic Index entries found to evaluate.")
          return 0
  ```
- `tools/pack_eval.py:L55-61`:
  ```
  for line in region.splitlines():
          lm = TOPIC_LINE.match(line)
          if not lm:
              continue
          term, refs = lm.group(1), re.findall(r"ch\d+", lm.group(2).lower())
          if not refs:
              continue
  ```
- `SKILL.md:L539-552`: `## Step 9: VERIFY (three gates, all must pass)`

Blast radius: incomplete or broken topic indexes publish as verified; agents mis-route queries to chapters that were never indexed, undermining the reference-oracle claim.

## I9 · prompt-injection-scan-omitted-from-verify-gate

**Severity:** MEDIUM | **Corroboration:** 1 (guard) | **Lenses:** guard | **Deps:** none
**Provenance:** guard/prompt-injection-scan-omitted-from-verify-gate (MEDIUM)

Upstream-added tools/scan_generated_skill.py is an advisory prompt-injection / unsafe-authority scanner for generated skill markdown (ignore-previous, system tags, tool-call tokens, exfil patterns), with symlink and size guards. SKILL.md Step 9's mandatory verify trio is only check_overlap, validate_pack, and pack_eval; the injection scan is never required before reporting a pack done. Extraction sanitizes invisible code points, but phrase-level injection in synthesised chapter/SKILL text is unchecked by the documented publish gate.

Evidence:

- `SKILL.md:L539-552`:
  ```
  ## Step 9: VERIFY (three gates, all must pass)

  ```bash
  # (a) licence-safety + quality: no verbatim passages lifted from the source
  python3 <SKILL_DIR>/tools/check_overlap.py --source <full_text.txt> --pack packs/<slug>
  # (b) structure + provenance: required files, frontmatter, links, PACK.yaml fields, tier
  python3 <SKILL_DIR>/tools/validate_pack.py packs/<slug>
  # (c) index truth: every Topic-Index route is grounded in the chapter it points to
  python3 <SKILL_DIR>/tools/pack_eval.py --pack packs/<slug>
  ```
  ```
- `tools/scan_generated_skill.py:L4`: `"""Advisory scan for prompt injection and unsafe authority in generated skills."""`
- `CHANGELOG.md:L990-991`:
  ```
  Vendored upstream `tools/discovery_tax.py` and `tools/scan_generated_skill.py`
    (advisory prompt-injection scan for generated skills).
  ```

Blast radius: packs can pass the three publish gates while carrying instruction-override or tool-call control phrases into agent-loaded SKILL.md/chapters; operators who follow SKILL.md alone never run the scanner that exists to catch that class.

## I10 · contributing-omits-pytest-runbook

**Severity:** MEDIUM | **Corroboration:** 1 (operate) | **Lenses:** operate | **Deps:** I1
**Provenance:** operate/contributing-omits-pytest-runbook (MEDIUM)

The repo ships a large pytest suite (tests/test_book_to_skill.py alone ~1892 lines; CHANGELOG claims 452 passed) and even a .pytest_cache artifact trail, but CONTRIBUTING.md's "Before you open a PR" checklist only requires tools self-checks and py_compile. No mention of pytest, required extras, or how to run the suite. Combined with CI not running tests, contributor onboarding has no single documented command that validates the extraction engine the fork vendors.

Evidence:

- `CONTRIBUTING.md:L27-34`: `## Before you open a PR`
- `CHANGELOG.md:L987`: `- `tests/`: upstream suite carried over (452 passed, 5 skipped).`
- `tests/test_repo_hygiene.py:L8`: `import pytest`

Blast radius: contributors skip the real suite, open PRs that only pass local self-checks, and reviewers have no shared runbook; extraction regressions that self-check does not cover slip through until a user hits them.

## Advisories

Below-the-findings-bar material recorded for a later packaging run to judge; none of these were graded as issues this round.

| Id | Title | Evidence |
|----|-------|----------|
| a-01 | README claims every tool has --self-check; build_pack.py has none | README.md Tools section; tools/build_pack.py |
| a-02 | discovery_tax.py / scan_generated_skill.py sit outside SKILL pipeline (vendored advisory per CHANGELOG) | CHANGELOG.md:L990-L991; tools/discovery_tax.py; tools/scan_generated_skill.py |
| a-03 | book_to_skill/utils.py ~1k-line vendored monolith; CONTRIBUTING forbids local divergence | book_to_skill/utils.py; CONTRIBUTING.md:L13-L16 |
| a-04 | CONTRIBUTING self-check loop omits build_pack (and advisory tools) | CONTRIBUTING.md:L30-L32 |
| a-05 | check_overlap tokenizes only [a-z0-9]+ so CJK/verbatim non-Latin runs are invisible to the n-gram gate | tools/check_overlap.py:L37-41 |
| a-06 | outline.py exits 0 with empty outline when no headings match (only stderr note) | tools/outline.py:L132-135 |
| a-07 | validate_pack never asserts required Scope & Limits section despite PACK-SPEC/SKILL requiring it | tools/validate_pack.py:L53-106 |
| a-08 | tools/ have --self-check only; zero pytest modules cover vet/overlap/validate/pack_eval/build_pack | tests/ (no matches for vet_source\|check_overlap\|validate_pack) |
| a-09 | vet EXCLUDED key 'iec ' trailing space can miss bare IEC publisher tokens at string end | tools/vet_source.py:L43 |
| a-10 | outline.py --out writes any path the operator passes; no containment, but fully intentional CLI output flag | tools/outline.py:L127-128 |
| a-11 | build_pack PACK.yaml/.format embeds title/license raw; quote/newline can break YAML shape, not a remote sink | tools/build_pack.py:L117-120 |
| a-12 | DOCX safety is multi-encoding DOCTYPE/ENTITY string scan, not a rejecting XML parser; defense-in-depth already present | book_to_skill/parsers/docx.py:L93-108 |
| a-13 | subprocess calls use argv lists + abspath (pdftotext/pdfinfo/ebook-convert/pip); no shell=True found | book_to_skill/parsers/pdf.py:L81-84 |
| a-14 | SECURITY.md supported-versions table still lists 0.1.x while release is 0.2.0; policy staleness not a boundary hole | SECURITY.md:L7-9 |
| a-15 | vet_source 'iso' substring can over-exclude titles; fails closed, not an auth bypass | tools/vet_source.py:L41-42 |
| a-16 | No secrets/credentials in tracked tree; CI leak-sentinel grep covers PRIVATE KEY/CONFIDENTIAL | .github/workflows/validate.yml:L906-914 |
| a-17 | README install target example omits jgs/ namespace vs install.py default | README.md:L291-292 |
| a-18 | README CLI blocks prefer python3 while Install section uses plain python | README.md:L228 vs README.md:L272 |
| a-19 | build_pack.py template TODOs are intentional scaffold placeholders, not operator docs gaps | tools/build_pack.py:L49 |
| a-20 | Transform-agent tool limitation is already documented in docs/other-agents.md | docs/other-agents.md:L758-772 |
