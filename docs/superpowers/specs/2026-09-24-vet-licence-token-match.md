# Spec: P3 vet-licence-token-match

- date: 2026-09-24
- project: jgs-reference-skill
- package: P3 (docs/superpowers/packages/2026-09-24-jgs-reference-skill-packages.md)
- author-leaf: fallback (inline); constraints locked at the package proposal stop
- context: ad-hoc (P3 package section; finding I7; current files read in full: tools/vet_source.py 190 lines including v0.2.1 Excluded entries AFOTEC/DAG/CMU-SEI, tools/build_pack.py classify import and scaffold path, SKILL.md Step 1 vet block, docs/SOURCE-VETTING.md Tier 2 permissive line; tests/ has no module covering vet_source, confirmed by search)
- research: skipped (internal tool hardening; no external APIs, libraries, or version-sensitive choices)

## Problem

`tools/vet_source.classify` is the licence gate that decides whether a source is packageable and whether `commercial_use` may be true. After Excluded and public-domain / Creative-Commons branches, it treats any licence string that merely *contains* the character sequences `mit`, `apache`, or `bsd` as Tier 2 open/permissive with `commercial_use=true`.

That is a substring test, not a grant test. Ordinary non-grant prose that happens to embed those three-letter runs is classified the same way as a real MIT, Apache, or BSD licence:

| Accidental host word | Embedded run | Current result |
|---|---|---|
| `limitations` | `mit` | Tier 2, `commercial_use=true` |
| `committee` | `mit` | Tier 2, `commercial_use=true` |
| Boundary illustration: `FreeBSD license` (pre-fix) | `bsd` had no boundary inside `freebsd`, so the substring check matched it by luck; the boundary matcher needs the explicit `free` prefix form | Tier 2, `commercial_use=true` (unchanged result, now by rule) |

`build_pack` imports `classify` and writes the returned `license_tier` / `commercial_use` / `share_alike` / `attribution_required` straight into `PACK.yaml`. A false Tier-2 verdict therefore becomes a false redistribution grant in provenance before any later gate looks at the licence text again. That is the failure mode the licence-clean product exists to prevent (finding I7).

## Evidence

Current file (v0.2.1 tree; line numbers shifted from the findings doc by the AFOTEC / DAG / CMU-SEI Excluded entries, verified against the file on disk):

- `tools/vet_source.py:L105-107` (the defect):
  ```
  if any(k in lic for k in ("mit", "apache", "bsd")):
          return _verdict(tier=2, commercial_use=True, share_alike=False,
                          attribution_required=True)
  ```
  `lic` is `(license_str or "").lower()` (L76). The test is pure Python `in` on substrings.

- `tools/vet_source.py:L109-114` (fallback the false positives should have taken): step 4 returns Tier 3 with `commercial_use=False`, `share_alike=False`, `attribution_required=True`, and a warning that no recognised redistribution grant was found ("Freely available" is not a licence).

- `tools/vet_source.py:L80-82` (Excluded path, title|publisher only; unchanged by this package):
  ```
  for kw, reason in EXCLUDED.items():
          if kw in hay:
              return _verdict(excluded=True, reason=reason, tier=None)
  ```

- `tools/build_pack.py:L33` and `L114-132`: `from vet_source import classify`; scaffold refuses Excluded, then stamps `license_tier` / `commercial_use` from the verdict into PACK.yaml.

- `docs/SOURCE-VETTING.md:L33`: `Permissive licences (MIT/Apache/BSD) where they cover the text.` Documents the families, not the matching rule.

- `tools/vet_source.py:L131-154`: `_self_check` covers Excluded, Tier 1, CC BY-NC-SA, CC BY-ND, and "freely available" Tier 3. It has **no** case for bare MIT/Apache/BSD grants and **no** false-positive probe for `limitations` / `committee` / `distributed`.

- `tests/`: no `test_*vet*` module; advisory a-08 already recorded zero pytest coverage of vet_source.

- Prior review: I7 PASS (MEDIUM, "substring match over-matches non-grant licence prose").

## Goals

### 1. Boundary-aware permissive-family match

