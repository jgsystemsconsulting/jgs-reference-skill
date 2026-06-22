#!/usr/bin/env python3
# Copyright (c) 2026 JG Systems Consulting Ltd. — MIT License (see ../LICENSE).
# SPDX-License-Identifier: MIT
"""
check_overlap.py — verbatim-overlap detector (improvement themes 1 + 2).

book-to-skill *says* "never copy raw book text" as a rule but never verifies it.
reference-skill verifies it mechanically: it n-gram-shingles the source text and
flags any run of >= N consecutive words in the generated pack that appears
verbatim in the source. This automates the kind of by-hand fix where a verbatim
source phrase had to be paraphrased before publishing.

It is both a licence-safety gate (no long verbatim passages of a copyrighted
source) and a quality gate (a pack must synthesise, not photocopy).

Usage:
    python tools/check_overlap.py --source full_text.txt --pack packs/<slug>
    python tools/check_overlap.py --source src.txt --generated a.md b.md -n 10
    python tools/check_overlap.py --self-check

Exit codes: 0 = clean, 3 = verbatim overlap found, 1 = usage error.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Force UTF-8 stdout so report glyphs (⚠/🔴/✅) survive legacy Windows code pages.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

_WORD = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def shingles(tokens: list[str], n: int) -> set[tuple]:
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def find_overlaps(source_text: str, gen_text: str, n: int, max_hits: int = 20) -> list[str]:
    """Return up to max_hits verbatim n-gram runs shared by source and generated text."""
    src = shingles(tokenize(source_text), n)
    if not src:
        return []
    gtok = tokenize(gen_text)
    hits, seen = [], set()
    i = 0
    while i <= len(gtok) - n:
        gram = tuple(gtok[i:i + n])
        if gram in src:
            # Extend the match as far as it stays verbatim, so we report the full run.
            j = i + n
            while j < len(gtok) and tuple(gtok[j - n + 1:j + 1]) in src:
                j += 1
            run = " ".join(gtok[i:j])
            if run not in seen:
                seen.add(run)
                hits.append(run)
                if len(hits) >= max_hits:
                    break
            i = j
        else:
            i += 1
    return hits


def _gen_files(pack_dir: Path) -> list[Path]:
    files = list(pack_dir.glob("chapters/ch*.md"))
    for name in ("SKILL.md", "glossary.md", "patterns.md", "cheatsheet.md"):
        p = pack_dir / name
        if p.is_file():
            files.append(p)
    return files


def _self_check() -> int:
    source = ("The systems engineering process transforms stakeholder needs into a "
              "verified solution through iterative analysis design and integration "
              "across the entire life cycle of the system of interest.")
    copied = "needs into a verified solution through iterative analysis design and integration across"
    paraphrase = ("Reference-depth notes restate ideas in fresh wording so nothing is "
                  "lifted word for word from the original document at all.")
    hits_bad = find_overlaps(source, copied, n=8)
    hits_good = find_overlaps(source, paraphrase, n=8)
    ok = bool(hits_bad) and not hits_good
    print("check_overlap self-check:", "PASS" if ok else "FAIL")
    if not ok:
        print("  copied->", hits_bad, "| paraphrase->", hits_good)
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", help="extracted source text (full_text.txt)")
    ap.add_argument("--pack", help="generated pack directory")
    ap.add_argument("--generated", nargs="*", default=[], help="specific generated files")
    ap.add_argument("-n", type=int, default=12, help="verbatim run length to flag (words)")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv[1:])

    if args.self_check:
        return _self_check()
    if not args.source or not (args.pack or args.generated):
        ap.error("need --source and one of --pack / --generated")

    source_text = Path(args.source).read_text(encoding="utf-8", errors="ignore")
    targets = [Path(g) for g in args.generated]
    if args.pack:
        targets += _gen_files(Path(args.pack))

    total = 0
    for f in targets:
        if not f.is_file():
            continue
        hits = find_overlaps(source_text, f.read_text(encoding="utf-8", errors="ignore"), args.n)
        if hits:
            total += len(hits)
            print(f"⚠  {f}: {len(hits)} verbatim run(s) >= {args.n} words")
            for h in hits[:5]:
                print(f'      "{h[:120]}{"…" if len(h) > 120 else ""}"')

    if total:
        print(f"\n🔴 {total} verbatim overlap(s) found — paraphrase before publishing.")
        return 3
    print(f"✅ No verbatim run >= {args.n} words shared with the source.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
