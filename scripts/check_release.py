#!/usr/bin/env python3
# Copyright (c) 2026 JG Systems Consulting Ltd. See LICENSE.
# SPDX-License-Identifier: MIT
"""Release gate (RR-B-15): required files, forbidden content, headers
present on first-party .py files. Exits non-zero on any failure.

Complements (does not replace) validate.yml's existing content-integrity,
SKILL.md frontmatter, and version-consistency steps.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

REQUIRED = [
    "LICENSE", "COPYRIGHT", "NOTICE", "README.md", "CHANGELOG.md",
    "SECURITY.md", "CITATION.cff", "RELEASE-INFO.txt", "SKILL.md",
    "docs/index.html",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
]

FORBIDDEN_CONTENT = [
    re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
    re.compile(r"CONFIDENTIAL"),
]


def _tracked_py() -> list[pathlib.Path]:
    import subprocess
    out = subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout
    files = [ROOT / p for p in out.splitlines()]
    vendor_dirs = {p.parent for p in ROOT.rglob("LICENSE.upstream.md")}
    return [p for p in files if not any(p == d or d in p.parents for d in vendor_dirs)]


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"required file missing: {rel}")

    for path in ROOT.rglob("*"):
        rel_parts = path.relative_to(ROOT).parts
        if not path.is_file() or ".git" in path.parts:
            continue
        if rel_parts[:1] == (".github",) or rel_parts == ("scripts", "check_release.py"):
            continue  # legitimately define these sentinels as their own grep targets
        if path.suffix.lower() not in {".py", ".md", ".txt", ".yml", ".yaml", ".json", ".cff", ".html"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in FORBIDDEN_CONTENT:
            if pat.search(text):
                errors.append(f"forbidden content ({pat.pattern}) in {path.relative_to(ROOT)}")

    for path in _tracked_py():
        head = path.read_text(encoding="utf-8", errors="ignore")[:600]
        rel = path.relative_to(ROOT)
        if "Copyright (c)" not in head:
            errors.append(f"missing licence header: {rel}")
        if "SPDX-License-Identifier" not in head:
            errors.append(f"missing SPDX identifier: {rel}")

    if errors:
        for e in errors:
            print(f"::error::{e}")
        print(f"FAILED: {len(errors)} issue(s).")
        return 1

    print("Release gate: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
