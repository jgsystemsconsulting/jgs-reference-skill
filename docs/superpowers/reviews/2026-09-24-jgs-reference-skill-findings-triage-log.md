# Triage log — jgs-reference-skill repo review (2026-09-24, light)

| Finding | First seen | Last seen | Verdict | Rationale |
|---------|------------|-----------|---------|-----------|
| I1 ci-blind-to-tests-and-gates | round 1 | round 1 | PASS (HIGH) | 3-lens union (defect/guard/operate); all citations verified against bundle; no downgrade warranted |
| I2 build-pack-scaffold-unsafe-and-unvalidated | round 1 | round 1 | PASS (HIGH) | 3-lens union (rot/defect/guard); slug path-escape confirmed, SECURITY.md names out-of-tree writes in scope; no downgrade |
| I3 readme-doc-path-drift | round 1 | round 1 | PASS (MEDIUM) | 2-lens union (rot/operate); install path and workdir drift both verified |
| I4 install-path-and-payload-gaps | round 1 | round 1 | PASS (MEDIUM) | 2-lens union (guard/operate); unsanitized namespace + rmtree, missing pyproject in payload |
| I5 release-info-stale-commit | round 1 | round 1 | PASS (MEDIUM) | 1c8b781 absent from recorded git history; HEAD is 7110cd2 |
| I6 pack-yaml-dual-template | round 1 | round 1 | PASS (MEDIUM) | two provenance shapes already disagree (TODO vs placeholder) |
| I7 vet-mit-substring-false-tier | round 1 | round 1 | PASS (MEDIUM) | substring match over-matches non-grant licence prose |
| I8 pack-eval-vacuous-pass | round 1 | round 1 | PASS (MEDIUM) | zero-index exit 0 contradicts Step 9 gate rule |
| I9 prompt-injection-scan-omitted-from-verify-gate | round 1 | round 1 | PASS (MEDIUM) | scanner exists in-tree but is outside the documented verify trio |
| I10 contributing-omits-pytest-runbook | round 1 | round 1 | PASS (MEDIUM) | PR checklist omits pytest; pairs with I1 |
