| Finding | First seen | Last seen | Verdict | Rationale |
|---------|------------|-----------|---------|-----------|
| C1 Goal 3 fill-later output mismatches Goal 4 marker set | R1 | R1 | Genuine | Goal 4 rejects TODO in notes/built_on but the new template emits none there; marker sets must match or detection is dead |
| C2 filled-capable fields and placeholder grammar undefined | R1 | R1 | Genuine | Unscoped `<` check would reject legitimate titles containing `<`; enumerate fields to avoid permanent validate failure |
| C3 LICENSE escaping mandate corrupts licence prose | R1 | R1 | Genuine | YAML-style escaping puts literal backslashes in human-readable LICENSE text; no test covers LICENSE output |
| C4 template fill mechanics and load path undefined | R1 | R1 | Genuine | Three flags share one `<true\|false>` token so naive replace collides; template path resolution unstated |
| C5 round-trip criterion impossible with current reader | R1 | R1 | Genuine | parse_simple_yaml (validate_pack.py L49) strips quotes with no unescape, so quote and newline titles cannot round-trip |
| M1 template inline comments break flat parser | R1 | R1 | Genuine | Filled `license_tier: 1  # comment` parses the comment into the tier value and fails the tier check |
| M2 simulated-fill fixture unspecified | R1 | R1 | Genuine | Scaffold lacks SKILL.md and chapters, so fill alone cannot make validate pass; criterion unmeetable as written |
| M3 signpost packs omit LICENSE; TODO check undefined | R1 | R1 | Genuine | validate skips LICENSE for signpost packs; spec must state the TODO-marker check is non-signpost only |
| M4 containment undefined when out-dir missing | R1 | R1 | FP | Inflation-FP: pathlib resolve() is non-strict, containment works before out-dir exists; mkdir(parents=True) creates it |
| M5 evidence cites docs/PACK-SPEC.md:L653 | R1 | R1 | Genuine | Actual templates/PACK.yaml reference is PACK-SPEC.md:L49; citation is wrong |
| A1 kebab regex accepts Windows reserved names | R1 | R1 | Advisory-skipped | Reserved names fail loudly at mkdir, no escape or corruption; blocklist is out of this package's scope |
| A2 one shape source criterion unsatisfiable literally | R1 | R1 | Advisory-skipped | Semicolon ties shape source to build_pack generation; self-check fixtures are not shape sources under a normal read |
| A3 constraint 6 bans em dashes but stub has them | R1 | R1 | Advisory-skipped | Constraint 6 scopes to touched docs; LICENSE_STUB is a code-emitted artifact consistent with existing repo files |
| A4 Goal 4 omits zero source_pages/chapters counters | R1 | R1 | Advisory-skipped | Zero counters are build completeness, not scaffold markers; different failure class that bloats Goal 4 |
| A5 validation order unstated | R1 | R1 | Advisory-skipped | Goal 1 already requires all checks before any filesystem effect; order follows from that requirement |
| A6 SKILL.md wording drift after marker change | R1 | R1 | Genuine | SKILL.md L151 tells the agent to fill PACK.yaml TODOs, which Goal 3 deletes; one-line sync already in scope |
| A7 criterion contradicts itself re --self-check | R1 | R1 | Advisory-skipped | In-sentence conditional resolves it: build_pack has no --self-check today and none is added; b-07 owns the gap |
| A8 doc-sync names only PACK-SPEC.md | R1 | R1 | Genuine | SKILL.md L151-152 also goes stale; non-goals example should name SKILL.md alongside PACK-SPEC.md |
| A9 parenthetical references nonexistent plan reader | R1 | R1 | Genuine | Dangling reference in the round-trip criterion; subsumed by C5's rewrite of that criterion |

## Round 1 Summary

