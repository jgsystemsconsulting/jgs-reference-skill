# Backlog: jgs-reference-skill

One project per repository. Rows are never deleted; every transition is a status change. Source names the lens or run that surfaced the row.

| id | title | source | status | evidence |
|----|-------|--------|--------|----------|
| b-01 | USER-SCOPE toolchain (not this repo): Higgsfield integration items 1-5 (jgs-video-gen agent, jgs-motion-teaser skill, jgs-announce teaser.mp4, release-standard motion checklist item, superpowers release-visuals leaf); phase-2 soul-id/TTS/marketing-studio deferred | user intent round 1 | promoted | bundle §3 items 1-6; `.zcode/context-state.md`; promoted into P7 (2026-09-24 proposal stop) |
| b-02 | SECURITY.md supported-versions table still lists 0.1.x; update to 0.2.0 | advisories round 1 (a-14) | open | SECURITY.md:L7-9 |
| b-03 | check_overlap `[a-z0-9]+` tokenizer misses CJK/non-Latin verbatim runs in the n-gram gate | advisories round 1 (a-05) | open | tools/check_overlap.py:L37-41 |
| b-04 | outline.py exits 0 on empty outline (no matching headings); should fail closed | advisories round 1 (a-06) | open | tools/outline.py:L132-135 |
| b-05 | vet_source token hygiene: EXCLUDED key `'iec '` trailing space misses end-of-string tokens (a-09); `'iso'` substring over-excludes titles (a-15) | advisories round 1 (a-09, a-15) | open | tools/vet_source.py:L43, L41-42 |
| b-06 | DOCX safety is a multi-encoding DOCTYPE/ENTITY string scan, not a rejecting XML parser (defense-in-depth upgrade) | advisories round 1 (a-12) | open | book_to_skill/parsers/docx.py:L93-108 |
| b-07 | build_pack.py has no `--self-check` while README claims every tool has one and the CONTRIBUTING self-check loop omits it | advisories round 1 (a-01, a-04) | open | CONTRIBUTING.md:L30-32; tools/build_pack.py |
| b-08 | validate_pack never asserts the required Scope & Limits section despite PACK-SPEC/SKILL requiring it | advisories round 1 (a-07) | open | tools/validate_pack.py:L53-106 |