Replace the three-substring `any(k in lic ...)` test with a single case-insensitive token / word-boundary matcher over the already-lowercased `lic` string. A match still returns the existing Tier 2 verdict shape:

```
_verdict(tier=2, commercial_use=True, share_alike=False, attribution_required=True)
```

No match falls through to the existing step-4 path (Goal 3). Implementation stays pure `re` from the stdlib already imported at L28.

**Matcher rule (normative).** A permissive-family hit is a match of any of the following patterns against `lic` (lowercased). Use Python `\b` word boundaries so the family token is not a run inside a longer alphabetic word. Hyphen and other non-word characters already form a boundary, so SPDX-style and "MIT-style" forms work without extra branches.

| Family | Accepted forms the matcher must catch (illustrative spellings; match is on the family token plus optional well-known qualifiers) | Pattern intent |
|---|---|---|
| MIT | `MIT`, `MIT License`, `The MIT License`, `MIT licence`, `X11/MIT`, `MIT-style`, `MIT-style license`, SPDX `MIT` | `\bmit\b` (the bare family token already accepts every listed spelling) |
| Apache | `Apache`, `Apache 2.0`, `Apache License 2.0`, `Apache Licence 2.0`, `Apache-2.0`, `Apache License, Version 2.0`, SPDX `Apache-2.0` | `\bapache\b` |
| BSD | `BSD`, `BSD license`, `BSD 2-Clause`, `BSD 3-Clause`, `BSD-2-Clause`, `BSD-3-Clause`, `2-Clause BSD`, `3-Clause BSD`, `new BSD`, `simplified BSD`, `FreeBSD license`, SPDX `BSD-2-Clause` / `BSD-3-Clause` | `\b(?:free\s*)?bsd\b` (the optional `free` prefix catches the FreeBSD spelling) |

**Concrete implementation shape (recommended, not sacred as long as the accepted-forms table holds):**

```python
_PERMISSIVE_FAMILY = re.compile(r"\b(?:mit|apache|(?:free\s*)?bsd)\b")
# ...
_NEGATION = re.compile(
    r"\bnon[\s_-]*commercial\b|\bno[\s]+commercial\b|\bnot\s+for\s+commercial\b"
    r"|\bcommercial\s+use\s+(?:is\s+)?(?:prohibited|restricted|forbidden|not\s+permitted|not\s+allowed)\b"
    r"|\bnc\b")  # boundary-anchored: the standalone token, never the nc inside licence
if _PERMISSIVE_FAMILY.search(lic) and not _NEGATION.search(lic):
    return _verdict(tier=2, commercial_use=True, share_alike=False,
                    attribution_required=True)
# A negated grant ("non-commercial MIT variant") must NOT return
# commercial_use=True: it falls through to the step-4 caution path.
```

One compiled pattern is enough. Do not enumerate every SPDX string as a separate branch; the boundary on the family token is the contract.

**Explicit non-matches (must stay non-Tier-2 from this branch):**

- `limitations`, `committee`, `permit`, `submit`, `admitted` (host `mit`)
- synthetic embedded hosts `xxbsdxx`, `bsdlike` (no common English word embeds `bsd`; the boundary guard is belt-and-braces, so synthetic tokens probe it)
- bare narrative that never names a family: `all rights reserved`, `freely available`, `see website for terms`

**Out of matcher scope (do not invent):** GPL/LGPL/MPL/EPL and other copyleft families stay on the step-4 Tier 3 path unless a future package adds them. CC stays on the existing `cc` regex branch above this one. Public-domain / US-gov stays on the existing Tier 1 branch.

### 2. Ambiguous family mention fails toward caution

If the licence string does not satisfy the boundary matcher, this branch must **not** return `commercial_use=true`. There is no "maybe MIT" half-tier. The same caution applies to negated grants: a family token accompanied by a non-commercial restriction (spelled `non-commercial`, `noncommercial`, `non commercial`, `no commercial`, `not for commercial`, `commercial use prohibited/restricted/forbidden/not permitted`, or a standalone `nc` token) must not yield `commercial_use=true`; the negation guard in the implementation shape routes it to the step-4 fallback. The trade-off is accepted and deliberate: a legitimate permissive grant whose prose merely mentions non-commercial terms alongside the family token (for example "MIT; no commercial restrictions") is also demoted to the caution path. Failing toward caution is the contract.

