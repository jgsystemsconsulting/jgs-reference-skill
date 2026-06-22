#!/usr/bin/env python3
# Copyright (c) 2026 JG Systems Consulting Ltd. — MIT License (see ../LICENSE).
# SPDX-License-Identifier: MIT
"""
outline.py — deterministic structure map of an extracted source (theme 4).

book-to-skill's large-book handling tells the agent to `grep` for chapter
headings ad hoc, which slices the wrong range when headings are irregular.
outline.py does it once, deterministically: it detects headings and emits exact
line + char offsets per section as JSON, so chapter generation reads precise
slices instead of guessing. Re-runnable and diff-able.

Usage:
    python tools/outline.py --source full_text.txt
    python tools/outline.py --source full_text.txt --out outline.json
    python tools/outline.py --self-check

Output: JSON list of {index, title, level, start_line, end_line, start_char,
end_char, word_count, est_tokens}.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

WORDS_PER_TOKEN = 0.75

# Heading patterns, most specific first. Each returns (level, title).
PATTERNS = [
    (re.compile(r"^\s*(chapter|appendix)\s+([0-9]+|[ivxlcdm]+)\b[.:)]?\s*(.*)$", re.I), "chapter"),
    (re.compile(r"^\s*(part|section)\s+([0-9]+|[ivxlcdm]+)\b[.:)]?\s*(.*)$", re.I), "part"),
    (re.compile(r"^(#{1,3})\s+(.*\S)\s*$"), "md"),                 # markdown headings
    (re.compile(r"^\s*(\d+(?:\.\d+){0,2})\s+([A-Z][^\n]{2,80})$"), "numbered"),  # 3.2 Title
]


def detect_headings(lines: list[str]) -> list[dict]:
    out = []
    for ln, raw in enumerate(lines):
        for pat, kind in PATTERNS:
            m = pat.match(raw)
            if not m:
                continue
            if kind == "md":
                level, title = len(m.group(1)), m.group(2).strip()
            elif kind == "numbered":
                level, title = m.group(1).count(".") + 1, raw.strip()
            else:
                level = 1 if kind == "chapter" else 2
                title = raw.strip()
            out.append({"line": ln, "level": level, "title": title})
            break
    return out


def build_outline(text: str) -> list[dict]:
    lines = text.splitlines()
    # char offset at the start of each line
    char_at = [0] * (len(lines) + 1)
    for i, l in enumerate(lines):
        char_at[i + 1] = char_at[i] + len(l) + 1  # +1 for the newline

    heads = detect_headings(lines)
    sections = []
    for idx, h in enumerate(heads):
        start_line = h["line"]
        end_line = heads[idx + 1]["line"] if idx + 1 < len(heads) else len(lines)
        body = "\n".join(lines[start_line:end_line])
        words = len(re.findall(r"\S+", body))
        sections.append({
            "index": idx,
            "title": h["title"][:120],
            "level": h["level"],
            "start_line": start_line,
            "end_line": end_line,
            "start_char": char_at[start_line],
            "end_char": char_at[end_line],
            "word_count": words,
            "est_tokens": round(words / WORDS_PER_TOKEN),
        })
    return sections


def _self_check() -> int:
    text = (
        "Front matter line.\n"
        "Chapter 1 Foundations\n"
        "Body of chapter one with several words here.\n"
        "Chapter 2 Architecture\n"
        "Body of chapter two.\n"
        "More chapter two text.\n"
        "Chapter 3 Verification\n"
        "Final body.\n"
    )
    o = build_outline(text)
    ok = (
        len(o) == 3
        and o[0]["start_line"] == 1 and o[0]["end_line"] == 3
        and o[1]["start_line"] == 3 and o[1]["end_line"] == 6
        and o[2]["start_line"] == 6
        and all(o[i]["end_line"] == o[i + 1]["start_line"] for i in range(len(o) - 1))
    )
    print("outline self-check:", "PASS" if ok else "FAIL")
    if not ok:
        print(json.dumps(o, indent=2))
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", help="extracted text (full_text.txt)")
    ap.add_argument("--out", help="write JSON here (default: stdout)")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv[1:])

    if args.self_check:
        return _self_check()
    if not args.source:
        ap.error("--source is required")

    text = Path(args.source).read_text(encoding="utf-8", errors="ignore")
    outline = build_outline(text)
    payload = json.dumps(outline, indent=2)
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(f"Wrote {len(outline)} section(s) to {args.out}")
    else:
        print(payload)
    if not outline:
        print("(no headings detected — pass --source a real extraction, or the source "
              "has no recognisable heading structure)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
