| Finding | First seen | Last seen | Verdict | Rationale |
|---------|------------|-----------|---------|-----------|
| index.html Three gates claim missing from doc-sync table (C1) | R1 | R1 | Genuine | Confirmed docs/index.html:142 and :187 say three gates; P8 owns the landing page, so add it to the spec known-drift list as P8-owned rather than syncing here |
| Signpost short-circuit trusts kind scalar alone (M1) | R1 | R1 | Genuine | Full pack mislabeled signpost silently skips index truth the old pack_eval ran; short-circuit should warn or fail when chapters or Topic Index exist |
| Scan gate has no false-positive remediation path (M2) | R1 | R1 | Genuine | Scanner rules are intentionally broad and exit 1 fails publish, so a reviewed false positive has no recourse; define an explicit waiver or fix-text path |
| README all --self-check heading false for scan row (M3) | R1 | R1 | Genuine | README L133 heading claims every tool has --self-check and the spec adds a scan row without one, so the spec must also fix that heading |
| Missing pack path traceback exit 1 (A1) | R1 | R1 | Advisory-skipped | Pre-existing loud crash, not silent; a new exit code would bloat the exit contract this package already touches |
| Out-of-scope pack-root md scan bypass undocumented (A2) | R1 | R1 | Advisory-skipped | Spec L114 keeps skip-as-advisory behavior and the scanner prints a note per skipped file, so operator-facing prose adds little |
| check_overlap zero-target vacuous green (A3) | R1 | R1 | Design | Constraints freeze check_overlap behavior in this package; the same-class fix belongs in the backlog beside b-04 |
| First-match Topic Index heading false-fail on quoted text (A4) | R1 | R1 | Advisory-skipped | Fails closed rather than silently passing, and the case is rare, so it does not justify widening the diff |
| main argv slicing footgun in tests (A5) | R1 | R1 | Genuine | Spec L243 drives tests through main, which slices argv[1:], so one spec line naming the program-placeholder convention prevents argparse usage errors |
| PACK.yaml OSError fall-through unstated (A6) | R1 | R1 | FP | Inflation-FP: spec L90 already routes missing or unreadable PACK.yaml through the full-pack fail-closed path, which is the OSError case |

## Round 1 Summary

| Finding | Lens | Severity | Verdict | Action |
|---------|------|----------|---------|--------|
| index.html drift ownerless | saboteur, auditor | CRIT (promoted) | Genuine | Fixed (Round 1: declared P8-owned in known-drift) |
| Signpost kind-scalar bypass widens to index gate | saboteur | MAJ | Genuine | Fixed (Round 1: shape guard on short-circuit) |
| Scanner remediation undefined | saboteur | MAJ | Genuine | Fixed (Round 1: reword-default + PACK.yaml waiver audit artifact) |
| README all-self-check heading false for scan | saboteur, new_hire, auditor | MAJ (promoted) | Genuine | Fixed (Round 1: heading reword bullet) |
| FileNotFoundError traceback exit path | saboteur | ADV | Advisory-skipped (nonzero either way; gate still fails safe) | Skipped (Round 1) |
| Out-of-scope .md scan bypass | saboteur | ADV | Advisory-skipped (kept behavior already documented in spec) | Skipped (Round 1) |
| check_overlap vacuous green | saboteur | ADV | Genuine (out of P4 scope) | Routed to backlog b-09 (Round 1) |
| First-match Topic Index false-fail | saboteur | ADV | Advisory-skipped (edge case; false-RED direction is safe) | Skipped (Round 1) |
| main(argv) argv[1:] footgun | new_hire | ADV | Genuine | Fixed (Round 1: convention line) |
| PACK.yaml OSError fall-through | new_hire | ADV | Advisory-skipped (spec rule 3 already covers missing/unreadable) | Skipped (Round 1) |

Fixes applied: 5
Inflation rate: 0% (0 of 4 CRITICAL+MAJOR findings triaged FP, Recurring FP, or Design)
Validation: PASS