Exact fallback (current step 4, keep behavior and warning text unless a trivial wording fix is required for accuracy):

- `license_tier=3`
- `commercial_use=False`
- `share_alike=False`
- `attribution_required=True`
- `excluded=False`
- `recommended_mode="pack"` (Tier 3 is still packageable *with justification*; the warning tells the operator to treat it as Excluded until a real grant is confirmed, matching SOURCE-VETTING.md Tier 3)
- `warnings` contains the existing "No recognised redistribution grant found..." message

Classify order is unchanged and still short-circuits:

1. Excluded on `title | publisher` haystack
2. Public domain / US-gov → Tier 1
3. Creative Commons BY/NC/SA/ND → Tier 2 or 3 (ND)
4. **Boundary-aware** MIT/Apache/BSD → Tier 2 `commercial_use=true`
5. Else → Tier 3 `commercial_use=false` + warning

A licence string that names a family only inside a longer word (the false-positive hosts above) takes path 5, not path 4.

### 3. Self-check and regression coverage

`python tools/vet_source.py --self-check` keeps passing and **gains** cases that lock the new matcher. Prefer extending the existing `_self_check` table and assertions (zero new test framework required for the gate CONTRIBUTING already runs). Optional thin pytest module is allowed but not required if self-check covers every Success criterion probe below.

Required self-check (or pytest) probes, mapped 1:1 to Success criteria:

| Probe class | Input licence (title/publisher neutral non-Excluded) | Expected |
|---|---|---|
| False positive | `limitations of liability apply` | not Tier 2; `commercial_use is False`; tier 3 |
| False positive | `reviewed by committee` | not Tier 2; `commercial_use is False`; tier 3 |
| False positive | `may be distributed under site terms` | not Tier 2; `commercial_use is False`; tier 3 |
| True grant | `MIT` | Tier 2, `commercial_use=True`, `share_alike=False`, `attribution_required=True` |
| True grant | `Apache 2.0` | same Tier 2 shape |
| True grant | `BSD 3-Clause` (and/or `BSD-3-Clause`) | same Tier 2 shape |
| True grant | `MIT-style` | same Tier 2 shape |
| True grant | `FreeBSD license` | same Tier 2 shape (the `(?:free\s*)?bsd` prefix form) |
| Negated grant | `MIT for non-commercial use only` | NOT `commercial_use=True`; falls to the step-4 caution path (tier 3) |
| Negated grant | `noncommercial MIT variant` | same caution path |
| Negated grant | `MIT, commercial use prohibited` | same caution path |
| Negated grant | `MIT; no commercial restrictions` | same caution path (accepted false-negative demotion, see Goal 2) |
| Negated grant | `MIT NC` / `licence nc only` | same caution path (standalone nc token) |
| Negated grant | `MIT, commercial use not allowed` | same caution path (paraphrase) |
| True grant | `MIT licence` and `Apache Licence 2.0` | same Tier 2 shape (the nc inside licence must NOT demote) |
| Excluded unchanged | title/publisher hits for `afotec`, `defense acquisition guidebook` / `dod dag`, `cmu` / `carnegie mellon` / `software engineering institute` (existing EXCLUDED keys) | `excluded=True`, tier `None`; reasons unchanged |
| Existing self-check | current eight table rows (ISO, OMG, Wiley/INCOSE, NASA PD, DoD Dist A, SEBoK CC BY-NC-SA, CC BY-ND, freely available) | same expected excluded/tier as today; SEBoK NC+SA assert unchanged |
| build_pack e2e | real MIT source through `build_pack` (non-Excluded title/publisher, `--license MIT`, unique kebab slug, tmp out-dir) | exit 0; PACK.yaml carries `license_tier: 2` and `commercial_use: true` derived from classify (no manual `--tier` / `--commercial-use` override) |

The build_pack probe may live in `tests/test_build_pack_scaffold.py` (already present from P2) or as a subprocess assertion beside self-check; either is fine. It must not require network, new deps, or writing under the repo's real `packs/`.

### 4. Doc sync

