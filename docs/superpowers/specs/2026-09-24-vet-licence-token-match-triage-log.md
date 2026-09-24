| Finding | First seen | Last seen | Verdict | Rationale |
|---------|------------|-----------|---------|-----------|
| C1 FreeBSD accepted form unreachable by pattern | R1 | R1 | Genuine | L73 requires the matcher to catch "FreeBSD license" but \bbsd\b has no boundary inside "freebsd"; normative table and pattern contradict |
| M1 negated grants still match as commercial | R1 | R1 | Genuine | "non-commercial MIT" passes no earlier branch and \bmit\b matches, returning commercial_use=true; concrete wrong-grant path, guard or declare non-goal |
| A1 Tier 1 publisher-substring hole | R1 | R1 | Design | Pre-existing US_GOV tuple behavior outside package scope; spec non-goals keep adjacent matching hygiene in backlog like a-09/a-15 |
| A2 weak bsd host examples | R1 | R1 | Genuine | distributed, absorbed, subsidy contain no bsd run at all, so the non-match list and its probe rows are vacuous; replace with real hosts |
| A3 probe table omits enumerated forms | R1 | R1 | Advisory-skipped | Accepted forms are marked illustrative; one probe per family locks the boundary contract, a row per spelling is bloat |
| A4 probe tuples not concrete | R1 | R1 | Advisory-skipped | Existing _self_check tuple shape carries over and the slash alternates are deliberate options; literal pairs add spec bloat |
| A5 non-match list mostly unprobed | R1 | R1 | Advisory-skipped | Matcher is one alternation; per-family probes suffice, and bulk-adding the listed bsd hosts would add vacuous probes per A2 |
| A7 SC references old FreeBSD behavior | R1 | R1 | FP | L169-176 contain no FreeBSD reference of any kind; SC alignment is already carried inside C1's fix |
| A6 redundant qualifier clause | R1 | R1 | Genuine | MIT intent cell admits bare \bmit\b accepts every listed form; delete the optional-qualifier parenthetical |
| A8 SC8 conditional wording | R1 | R1 | Genuine | "when the matching rule is documented" lets SC8 pass by doing nothing; make the SOURCE-VETTING note unconditional |

## Round 1 Summary

| Finding | Lens | Severity | Verdict | Action |
|---------|------|----------|---------|--------|
| FreeBSD row vs boundary rule contradiction | saboteur, new_hire, auditor | CRIT | Genuine | Fixed (Round 1: `(?:free\s*)?bsd` prefix form, aligned probes + SC3) |
| Negation gap (non-commercial MIT → Tier 2 true) | saboteur | MAJ | Genuine | Fixed (Round 1: negation guard in shape + Goal 2 sentence + probe rows + SC3b) |
| Tier 1 publisher-substring hole (adjacent) | saboteur | ADV | Advisory-skipped (out of scope; routed to backlog b-05 territory) | Skipped (Round 1) |
| Weak bsd host examples | new_hire, auditor | ADV | Genuine | Fixed (Round 1: synthetic hosts xxbsdxx/bsdlike with rationale) |
| Probe table omits enumerated forms | saboteur, auditor | ADV | Genuine | Fixed (Round 1: FreeBSD + negation rows added) |
| Probe tuples not concrete | new_hire | ADV | Advisory-skipped (SC section already gives literal classify tuples) | Skipped (Round 1) |
| Redundant qualifier clause | new_hire | ADV | Genuine | Fixed (Round 1: deleted) |
| SC/Goal FreeBSD alignment | new_hire | ADV | Genuine | Fixed (Round 1: SC3 includes FreeBSD) |
| SC8 conditional wording | auditor | ADV | Genuine | Fixed (Round 1: unconditional) |

Fixes applied: 5
Inflation rate: 0% (0 of 2 CRITICAL+MAJOR findings triaged FP, Recurring FP, or Design)
Validation: PASS (pattern sanity-run: FreeBSD MATCH, limitations/distributed/xxbsdxx no, negation handled by guard)
