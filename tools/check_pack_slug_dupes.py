#!/usr/bin/env python3
# Copyright (c) 2026 JG Systems Consulting Ltd. - MIT License (see LICENSE).
# SPDX-License-Identifier: MIT
"""Advisory fleet checker: same-slug pack collisions across sibling repos.

Backlog uk-defence-knowledge-pack-elaboration-1. Not wired into CI (the
FLEET-CONVENTIONS gate constants stay pinned at five sites); run at release
time or on demand:

    python tooling/check_pack_slug_dupes.py            # auto-discover siblings
    python tooling/check_pack_slug_dupes.py --root <dir>   # explicit fleet root

Rule (docs/CROSS-PACK-BOUNDARIES.md): a UK defence publication has one content
owner. A sibling must not install a same-slug content copy. Exit codes:

- 0: no collisions (same slug may appear in one repo only; different slugs fine)
- 1: content-vs-content or content-vs-signpost same-slug collision (hard)
- 2: signpost-vs-signpost same slug in two repos (warning-grade, still reported)

A slug is a pack directory holding a SKILL.md; its kind comes from the
``kind:`` frontmatter line (content packs have no kind line, orchestrator and
signpost do). Slugs appearing in exactly one repo are never findings.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SECTOR_SUFFIX = "-knowledge-packs"


def classify(pack_dir: Path) -> str:
    skill = pack_dir / "SKILL.md"
    if not skill.is_file():
        return "unknown"
    m = re.search(r"^kind:\s*(signpost|orchestrator)\s*$", skill.read_text(encoding="utf-8", errors="ignore"), re.M)
    return m.group(1) if m else "content"


def discover_fleet(explicit: Path | None) -> list[Path]:
    if explicit is not None:
        roots = [explicit]
    else:
        home = Path(__file__).resolve().parent.parent  # this repo's root
        roots = sorted(p for p in home.parent.glob(f"*{SECTOR_SUFFIX}") if p.is_dir())
    repos: list[Path] = []
    for root in roots:
        packs = root / "packs"
        if packs.is_dir():
            repos.append(packs)
    return repos


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None, help="fleet root holding sibling sector repos (default: auto-discover beside this repo)")
    args = ap.parse_args()

    pack_roots = discover_fleet(args.root)
    if len(pack_roots) < 2:
        print(f"fleet discovery found {len(pack_roots)} sector repo(s); nothing to compare", file=sys.stderr)
        return 0

    slug_kinds: dict[str, list[tuple[str, str]]] = {}
    for packs in pack_roots:
        for pack_dir in sorted(p for p in packs.iterdir() if p.is_dir()):
            slug_kinds.setdefault(pack_dir.name, []).append((str(packs.parent), classify(pack_dir)))

    hard: list[str] = []
    warn: list[str] = []
    for slug in sorted(slug_kinds):
        hits = slug_kinds[slug]
        if len(hits) < 2:
            continue
        kinds = {k for _, k in hits}
        where = ", ".join(f"{repo} ({k})" for repo, k in hits)
        if "content" in kinds:
            hard.append(f"[dupes] slug '{slug}' ships as content in 2+ repos: {where}")
        elif kinds == {"signpost"}:
            warn.append(f"[dupes] slug '{slug}' is a signpost in 2+ repos (citation-only, but the install name still collides): {where}")
        else:
            warn.append(f"[dupes] slug '{slug}' present in 2+ repos (kinds: {where})")

    print(f"fleet: {len(pack_roots)} sector repos compared")
    for line in sorted(hard) + sorted(warn):
        print(line)
    if hard:
        print(f"RESULT: FAIL ({len(hard)} content collision(s), {len(warn)} warning(s))")
        return 1
    if warn:
        print(f"RESULT: WARN ({len(warn)} warning(s), no content collisions)")
        return 2
    print("RESULT: CLEAN (no same-slug collisions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
