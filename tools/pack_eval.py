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

Exit codes (deliberate superset of the spec table: 2 also covers a pack path that is not a directory, 3 also covers missing SKILL.md — both fail-closed):
  0  routes grounded (full pack), signpost skip, or --self-check pass
  1  --self-check failure
  2  usage (--pack missing / bad args / pack path not a directory)
  3  full-pack structural index failure (missing Topic Index section, or
     section present with zero parseable entries; also missing SKILL.md
     on the full-pack path)
  4  at least one mis-route among evaluated entries
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


def _pack_kind(pack_dir: Path) -> str | None:
    """Flat `kind:` scalar from PACK.yaml, or None if missing/unreadable."""
    path = pack_dir / "PACK.yaml"
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    for line in text.splitlines():
        if not line or line[0] in " \t#":
            continue
        m = re.match(r"^kind:\s*(.*)$", line)
        if not m:
            continue
        val = m.group(1).strip().strip('"').strip("'")
        return val or None
    return None


def _has_ch_files(pack_dir: Path) -> bool:
    chapters = pack_dir / "chapters"
    return chapters.is_dir() and any(re.match(r"ch\d+", f.name) for f in chapters.glob("*.md"))


def _skill_has_topic_index_heading(pack_dir: Path) -> bool:
    skill = pack_dir / "SKILL.md"
    if not skill.is_file():
        return False
    try:
        body = skill.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return re.search(r"##\s*Topic Index\b", body, re.I) is not None


def is_signpost_pack(pack_dir: Path) -> bool:
    """True only when kind is signpost AND nothing smuggles a full pack.

    Spec: kind alone is not trusted. Chapters with chNN files, or a Topic
    Index heading in SKILL.md, force the full-pack path.
    """
    if _pack_kind(pack_dir) != "signpost":
        return False
    if _has_ch_files(pack_dir):
        return False
    if _skill_has_topic_index_heading(pack_dir):
        return False
    return True


def key_words(term: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", term.lower()) if w not in STOP and len(w) > 2]


def evaluate(pack_dir: Path) -> tuple[int, int, list[str], int | None]:
    """Return (passed, total, failures, structural_code).

    structural_code is 3 when the Topic Index section is missing or yields
    zero parseable entries; None when evaluation completed and the caller
    decides 0 vs 4 from failures.
    """
    skill_path = pack_dir / "SKILL.md"
    skill = skill_path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"##\s*Topic Index(.*?)(?:\n##\s|\Z)", skill, re.S | re.I)
    if not m:
        return 0, 0, [], 3
    region = m.group(1)

    chapter_text: dict[str, str] = {}
    chapters_dir = pack_dir / "chapters"
    if chapters_dir.is_dir():
        for ch in chapters_dir.glob("ch*.md"):
            cm = re.match(r"(ch\d+)", ch.name)
            if not cm:
                continue
            chapter_text[cm.group(1)] = ch.read_text(
                encoding="utf-8", errors="ignore"
            ).lower()

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
                failures.append(
                    f"{term!r} → {cid} (chapter never mentions the term)"
                )
            else:
                passed += 1
    if total == 0:
        return 0, 0, [], 3
    return passed, total, failures, None


