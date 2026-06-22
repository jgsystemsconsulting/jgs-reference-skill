<!--
Copyright (c) 2026 JG Systems Consulting Ltd. — MIT License (see ../LICENSE).
Adapted from jgs-se-knowledge-packs/docs/SOURCE-VETTING.md (MIT). This rubric is
encoded in tools/vet_source.py — keep the two in sync.
-->

# Source Vetting

**No pack is built unless its source clears this rubric.** A reference pack
*reproduces and transforms* a source into new published files — that is
redistribution plus derivative work, and it needs an actual grant.

> **"Free to download" is not "free to redistribute."**

`tools/vet_source.py` classifies a source mechanically and **hard-stops on
Excluded**. The tiers:

### 🟢 Tier 1 — Public domain (maximum freedom)
No copyright, or explicit public-domain dedication. Reproduce, transform,
redistribute freely; attribution is courtesy.
- **US Government works** — not copyrightable in the US (17 U.S.C. § 105): NASA,
  NIST, US DoD, FAA, GAO. Look for **Distribution Statement A**.
- CC0 / explicit public-domain dedication.
- *Caveat:* a US-gov work may quote third-party (ISO/IEC/IEEE) text — reproduce
  **none** of it. `vet_source.py` warns on this.

### 🟡 Tier 2 — Open licence (shareable with conditions)
A licence granting redistribution and derivatives. The pack **carries the
conditions forward**:
- **Creative Commons** BY / BY-SA / BY-NC / BY-NC-SA. NC → `commercial_use: false`;
  SA → pack content under the source's licence (not this repo's MIT); BY →
  attribution in `LICENSE` + `PACK.yaml`.
- Permissive licences (MIT/Apache/BSD) where they cover the text.

### 🟠 Tier 3 — Caution (justify in PACK.yaml)
- **No-derivatives** (CC BY-ND): a pack transforms the source, which ND forbids.
  Prefer signpost; package only with written justification.
- **"Freely available", no stated licence.** Treat as Excluded until a real grant
  is confirmed.

### 🔴 Excluded — read-and-cite only (hard stop → signpost)
You may read and cite these; you may **not** package them.

| Source | Why |
|---|---|
| **ISO / IEC / IEEE** (15288, 42010, 12207…) | Paywalled, all-rights-reserved. |
| **INCOSE SE Handbook / Vision** | Copyrighted (Wiley). |
| **SWEBOK v4** | "May not alter the text"; individual non-commercial only. |
| **MITRE SE Guide** | All rights reserved. |
| **Open Group TOGAF / ArchiMate** | Evaluation/member licence. |
| **PMI PMBOK** | PMI copyright. |
| **OMG specs** (UML, SysML, BPMN, UAF, MOF, XMI, OCL, DDS…) | OMG licence is informational-use-only: no network posting, no modification. |

> If *you* are licensed to read one of these (e.g. an employer ISO seat), that
> licence is **yours**, not the pack's. Build for private use if you must; do not
> publish the pack. Excluded sources become **signposts** — cite + point to the owner.

## Checklist (before publishing a pack)

1. [ ] Source document, version, publisher identified.
2. [ ] Licence statement found **in the source itself**.
3. [ ] `vet_source.py` run → tier assigned, not Excluded.
4. [ ] Tier 2: NC / SA / BY conditions recorded in `PACK.yaml`.
5. [ ] Tier 3: written justification in `PACK.yaml` `notes`.
6. [ ] `LICENSE` reproduces the source's terms.
7. [ ] `check_overlap.py` clean — no verbatim passages.
8. [ ] No source-material URL published (attribution is textual).