| Finding | Lens | Severity | Verdict | Action |
|---------|------|----------|---------|--------|
| Marker vocabulary mismatch (Goal 3 vs Goal 4) | saboteur, new_hire, auditor | CRIT | Genuine | Fixed (Round 1, full Goals 2-4 rewrite: TODO markers normative in template) |
| filled-capable/placeholder grammar undefined | saboteur, new_hire | CRIT | Genuine | Fixed (Round 1: enumerated <TOKEN> set + TODO markers) |
| LICENSE escaping scope | saboteur, new_hire | CRIT | Genuine | Fixed (Round 1: LICENSE plain prose, no escaping; PACK.yaml only) |
| Template load path + fill mechanics | saboteur, new_hire | CRIT | Genuine | Fixed (Round 1: per-key token replacement, tool-relative path) |
| Round-trip impossible under blind strip | saboteur, auditor | CRIT | Genuine | Fixed (Round 1: parse_simple_yaml upgraded with json unescape; round-trip = value equality) |
| Inline comments break flat parser | saboteur | MAJ | Genuine | Fixed (Round 1: comments moved to own lines) |
| Simulated-fill fixture unspecified | new_hire | MAJ | Genuine | Fixed (Round 1: normative fixture section) |
| Signpost LICENSE behavior | new_hire | MAJ | Genuine | Fixed (Round 1: signpost skips LICENSE + counters) |
| PACK-SPEC.md:L653 cite | saboteur, auditor | MAJ | Genuine | Fixed (Round 1: L49) |
| Zero counters unowned | saboteur | ADV | Genuine | Fixed (Round 1: source_pages/chapters 0 = unfilled, non-signpost) |
| SKILL.md drift | new_hire, auditor | ADV | Genuine | Fixed (Round 1: Goal 6 doc sync covers SKILL.md:L151-152) |
| Validation order unstated | new_hire | ADV | Genuine | Fixed (Round 1: order stated in Goal 1) |
| Windows reserved names | saboteur | ADV | Genuine | Fixed (Round 1: blocklist in Goal 1) |
| "one shape source in tree" over-broad | saboteur | ADV | Genuine | Fixed (Round 1: "single normative shape source") |
| Em-dash stub vs constraint 6 | saboteur | ADV | Genuine | Fixed (Round 1: stub de-em-dashed; carve-out documented) |
| --self-check criterion contradiction | auditor | ADV | Genuine | Fixed (Round 1: non-goals reconciled with b-07) |
| PACK-SPEC:L653 in context line | auditor | ADV | Genuine (dup of M5) | Fixed (Round 1) |
| "(or the plan's verified reader)" | auditor | ADV | FP (sentence does not exist in the rewritten draft; stale merge carry-over) | Skipped (Round 1) |
| build_pack self-check loop claim | auditor | ADV | Advisory-skipped (covered by non-goals rewrite) | Skipped (Round 1) |

Fixes applied: 12 (coherent rewrite of Goals 1-6, fixture section, constraints, success criteria)
Inflation rate: 0% (0 of 17 CRITICAL+MAJOR findings triaged FP, Recurring FP, or Design)
Validation: PASS (rewritten spec checked against current build_pack.py, validate_pack.py, templates/PACK.yaml, SKILL.md)

## Round 2 Summary

| Finding | Lens | Severity | Verdict | Action |
|---------|------|----------|---------|--------|
| All 6 round-1 fix groups (markers, grammar, escaping pair, fill mechanics, containment, fixture/doc-sync) | saboteur, new_hire, auditor | CRIT/MAJ | Genuine | Confirmed resolved (Round 2 wave) |
| Signpost scope ambiguity ("additionally skip") | saboteur, auditor | ADV | Genuine | Fixed (Round 2: signposts skip all four checks) |
| Nested build.* keys vs flat parser | saboteur, new_hire | ADV | Genuine | Fixed (Round 2: raw-line anchored check stated) |
| Fail-closed false-positive posture | saboteur | ADV | Genuine | Fixed (Round 2: markers reserved, reword-to-publish documented) |
| Template token line shape (bare vs quoted) | new_hire | ADV | Genuine | Fixed (Round 2: bare token lines, json.dumps substitution supplies quotes) |

Fixes applied: 4 (advisory; wave confirmed all 12 round-1 fixes resolved)
Inflation rate: n/a (0 CRITICAL+MAJOR findings this round)
Validation: PASS

## Converged: Round 2

Track 1: Merged verdict NO_CRITICAL_OR_MAJOR. (Round 2 confirmation wave: all 6 round-1 fix groups confirmed resolved by saboteur, new_hire, auditor; four clarifying advisories fixed.)
Total rounds: 2  |  Total fixes: 16
Document is ready.
