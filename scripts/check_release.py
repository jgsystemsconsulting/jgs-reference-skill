#!/usr/bin/env python3
# Copyright (c) 2026 JG Systems Consulting Ltd. See LICENSE.
# SPDX-License-Identifier: MIT
"""Release gate (RR-B-15): required files, forbidden content, headers
present on first-party .py files, and Source-Commit resolves to an
ancestor of HEAD. Exits non-zero on any failure.

Complements (does not replace) validate.yml's existing content-integrity,
SKILL.md frontmatter, and version-consistency steps.

Source-Commit ancestor check walks local git history. Shallow clones may
false-fail; run `git fetch --unshallow` (or deepen) before relying on this
gate locally. CI integrity checkout sets fetch-depth: 0.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

REQUIRED = [
    "LICENSE", "COPYRIGHT", "NOTICE", "README.md", "CHANGELOG.md",
    "SECURITY.md", "CITATION.cff", "RELEASE-INFO.txt", "SKILL.md",
    "docs/index.html",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
]

# Assembled from parts so this file never self-matches the workflow's
# leak-sentinel grep (validate.yml), which excludes only .git/ and .github/.
# The variable name also avoids the contiguous word: the grep is -i.
_SENTINEL = "CONFID" + "ENTIAL"

FORBIDDEN_CONTENT = [
    re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
    re.compile(_SENTINEL),
]

_SOURCE_COMMIT_LINE = re.compile(r"^Source-Commit:\s*(\S+)\s*$", re.M)
_SOURCE_COMMIT_HEX = re.compile(r"^[0-9a-fA-F]{7,40}$")


def _tracked_py() -> list[pathlib.Path]:
    out = subprocess.run(["git", "ls-files", "*.py"], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout
    files = [ROOT / p for p in out.splitlines()]
    vendor_dirs = {p.parent for p in ROOT.rglob("LICENSE.upstream.md")}
    return [p for p in files if not any(p == d or d in p.parents for d in vendor_dirs)]


def check_source_commit(root: pathlib.Path) -> list[str]:
    """Return error strings for a bad or missing Source-Commit pin.

    Missing RELEASE-INFO.txt yields [] so the required-file loop owns that
    report (no double fault). Fail closed when git is missing. Shallow
    clones are not auto-skipped; see module docstring.
    """
    path = root / "RELEASE-INFO.txt"
    if not path.is_file():
        return []

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"RELEASE-INFO.txt: unreadable: {exc}"]

    matches = _SOURCE_COMMIT_LINE.findall(text)
    if len(matches) == 0:
        return ["RELEASE-INFO.txt: missing Source-Commit field"]
    if len(matches) > 1:
        return ["RELEASE-INFO.txt: duplicate Source-Commit field"]

    token = matches[0].strip()
    if not token:
        return ["RELEASE-INFO.txt: empty Source-Commit value"]

    if _SOURCE_COMMIT_HEX.fullmatch(token) is None:
        return [
            "RELEASE-INFO.txt: Source-Commit malformed "
            f"(want 7-40 hex chars): {token}"
        ]

    try:
        probe = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=root,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, OSError) as exc:
        return [f"RELEASE-INFO.txt: Source-Commit check requires git: {exc}"]

    if probe.returncode != 0:
        return ["RELEASE-INFO.txt: Source-Commit check: not a git repository"]

    # Peel to a commit object. Argv list keeps ^{commit} intact on Windows
    # (no shell). token + "^{commit}" avoids f-string brace escaping traps.
    try:
        resolved_proc = subprocess.run(
            ["git", "rev-parse", "--verify", token + "^{commit}"],
            cwd=root,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, OSError) as exc:
        return [f"RELEASE-INFO.txt: Source-Commit check requires git: {exc}"]

    resolved = (resolved_proc.stdout or "").strip()
    if resolved_proc.returncode != 0 or not resolved:
        return [
            "RELEASE-INFO.txt: Source-Commit does not resolve to a commit: "
            f"{token}"
        ]

    try:
        anc = subprocess.run(
            ["git", "merge-base", "--is-ancestor", resolved, "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, OSError) as exc:
        return [f"RELEASE-INFO.txt: Source-Commit check requires git: {exc}"]

    if anc.returncode == 0:
        return []
    if anc.returncode == 1:
        return [
            "RELEASE-INFO.txt: Source-Commit is not an ancestor of HEAD: "
            f"{resolved}"
        ]
    reason = (anc.stderr or anc.stdout or f"exit {anc.returncode}").strip()
    return [f"RELEASE-INFO.txt: Source-Commit ancestor check failed: {reason}"]


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"required file missing: {rel}")

    errors.extend(check_source_commit(ROOT))

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
