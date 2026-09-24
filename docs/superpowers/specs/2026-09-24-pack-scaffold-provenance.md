# Spec: P2 pack-scaffold-provenance

- date: 2026-09-24
- project: jgs-reference-skill
- package: P2 (docs/superpowers/packages/2026-09-24-jgs-reference-skill-packages.md)
- author-leaf: fallback (inline); constraints locked at the package proposal stop
- context: ad-hoc (P2 package section; findings I2 and I6; current files read in full: tools/build_pack.py 138 lines, tools/validate_pack.py 163 lines, templates/PACK.yaml, SKILL.md scaffold and Step 9 sections; v0.2.1 touched only tools/vet_source.py among tools, so the review's line references hold and were spot-verified)
- research: skipped (internal tool hardening; no external APIs, libraries, or version-sensitive choices)

## Problem

tools/build_pack.py is the entry to licence-clean pack production and it fails three ways at once, on one write path:

1. **Uncontained path join.** `pack_dir = Path(args.out_dir) / args.slug` (L111) with no validation of `--slug`. A slug of `/tmp/evil` discards the left operand entirely (pathlib semantics on an absolute right operand); `../../outside` escapes the packs tree. The very next lines mkdir and write files. SECURITY.md:L35-38 names "any tool that writes outside the intended pack/skill directory" as in scope.
2. **Unsafe YAML emission.** `PACK_YAML_TEMPLATE.format(...)` (L117-120) substitutes title, publisher, version, and license raw into double-quoted YAML scalars (L35-44). A quote, colon-newline, or `#` in a real-world title breaks the file shape or injects keys, and validate_pack's flat `parse_simple_yaml` then mis-reads mandatory fields.
3. **TODO provenance passes the gate.** The scaffold deliberately emits `built_on: "TODO"`, a TODO notes block (L49-53), and a LICENSE stub whose body says `TODO: reproduce the source's full licence text` (L66). validate_pack only checks field presence (REQUIRED_PACK_FIELDS, L33) and never rejects unfilled markers, so an unfilled scaffold passes Step 9's structural gate with invisible provenance debt.

Also on the same path: the PACK.yaml shape exists twice. `PACK_YAML_TEMPLATE` embedded in build_pack (L35-54) and `templates/PACK.yaml` (referenced from docs/PACK-SPEC.md:L49) already disagree: the template file has clean placeholders and inline comments; the embed has literal TODO markers. Drift is the default failure mode (finding I6).

These are one scaffold-to-disk-to-validate data flow, not four themes: every defect lands in the same PACK.yaml write and the same validate read.

## Evidence

- `tools/build_pack.py:L111-115`: `pack_dir = Path(args.out_dir) / args.slug` then `(pack_dir / "chapters").mkdir(parents=True)` with no slug validation
- `tools/build_pack.py:L117-120`: `PACK_YAML_TEMPLATE.format(...)` straight into `write_text`
- `tools/build_pack.py:L35-54`: embedded template with `title: "{title}"` and `built_on: "TODO"`
- `tools/build_pack.py:L56-72`: LICENSE_STUB with `TODO: reproduce the source's full licence text`
- `templates/PACK.yaml`: same shape with `<...>` placeholders and inline comments on the slug and licence-tier lines; already divergent from the embed
- `tools/validate_pack.py:L33`: `REQUIRED_PACK_FIELDS = ("slug", "title", "publisher", "license", "license_tier", "commercial_use")` — presence check only, at L96-98
- `tools/validate_pack.py:L37-49`: `parse_simple_yaml` strips quotes blindly, never unescapes, skips indented lines and block scalars
- `SECURITY.md:L35-38`: `- any tool that writes outside the intended pack/skill directory;`
- `SKILL.md:L151`: the scaffold workflow instructs the operator to "Fill the `PACK.yaml` TODOs ... and reproduce the source's terms in `LICENSE`" — filling happens between scaffold and verify
- Prior review: I2 PASS (HIGH), I6 PASS (MEDIUM, folded into this package)

## Goals

1. **Contained scaffold paths.** build_pack validates `--slug` before any filesystem effect, in this order: (a) kebab-case check `^[a-z0-9]+(-[a-z0-9]+)*$` plus a Windows reserved-name blocklist (con, prn, aux, nul, com1-9, lpt1-9, case-insensitive); (b) containment: resolve the out-dir with `Path(args.out_dir).resolve()` (parents resolve fine without existing), join the slug, resolve again, and require the result to be inside the resolved out-dir before any mkdir or write. Absolute slugs and `..` segments fail the regex or the containment check; all violations exit nonzero with a clear error and create nothing. This works identically for a not-yet-existing out-dir.
2. **Safe YAML values in PACK.yaml only.** User-supplied title, publisher, version, and license are emitted as YAML double-quoted scalars escaped with `json.dumps` (stdlib; produces exactly the YAML double-quoted escaping rules for these characters). validate_pack's `parse_simple_yaml` is upgraded to recognise a fully double-quoted value and unescape it with `json.loads`, so the parsed value equals the original: round-trip means parsed-value equality and no key injection. The LICENSE stub is plain prose: user values go in raw (newlines stripped), no escaping, because no parser consumes it.
3. **One normative template source.** `templates/PACK.yaml` becomes the single normative PACK.yaml shape (self-check fixtures and test fixtures embed shapes for their own purposes and are not normative sources). The template is normalised as part of this package: inline comments move to their own lines (no comment text after values); build-filled fields carry unique single-use bare `<TOKEN>` placeholders on otherwise bare lines (for example the line `title: <TITLE>`; build_pack substitutes the token with the `json.dumps`-escaped value, quotes included), namely `<SLUG>`, `<TITLE>`, `<PUBLISHER>`, `<VERSION>`, `<LICENSE>`, `<TIER>`, `<COMMERCIAL_USE>`, `<SHARE_ALIKE>`, `<ATTRIBUTION_REQUIRED>`; fill-later fields carry literal `TODO` markers (`built_on: "TODO"`, a notes block beginning `TODO:`, `source_pages: 0`, `chapters: 0`). build_pack deletes its embedded `PACK_YAML_TEMPLATE`, loads the template file resolved relative to the tool's own directory, and substitutes each `<TOKEN>` field-targeted (never a global find-and-replace), leaving every TODO marker untouched. The LICENSE stub stays in build_pack (it has no second source) with its em dashes removed and its TODO line intact as the fill-later marker.
4. **The structural gate rejects unfilled scaffolds.** For non-signpost packs, validate_pack fails with named findings when: the raw PACK.yaml text contains `TODO` anywhere, or matches the placeholder pattern `<[A-Z][A-Z_]*>`; or a raw-line match of `source_pages: 0` or `chapters: 0` inside the build block (a raw-text anchored check, since the flat parser skips indented keys); or a present LICENSE still contains the stub line `TODO: reproduce`. These checks are deliberately fail-closed: a real pack whose genuine provenance notes contain the word TODO, or whose title legitimately contains `<WORD>`, must be reworded to publish — the markers are reserved. Signpost packs (`kind: signpost`) skip all four checks (no LICENSE required, no chapters required, no source_pages/chapters zero check, no TODO/placeholder scan). This is coherent with SKILL.md's flow: the operator fills the scaffold between build and Step 9, and Step 9's validate is the publish gate; an unfilled scaffold is never expected to pass.
5. **Regression tests.** tests/ gains coverage in the existing style (pytest, tmp_path): slug escape attempts (`/tmp/evil`, `../../x`, `Bad Slug`, `con`) each exit nonzero and create nothing; YAML break attempts (title containing a double quote, a colon, a newline, `#`) parse back equal through the upgraded parser with no key injection; an unfilled scaffold fails validate naming the markers; the filled fixture (below) passes validate.
6. **Doc sync.** The two places that describe the scaffold's fill-later markers stay truthful: docs/PACK-SPEC.md (the templates/PACK.yaml reference around L49) and SKILL.md:L151-152 (the "Fill the PACK.yaml TODOs" instruction) are updated to the normalised marker scheme in the same change.

## Simulated-fill fixture (normative for the tests)

The "filled" fixture is a complete minimal pack: SKILL.md with valid frontmatter (`name` = slug, a `description`) and one chapter link; `chapters/ch01-example.md` existing; PACK.yaml produced by build_pack with every `<TOKEN>` replaced and every TODO marker manually replaced (built_on set to a date, notes rewritten as real provenance prose, source_pages and chapters set to positive integers); LICENSE containing real reproduced terms with no `TODO: reproduce` line. validate_pack passes this fixture and fails the unfilled scaffold.

## Non-goals

- No vet_source licence-matching changes (P3 owns the substring false-tier issue; build_pack's import of classify stays).
- No CI changes (P1, done), no install.py changes (P5), no Step 9 gate-set changes (P4).
- No real YAML library dependency: tools stay pure stdlib (pyproject comment documents this contract). The json module is stdlib.
- No PACK-SPEC.md field redesign; the doc sync in Goal 6 is wording only.
- build_pack gains no `--self-check` in this package (backlog b-07 owns that gap); the CONTRIBUTING five-tool self-check loop is unchanged.

## Constraints (locked)

1. Tools remain pure stdlib; no new dependencies (json is stdlib).
2. The scaffold hard-stop on Excluded sources (build_pack L90-101) stays byte-equivalent in behavior.
3. templates/PACK.yaml becomes the single normative PACK.yaml shape; the embedded divergent template is deleted.
4. validate_pack's existing checks keep their current meaning; the unfilled-marker rejection and the double-quote unescaping are additive.
5. Containment applies to the resolved out-dir whatever it is, including non-default `--out-dir` values.
6. Written prose standard applies to docs this package touches (PACK-SPEC.md, SKILL.md sync lines): no em dashes, staff-engineer voice. Generated pack content (the LICENSE stub) is exempt but is de-em-dashed anyway as part of Goal 3.

## Success criteria

- `python tools/build_pack.py --slug /tmp/evil ...`, `--slug ../../x`, `--slug "Bad Slug"`, and `--slug con` each exit nonzero with a clear error and create nothing, including when `--out-dir` does not exist yet.
- A title containing `"`, `: `, `#`, or a newline produces a PACK.yaml whose upgraded `parse_simple_yaml` parse returns the original value, with no extra keys; the regression tests prove it.
- The emitted LICENSE shows the raw title text (no backslash artifacts) and no `TODO: reproduce` line after a fill.
- build_pack contains no embedded PACK.yaml template string; the generated scaffold is byte-identical across two runs with the same inputs (deterministic) and matches the normalised templates/PACK.yaml shape.
- `python tools/validate_pack.py <fresh-scaffold>` fails, naming the unfilled markers it found; the simulated-fill fixture passes; signpost fixtures behave as today.
- The doc sync (Goal 6) is applied: no stale "Fill the PACK.yaml TODOs" wording that contradicts the new marker scheme.
- New regression tests green alongside the existing suite (452 passed / 5 skipped baseline plus the new tests); the five-tool self-check loop still passes.

## Research

- research: skipped (internal tool hardening; no external APIs, libraries, or version-sensitive choices)