def _self_check() -> int:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        # --- existing grounded + mis-route shape via evaluate ---
        pack = root / "grounded"
        (pack / "chapters").mkdir(parents=True)
        (pack / "chapters" / "ch01-x.md").write_text(
            "Traceability links requirements to tests.", encoding="utf-8"
        )
        (pack / "chapters" / "ch02-y.md").write_text(
            "Verification confirms the build is right.", encoding="utf-8"
        )
        (pack / "SKILL.md").write_text(
            "## Topic Index\n"
            "- **Traceability** → ch01\n"
            "- **Verification** → ch02\n"
            "- **Wrongness** → ch01\n",
            encoding="utf-8",
        )
        passed, total, fails, structural = evaluate(pack)
        if not (
            structural is None
            and total == 3
            and passed == 2
            and any("Wrongness" in f for f in fails)
        ):
            failures.append(
                f"grounded probe: passed={passed} total={total} "
                f"structural={structural} fails={fails}"
            )
        # mis-route exit 4 through main
        rc = main(["pack_eval", "--pack", str(pack)])
        if rc != 4:
            failures.append(f"mis-route main exit want 4 got {rc}")

        # --- missing Topic Index section → 3 ---
        no_idx = root / "no-index"
        (no_idx / "chapters").mkdir(parents=True)
        (no_idx / "chapters" / "ch01-x.md").write_text(
            "body", encoding="utf-8"
        )
        (no_idx / "SKILL.md").write_text(
            "# Pack\n\nNo index here.\n", encoding="utf-8"
        )
        rc = main(["pack_eval", "--pack", str(no_idx)])
        if rc != 3:
            failures.append(f"missing-section want 3 got {rc}")

        # --- section present, zero parseable → 3 ---
        empty_idx = root / "empty-index"
        (empty_idx / "chapters").mkdir(parents=True)
        (empty_idx / "chapters" / "ch01-x.md").write_text(
            "body", encoding="utf-8"
        )
        (empty_idx / "SKILL.md").write_text(
            "## Topic Index\n\nNot a real entry.\n- plain bullet\n",
            encoding="utf-8",
        )
        rc = main(["pack_eval", "--pack", str(empty_idx)])
        if rc != 3:
            failures.append(f"zero-parseable want 3 got {rc}")

        # --- true signpost short-circuit → 0 ---
        sp = root / "signpost-ok"
        sp.mkdir()
        (sp / "PACK.yaml").write_text(
            'kind: signpost\nslug: "signpost-ok"\n', encoding="utf-8"
        )
        (sp / "SKILL.md").write_text(
            "# Citation only\n\nNo topic index.\n", encoding="utf-8"
        )
        rc = main(["pack_eval", "--pack", str(sp)])
        if rc != 0:
            failures.append(f"signpost skip want 0 got {rc}")

        # --- labelled full pack (smuggling) → not 0 ---
        # kind: signpost BUT chapters present → full-pack rules → 3 (no index)
        smug = root / "smuggle-chapters"
        (smug / "chapters").mkdir(parents=True)
        (smug / "chapters" / "ch01-x.md").write_text(
            "body", encoding="utf-8"
        )
        (smug / "PACK.yaml").write_text(
            "kind: signpost\n", encoding="utf-8"
        )
        (smug / "SKILL.md").write_text(
            "# Pretend signpost\n", encoding="utf-8"
        )
        rc = main(["pack_eval", "--pack", str(smug)])
        if rc == 0:
            failures.append(
                f"smuggle-chapters must not exit 0, got {rc}"
            )

        # kind: signpost + Topic Index heading, no chapters → full-pack → 3
        smug2 = root / "smuggle-index"
        smug2.mkdir()
        (smug2 / "PACK.yaml").write_text(
            "kind: signpost\n", encoding="utf-8"
        )
        (smug2 / "SKILL.md").write_text(
            "## Topic Index\n\n- not parseable\n", encoding="utf-8"
        )
        rc = main(["pack_eval", "--pack", str(smug2)])
        if rc == 0:
            failures.append(
                f"smuggle-index must not exit 0, got {rc}"
            )

        # --- valid full pack still 0 ---
        good = root / "good"
        (good / "chapters").mkdir(parents=True)
        (good / "chapters" / "ch01-x.md").write_text(
            "Traceability links requirements to tests.", encoding="utf-8"
        )
        (good / "SKILL.md").write_text(
            "## Topic Index\n- **Traceability** → ch01\n", encoding="utf-8"
        )
        rc = main(["pack_eval", "--pack", str(good)])
        if rc != 0:
            failures.append(f"valid pack want 0 got {rc}")

    ok = not failures
    print("pack_eval self-check:", "PASS" if ok else "FAIL")
    for line in failures:
        print(f"  {line}")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--pack")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv[1:])
    if args.self_check:
        return _self_check()
    if not args.pack:
        ap.error("--pack is required")

    pack = Path(args.pack)
    if not pack.is_dir():
        print(f"ERROR: pack directory not found: {pack}", file=sys.stderr)
        return 2

    if is_signpost_pack(pack):
        print(
            "signpost pack: index-truth eval does not apply; skipping."
        )
        return 0

    skill_path = pack / "SKILL.md"
    if not skill_path.is_file():
        print("ERROR: SKILL.md is missing.", file=sys.stderr)
        return 3

    try:
        passed, total, fails, structural = evaluate(pack)
    except OSError as exc:
        print(f"ERROR: could not read pack files: {exc}", file=sys.stderr)
        return 3

    if structural == 3:
        # Distinguish missing section vs zero-parseable for the operator.
        skill = skill_path.read_text(encoding="utf-8", errors="ignore")
        if not re.search(r"##\s*Topic Index\b", skill, re.I):
            print(
                "ERROR: SKILL.md has no ## Topic Index section.",
                file=sys.stderr,
            )
        else:
            print(
                "ERROR: Topic Index has no parseable entries to evaluate.",
                file=sys.stderr,
            )
        return 3

    for f in fails:
        print(f"⚠  mis-route: {f}")
    print(f"\n{passed}/{total} topic-index routes grounded in their chapter.")
    return 4 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
