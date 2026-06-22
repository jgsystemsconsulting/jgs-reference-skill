#!/usr/bin/env python3
# Copyright (c) 2026 JG Systems Consulting Ltd. — MIT License (see ../LICENSE).
# SPDX-License-Identifier: MIT
"""
vet_source.py — licence-vetting GATE for jgs-reference-skill (improvement theme 1).

book-to-skill has no licence awareness: it will happily transform a paywalled
ISO standard into a published skill. jgs-reference-skill refuses to. This script
classifies a source into Tier 1 / 2 / 3 / Excluded *before* any extraction, and
hard-stops (exit 2) on Excluded sources — routing them to signpost mode instead.

It encodes the rubric in docs/SOURCE-VETTING.md as code, and emits the
PACK.yaml field hints (license_tier, commercial_use, share_alike,
attribution_required) so provenance is filled from the verdict, not by hand.

Usage:
    python tools/vet_source.py --title "NASA SE Handbook" --publisher "NASA" \
        --license "Public Domain (US Government work)"
    python tools/vet_source.py --title "SysML" --publisher "Object Management Group"
    python tools/vet_source.py --self-check          # run built-in assertions

Exit codes: 0 = packageable (Tier 1/2/3), 2 = Excluded (hard stop), 1 = usage error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

# Force UTF-8 stdout so verdict glyphs (🔴/✅/⚠) don't raise UnicodeEncodeError on
# legacy Windows code pages (cp1252/cp936). Mirrors the vendored extractor.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# Sources that are read-and-cite-only — never packageable. Matched as substrings
# against "<title> | <publisher>" lowercased. Keep in sync with SOURCE-VETTING.md.
EXCLUDED = {
    "iso": "ISO standards are paywalled / all-rights-reserved",
    "iec ": "IEC standards are paywalled / all-rights-reserved",
    "ieee": "IEEE standards/SWEBOK are licensed per-user, no redistribution grant",
    "incose": "INCOSE handbooks/vision are copyrighted (Wiley), not redistributable",
    "swebok": "SWEBOK forbids alteration; individual non-commercial only",
    "mitre": "MITRE SE Guide is all-rights-reserved",
    "object management group": "OMG spec licence is informational-use-only (no posting, no modification)",
    "omg": "OMG spec licence is informational-use-only (no posting, no modification)",
    "open group": "TOGAF/ArchiMate are evaluation/member-licensed, not redistributable",
    "togaf": "TOGAF is evaluation/member-licensed",
    "archimate": "ArchiMate is evaluation/member-licensed",
    "pmbok": "PMBOK is PMI-copyrighted",
    "project management institute": "PMI material is copyrighted",
    "wiley": "Wiley-published works are copyrighted",
}

# US-government / public-domain publisher signals → Tier 1.
US_GOV = ("nasa", "nist", "department of defense", "dod", "ousd", "faa", "gao",
          "u.s. ", "us government", "u.s. government", "federal aviation",
          "department of ", "army", "navy", "air force", "defense acquisition")

PD_LICENSE = ("public domain", "17 u.s.c", "us government work", "u.s. government work",
              "distribution statement a", "distribution a", "cc0", "publicdomain")


def classify(title: str, publisher: str, license_str: str) -> dict:
    """Return a verdict dict. `excluded` True means hard-stop."""
    hay = f"{title} | {publisher}".lower()
    lic = (license_str or "").lower()

    # 1) Excluded wins over everything — a paywalled body publishing a "free" PDF
    #    is still not redistributable.
    for kw, reason in EXCLUDED.items():
        if kw in hay:
            return _verdict(excluded=True, reason=reason, tier=None)

    # 2) Public domain / US-gov → Tier 1 (maximum freedom).
    if any(k in lic for k in PD_LICENSE) or any(k in hay for k in US_GOV):
        warn = []
        if any(k in hay for k in ("nist", "ousd", "dod")):
            warn.append("US-gov work may quote third-party (e.g. ISO/IEC/IEEE) "
                        "text — reproduce none of it; verify before publishing.")
        return _verdict(tier=1, commercial_use=True, share_alike=False,
                        attribution_required=False, warnings=warn)

    # 3) Creative Commons / permissive → Tier 2, carrying conditions forward.
    cc = re.search(r"cc[\s_-]*by((?:[\s_-]*(?:nc|sa|nd))*)", lic)
    if cc:
        comps = set(re.findall(r"nc|sa|nd", cc.group(1)))
        if "nd" in comps:
            return _verdict(tier=3, commercial_use="nc" not in comps, share_alike=False,
                            attribution_required=True,
                            warnings=["No-Derivatives (ND): a pack transforms the source, "
                                      "which ND forbids. Prefer signpost; package only with "
                                      "written justification in PACK.yaml."])
        return _verdict(tier=2, commercial_use="nc" not in comps, share_alike="sa" in comps,
                        attribution_required=True)
    if any(k in lic for k in ("mit", "apache", "bsd")):
        return _verdict(tier=2, commercial_use=True, share_alike=False,
                        attribution_required=True)

    # 4) Anything else — unclear grant. "Freely available" is not a licence.
    return _verdict(tier=3, commercial_use=False, share_alike=False,
                    attribution_required=True,
                    warnings=["No recognised redistribution grant found. 'Free to "
                              "download' != 'free to redistribute'. Treat as Excluded "
                              "until a real grant is confirmed, or use signpost mode."])


def _verdict(tier, excluded=False, reason="", commercial_use=False,
             share_alike=False, attribution_required=True, warnings=None) -> dict:
    return {
        "excluded": excluded,
        "excluded_reason": reason,
        "license_tier": tier,
        "commercial_use": commercial_use,
        "share_alike": share_alike,
        "attribution_required": attribution_required,
        "warnings": warnings or [],
        "recommended_mode": "signpost" if excluded else "pack",
    }


def _self_check() -> int:
    cases = [
        # (title, publisher, license, expect_excluded, expect_tier)
        ("ISO/IEC/IEEE 15288", "ISO", "", True, None),
        ("SysML v2", "Object Management Group", "OMG Specification License", True, None),
        ("INCOSE SE Handbook", "Wiley", "", True, None),
        ("SE Handbook", "NASA", "Public Domain (US Government work)", False, 1),
        ("DoD SE Guidebook", "OUSD R&E", "Distribution A", False, 1),
        ("SEBoK", "BKCASE / Stevens", "CC BY-NC-SA 3.0", False, 2),
        ("Some Guide", "Author", "CC BY-ND 4.0", False, 3),
        ("Mystery Doc", "Random Blog", "freely available", False, 3),
    ]
    ok = True
    for title, pub, lic, exp_excl, exp_tier in cases:
        v = classify(title, pub, lic)
        if v["excluded"] != exp_excl or v["license_tier"] != exp_tier:
            print(f"FAIL: {title!r} -> {v['excluded']}/{v['license_tier']} "
                  f"(expected {exp_excl}/{exp_tier})")
            ok = False
    # NC + SA must propagate
    sebok = classify("SEBoK", "Stevens", "CC BY-NC-SA 3.0")
    assert sebok["commercial_use"] is False and sebok["share_alike"] is True, sebok
    print("vet_source self-check:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--title", default="")
    ap.add_argument("--publisher", default="")
    ap.add_argument("--license", default="")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON only")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv[1:])

    if args.self_check:
        return _self_check()
    if not (args.title or args.publisher):
        ap.error("provide --title and/or --publisher (and --license if known)")

    v = classify(args.title, args.publisher, args.license)
    if args.json:
        print(json.dumps(v, indent=2))
    else:
        if v["excluded"]:
            print(f"🔴 EXCLUDED — {v['excluded_reason']}")
            print("   → Do NOT package. Use signpost mode (cite + point to the owner).")
        else:
            print(f"✅ Tier {v['license_tier']} — packageable as a {v['recommended_mode']}")
            print(f"   commercial_use: {str(v['commercial_use']).lower()}  "
                  f"share_alike: {str(v['share_alike']).lower()}  "
                  f"attribution_required: {str(v['attribution_required']).lower()}")
        for w in v["warnings"]:
            print(f"   ⚠  {w}")
    return 2 if v["excluded"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
