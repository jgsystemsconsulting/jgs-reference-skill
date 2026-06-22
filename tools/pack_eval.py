#!/usr/bin/env python3
# Copyright (c) 2026 JG Systems Consulting Ltd. — MIT License (see ../LICENSE).
# SPDX-License-Identifier: MIT
"""
pack_eval.py — does the pack's index tell the truth? (improvement theme 4).

A deliberately light, mechanical retrieval check (no LLM, no harness to maintain).
For every `- **Term** → chNN[, chNN]` line in SKILL.md's Topic Index it asserts:
  1. each referenced chapter file exists, and
  2. the term's key words actually appear in that chapter.
A pack that indexes a term to a chapter that doesn't mention it will mis-route a
query — this catches that before release.

Usage:
    python tools/pack_eval.py --pack packs/<slug>
    python tools/pack_eval.py --self-check

Exit 0 = all index entries grounded, 4 = at least one mis-route, 2 = usage error.
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

STOP = {"the", "a", "an", "of", "and", "or", "to", "in", "for", "on", "with", "vs"}
TOPIC_LINE = re.compile(r"^\s*[-*]\s*\*\*(.+?)\*\*\s*(?:→|->|:)\s*(.+)$")


def key_words(term: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", term.lower()) if w not in STOP and len(w) > 2]


def evaluate(pack_dir: Path) -> tuple[int, int, list[str]]:
    skill = (pack_dir / "SKILL.md").read_text(encoding="utf-8", errors="ignore")
    # restrict to the Topic Index section if present
    m = re.search(r"##\s*Topic Index(.*?)(?:\n##\s|\Z)", skill, re.S | re.I)
    region = m.group(1) if m else skill

    chapter_text: dict[str, str] = {}
    for ch in (pack_dir / "chapters").glob("ch*.md"):
        cid = re.match(r"(ch\d+)", ch.name).group(1)
        chapter_text[cid] = ch.read_text(encoding="utf-8", errors="ignore").lower()

    passed = total = 0
    failures: list[str] = []
    for line in region.splitlines():
        lm = TOPIC_LINE.match(line)
        if not lm:
            continue
        term, refs = lm.group(1), re.findall(r"ch\d+", lm.group(2).lower())
        if not refs:
            continue
        kws = key_words(term)
        for cid in refs:
            total += 1
            body = chapter_text.get(cid)
            if body is None:
                failures.append(f"{term!r} → {cid} (no such chapter file)")
            elif kws and not any(w in body for w in kws):
                failures.append(f"{term!r} → {cid} (chapter never mentions the term)")
            else:
                passed += 1
    return passed, total, failures


def _self_check() -> int:
    with tempfile.TemporaryDirectory() as td:
        pack = Path(td) / "p"
        (pack / "chapters").mkdir(parents=True)
        (pack / "chapters" / "ch01-x.md").write_text(
            "Traceability links requirements to tests.", encoding="utf-8")
        (pack / "chapters" / "ch02-y.md").write_text(
            "Verification confirms the build is right.", encoding="utf-8")
        (pack / "SKILL.md").write_text(
            "## Topic Index\n- **Traceability** → ch01\n- **Verification** → ch02\n"
            "- **Wrongness** → ch01\n", encoding="utf-8")
        passed, total, fails = evaluate(pack)
    ok = total == 3 and passed == 2 and any("Wrongness" in f for f in fails)
    print("pack_eval self-check:", "PASS" if ok else "FAIL")
    if not ok:
        print(f"  passed={passed} total={total} fails={fails}")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv[1:])
    if args.self_check:
        return _self_check()
    if not args.pack:
        ap.error("--pack is required")

    passed, total, fails = evaluate(Path(args.pack))
    if total == 0:
        print("No Topic Index entries found to evaluate.")
        return 0
    for f in fails:
        print(f"⚠  mis-route: {f}")
    print(f"\n{passed}/{total} topic-index routes grounded in their chapter.")
    return 4 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