If `docs/SOURCE-VETTING.md` describes *how* MIT/Apache/BSD are recognised, update it in the same change. Today L33 only names the families ("Permissive licences (MIT/Apache/BSD) where they cover the text"). Add one short sentence that recognition is token / word-boundary based on the family name (MIT, Apache, BSD), case-insensitive, so accidental substrings in ordinary prose do not count as a grant. Do not paste the regex into the operator doc.

SKILL.md Step 1 only invokes the tool and consumes the JSON verdict; no SKILL copy change is required unless a line claims substring matching (none found).

## Non-goals

- Excluded-title token hygiene for `iec ` (trailing space, advisory a-09) and `iso` over-exclusion (a-15). Those stay backlog b-05 unless a one-line touch is forced by an edit already inside the EXCLUDED dict; this package does not schedule them.
- CI workflow changes (P1, done).
- build_pack path / YAML / template emission (P2, done). build_pack's `from vet_source import classify` call site stays; only classify's permissive branch changes underneath it.
- New licence families (GPL, MPL, proprietary parsers, full licence NLP).
- Changing Excluded matching to inspect the licence field (I7 mentioned the gap; fixing it is a different design and out of scope).
- Adding `build_pack --self-check` (backlog).
- Rewriting SOURCE-VETTING tier policy, signpost mode, or PACK-SPEC fields.

## Constraints (locked)

1. Pure stdlib only (`re` is already imported). No new dependencies.
2. `python tools/vet_source.py --self-check` keeps passing and gains coverage of the new matcher (false-positive and true-grant probes above).
3. Excluded hard-stop behavior and reasons for existing keys, including the v0.2.1 AFOTEC / DAG / CMU-SEI entries, stay unchanged.
4. Verdict dict shape (`excluded`, `excluded_reason`, `license_tier`, `commercial_use`, `share_alike`, `attribution_required`, `warnings`, `recommended_mode`) stays stable so `build_pack` needs no call-site change.
5. Classify short-circuit order (Excluded → Tier 1 → CC → permissive → Tier 3 fallback) stays stable.
6. False Tier-2 must fail toward caution: no match means step-4 Tier 3 with `commercial_use=False`, never a commercial true.
7. `docs/SOURCE-VETTING.md` stays in sync if it documents the matching rule (Goal 4).
8. Written prose standard on docs this package touches: no em dashes, staff-engineer voice.

## Success criteria

1. `classify("Some Guide", "Author", "limitations of liability apply")` returns `license_tier == 3` and `commercial_use is False` (not Tier 2).
2. Same for licence strings `reviewed by committee` and `may be distributed under site terms`.
3. `classify(..., "MIT")`, `classify(..., "Apache 2.0")`, `classify(..., "BSD 3-Clause")`, `classify(..., "MIT-style")`, and `classify(..., "FreeBSD license")` each return `license_tier == 2`, `commercial_use is True`, `share_alike is False`, `attribution_required is True`.
3b. Negated grants do NOT return `commercial_use is True`; they fall through to the caution path (tier 3). Probe at minimum: `MIT for non-commercial use only`, `noncommercial MIT variant`, `MIT, commercial use prohibited`, `MIT; no commercial restrictions`.
4. Excluded self-check cases for AFOTEC, DAG (`defense acquisition guidebook` / `dod dag`), and CMU-SEI (`cmu` / `carnegie mellon` / `software engineering institute`) still return `excluded is True` with their current reasons; prior eight self-check rows still pass; SEBoK NC+SA assert still holds.
5. `python tools/vet_source.py --self-check` exits 0 and includes the new false-positive and true-grant probes.
6. A `build_pack` run with a non-Excluded title/publisher and `--license MIT` (tmp out-dir, fresh kebab slug, no tier overrides) exits 0 and writes PACK.yaml with `license_tier: 2` and `commercial_use: true`.
7. No new runtime dependencies; tools remain pure stdlib.
8. SOURCE-VETTING.md Tier 2 permissive bullet states boundary/token recognition of the MIT/Apache/BSD family tokens (Goal 4 edit applied).

## Research

- research: skipped (internal tool hardening; no external APIs, libraries, or version-sensitive choices)
