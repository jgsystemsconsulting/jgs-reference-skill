# FCL triage log: docs/superpowers/specs/2026-09-24-ci-pytest-tool-gates.md

| Finding | First seen | Last seen | Verdict | Rationale |
|---------|------------|-----------|---------|-----------|
| C1: CHANGELOG citation drift (spec cites L987) | R1 | R1 | Genuine | Verified: "452 passed, 5 skipped" is at CHANGELOG.md:L17 in a 34-line file; retarget citation. |
| C2: Dead GitHub docs URL at L72 | R1 | R1 | Genuine | Cited building-and-testing-python path no longer resolves; swap for the caching-dependencies primary source. |
| M1: Three Research URLs dead, L72-74 | R1 | R1 | Genuine | Same rot as C2 across all three Research links; replace with working primary sources. |
| M2: "branch protection already exists" unsupported at L50 | R1 | R1 | Genuine | Repo settings are not verifiable in-repo; drop the clause or cite protection rules evidence. |
| A1: L12 "never executes checked-out repo code" contradicts check_release.py run | R1 | R1 | Genuine | Verified: validate.yml:L85 runs scripts/check_release.py. Severity anomaly: skeptic rated CRITICAL, merge under-promoted to ADVISORY; text must be fixed. |
| A2: ~4.5k-line suite overstatement at L14 | R1 | R1 | Genuine | Measured count is ~3.4k lines; one-word numeric fix, cheap and correct. |
| A3: Fork-PR safety misattributed at L46-47 | R1 | R1 | Genuine | validate.yml:L4-5 and L11 tie safety to pull_request trigger and read-all, not non-execution alone; one-line reattribution. |

## Round 1 Summary

| Finding | Lens | Severity | Verdict | Action |
|---------|------|----------|---------|--------|
| CHANGELOG loc drift (L987 vs L17) | skeptic, source, correspondent | CRIT | Genuine | Fixed (Round 1) |
| Dead Research URL for setup-python claim | skeptic, source | CRIT | Genuine | Fixed (Round 1) |
| All three Research URLs 404/403 | correspondent | MAJ | Genuine | Fixed (Round 1) |
| Branch-protection "already exists" unsupported | skeptic | MAJ | Genuine | Fixed (Round 1) |
| Non-execution claim contradicted by check_release.py | skeptic | CRIT per lens; merged ADV (under-promotion noted) | Genuine | Fixed (Round 1) |
| ~4.5k suite size overstates (~3.5k measured) | skeptic | ADV | Genuine | Fixed (Round 1) |
| Fork-safety misattributed to non-execution | skeptic | ADV | Genuine | Fixed (Round 1) |

Fixes applied: 7
Inflation rate: 0% (0 of 7 CRITICAL+MAJOR findings triaged FP, Recurring FP, or Design)
Validation: PASS (CHANGELOG.md:L17 verified by grep; replacement docs URLs fetched 200)

## Converged: Round 2

Track 1: Merged verdict NO_CRITICAL_OR_MAJOR. (Round 2 = confirmation wave: all 5 fixed loc groups confirmed `resolved by this change` by skeptic, source, and correspondent; no new findings.)
Total rounds: 2  |  Total fixes: 7
Document is ready.
