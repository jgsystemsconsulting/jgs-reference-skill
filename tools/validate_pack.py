#!/usr/bin/env python3
# Copyright (c) 2026 JG Systems Consulting Ltd. — MIT License (see ../LICENSE).
# SPDX-License-Identifier: MIT
#
# Adapted from jgs-se-knowledge-packs/tooling/validate_pack.py (MIT), with one
# improvement folded in: `kind: signpost` packs are validated against a reduced
# rubric (no chapters/ required) instead of failing — the signpost-exemption
# logic that previously lived only in the release checker.
"""
validate_pack.py — structural + licence validator for a reference pack.

Usage:
    python tools/validate_pack.py packs/<slug>
    python tools/validate_pack.py --all          # every pack under ./packs
    python tools/validate_pack.py --self-check

Checks (see docs/PACK-SPEC.md and docs/SOURCE-VETTING.md):
  - required files present: SKILL.md, PACK.yaml, LICENSE, chapters/ with >=1 chapter
    (signpost packs: SKILL.md + PACK.yaml only)
  - SKILL.md has YAML frontmatter with name + description; name matches folder slug
  - every chapters/chNN-*.md link in SKILL.md resolves to a real file
  - PACK.yaml mandatory fields filled; license_tier in {1,2,3}

stdlib only. Exit 0 = all passed, 1 = a failure, 2 = usage error.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

REQUIRED_PACK_FIELDS = ("slug", "title", "publisher", "license", "license_tier", "commercial_use")
VALID_TIERS = {"1", "2", "3"}


def parse_simple_yaml(text: str) -> dict:
    """Flat top-level `key: value` scalars only — enough to check mandatory fields."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        if not line or line[0] in " \t#":
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in (">", "|", ""):
            continue
        out[key] = val.strip().strip('"').strip("'")
    return out


def check_pack(pack_dir: Path) -> list[str]:
    errors: list[str] = []
    slug = pack_dir.name
    skill = pack_dir / "SKILL.md"
    pack_yaml = pack_dir / "PACK.yaml"

    meta = parse_simple_yaml(pack_yaml.read_text(encoding="utf-8")) if pack_yaml.is_file() else {}
    is_signpost = meta.get("kind") == "signpost"

    # --- required files ---
    if not skill.is_file():
        errors.append("missing SKILL.md")
    if not pack_yaml.is_file():
        errors.append("missing PACK.yaml")
    if not is_signpost:
        if not (pack_dir / "LICENSE").is_file():
            errors.append("missing LICENSE (must reproduce the source's terms)")
        chapters = pack_dir / "chapters"
        if not chapters.is_dir():
            errors.append("missing chapters/ directory")
        elif not sorted(chapters.glob("ch*.md")):
            errors.append("chapters/ contains no chNN-*.md files")

    # --- SKILL.md frontmatter + chapter links ---
    if skill.is_file():
        body = skill.read_text(encoding="utf-8")
        fm = re.match(r"^---\s*\n(.*?)\n---\s*\n", body, re.S)
        if not fm:
            errors.append("SKILL.md has no YAML frontmatter block")
        else:
            front = fm.group(1)
            name_m = re.search(r"^name:\s*(.+)$", front, re.M)
            if not name_m:
                errors.append("SKILL.md frontmatter missing 'name'")
            elif name_m.group(1).strip().strip('"').strip("'") != slug:
                errors.append(f"SKILL.md name '{name_m.group(1).strip()}' != folder slug '{slug}'")
            if not re.search(r"^description:\s*\S", front, re.M):
                errors.append("SKILL.md frontmatter missing 'description'")
        for link in re.findall(r"\((chapters/ch[0-9]{2}-[^)]+\.md)\)", body):
            if not (pack_dir / link).is_file():
                errors.append(f"SKILL.md links a missing chapter file: {link}")

    # --- PACK.yaml mandatory fields + tier ---
    if pack_yaml.is_file():
        for field in REQUIRED_PACK_FIELDS:
            if not meta.get(field):
                errors.append(f"PACK.yaml missing required field: {field}")
        tier = meta.get("license_tier", "")
        if tier and tier not in VALID_TIERS:
            errors.append(f"PACK.yaml license_tier='{tier}' invalid — must be 1, 2, or 3")
        if meta.get("slug") and meta["slug"] != slug:
            errors.append(f"PACK.yaml slug '{meta['slug']}' != folder name '{slug}'")

    return errors


def _self_check() -> int:
    with tempfile.TemporaryDirectory() as td:
        pack = Path(td) / "demo-pack"
        (pack / "chapters").mkdir(parents=True)
        (pack / "chapters" / "ch01-intro.md").write_text("# Chapter 1\n", encoding="utf-8")
        (pack / "SKILL.md").write_text(
            "---\nname: demo-pack\ndescription: demo. Thin on everything.\n---\n"
            "## Chapter Index\n| 1 | x | [ch01](chapters/ch01-intro.md) |\n", encoding="utf-8")
        (pack / "LICENSE").write_text("Public domain.\n", encoding="utf-8")
        (pack / "PACK.yaml").write_text(
            'slug: demo-pack\ntitle: "X"\npublisher: "Y"\nlicense: "Public Domain"\n'
            "license_tier: 1\ncommercial_use: true\n", encoding="utf-8")
        clean = check_pack(pack)
        # break it: wrong tier + missing chapter link target
        (pack / "PACK.yaml").write_text(
            'slug: demo-pack\ntitle: "X"\npublisher: "Y"\nlicense: "X"\n'
            "license_tier: 9\ncommercial_use: true\n", encoding="utf-8")
        broken = check_pack(pack)
    ok = (clean == []) and any("license_tier" in e for e in broken)
    print("validate_pack self-check:", "PASS" if ok else "FAIL")
    if not ok:
        print(" clean:", clean, "\n broken:", broken)
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    args = argv[1:]
    if "--self-check" in args:
        return _self_check()
    cwd = Path.cwd()
    if "--all" in args or not args:
        base = cwd / "packs"
        packs = sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []
    else:
        packs = [Path(a).resolve() for a in args]
    if not packs:
        print("No packs found to validate (looked in ./packs).")
        return 0

    total_fail = 0
    for pack in packs:
        errs = check_pack(pack)
        if errs:
            total_fail += 1
            print(f"FAIL  {pack.name}")
            for e in errs:
                print(f"        - {e}")
        else:
            print(f"PASS  {pack.name}")
    print(f"\n{len(packs) - total_fail}/{len(packs)} pack(s) passed.")
    return 1 if total_fail else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
