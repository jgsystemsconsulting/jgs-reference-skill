#!/usr/bin/env python3
# Copyright (c) 2026 JG Systems Consulting Ltd. — MIT License (see ../LICENSE).
# SPDX-License-Identifier: MIT
#
# Adapted from jgs-se-knowledge-packs/tooling/build_pack.py (MIT). Improvement:
# the licence tier and PACK.yaml flags are no longer hand-typed — they are
# derived from tools/vet_source.classify(), and the scaffold HARD-STOPS on an
# Excluded source instead of trusting the operator to have checked.
"""
build_pack.py — vet a source, then scaffold a reference pack with provenance.

Deterministic, auditable half of the build. The judgement half (extraction +
per-chapter synthesis) is done by an agent following SKILL.md.

Usage:
    python tools/build_pack.py --slug nasa-se-handbook \
        --title "NASA Systems Engineering Handbook (SP-2016-6105 Rev 2)" \
        --publisher "NASA" --version "Rev 2 (2016)" \
        --license "Public Domain (US Government work)"

Tier / commercial_use / share_alike / attribution are inferred from the licence
(override with --tier etc. if you disagree — you must then justify in PACK.yaml).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vet_source import classify  # noqa: E402  (same-dir tool)

VALID_TIERS = {"1", "2", "3"}

PACK_YAML_TEMPLATE = """\
slug: {slug}
title: "{title}"
publisher: "{publisher}"
source_version: "{version}"
license: "{license}"
license_tier: {tier}
commercial_use: {commercial_use}
share_alike: {share_alike}
attribution_required: {attribution_required}
build:
  method: "reference-skill: vendored book-to-skill extraction + offset-mapped chapter synthesis"
  source_pages: 0
  chapters: 0
  built_on: "TODO"
notes: >
  TODO: record how the source licence's conditions (attribution / non-commercial /
  share-alike / trademark) are carried forward into this pack. Synthesised reference
  notes only; no long verbatim passages (verify with tools/check_overlap.py).
"""

LICENSE_STUB = """\
{slug} pack — content licence
{underline}

Derived from:
    {title}
    {publisher}, {version}

Source licence: {license}  (tier {tier} — see ../../docs/SOURCE-VETTING.md)

TODO: reproduce the source's full licence text / terms here. For public-domain
(US Government) works, state that and keep an attribution courtesy note. For CC
sources, reproduce the deed summary and the obligations carried forward.

This licence governs the CONTENT of this pack and is independent of the
repository's MIT licence (which covers tooling only).
"""


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--publisher", required=True)
    ap.add_argument("--version", default="")
    ap.add_argument("--license", required=True, help="exact source licence name")
    ap.add_argument("--out-dir", default="packs", help="where packs live (default: ./packs)")
    ap.add_argument("--tier", choices=sorted(VALID_TIERS), help="override inferred tier")
    ap.add_argument("--commercial-use", choices=["true", "false"])
    ap.add_argument("--share-alike", choices=["true", "false"])
    ap.add_argument("--attribution-required", choices=["true", "false"])
    ap.add_argument("--force", action="store_true", help="scaffold even if vetting warns")
    args = ap.parse_args(argv[1:])

    # --- the gate: vet before you build ---
    v = classify(args.title, args.publisher, args.license)
    if v["excluded"]:
        print(f"🔴 REFUSED — source is Excluded: {v['excluded_reason']}", file=sys.stderr)
        print("   This source is not redistributable. Use signpost mode (cite + point to "
              "the owner), do NOT build a pack.", file=sys.stderr)
        return 2
    for w in v["warnings"]:
        print(f"⚠  {w}", file=sys.stderr)
    if v["warnings"] and not args.force:
        print("   Re-run with --force once you've justified the above in PACK.yaml.", file=sys.stderr)
        return 2

    def b(x):  # bool -> yaml literal
        return str(x).lower()

    tier = args.tier or str(v["license_tier"])
    commercial = args.commercial_use or b(v["commercial_use"])
    share_alike = args.share_alike or b(v["share_alike"])
    attribution = args.attribution_required or b(v["attribution_required"])

    pack_dir = Path(args.out_dir) / args.slug
    if pack_dir.exists():
        print(f"ERROR: {pack_dir} already exists.", file=sys.stderr)
        return 1
    (pack_dir / "chapters").mkdir(parents=True)

    (pack_dir / "PACK.yaml").write_text(PACK_YAML_TEMPLATE.format(
        slug=args.slug, title=args.title, publisher=args.publisher, version=args.version,
        license=args.license, tier=tier, commercial_use=commercial,
        share_alike=share_alike, attribution_required=attribution), encoding="utf-8")
    (pack_dir / "LICENSE").write_text(LICENSE_STUB.format(
        slug=args.slug, underline="=" * (len(args.slug) + 24), title=args.title,
        publisher=args.publisher, version=args.version, license=args.license, tier=tier),
        encoding="utf-8")

    print(f"✅ Vetted Tier {tier} → created {pack_dir}/ with PACK.yaml + LICENSE stub + chapters/.")
    print("\nNext (agent-driven — see SKILL.md):")
    print("  1. Extract:   python scripts/extract.py <source> --mode technical")
    print("  2. Outline:   python tools/outline.py --source <full_text.txt> --out outline.json")
    print("  3. Generate chapters/chNN-*.md + glossary/patterns/cheatsheet + SKILL.md")
    print("  4. Overlap:   python tools/check_overlap.py --source <full_text.txt> --pack " + str(pack_dir))
    print("  5. Validate:  python tools/validate_pack.py " + str(pack_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
