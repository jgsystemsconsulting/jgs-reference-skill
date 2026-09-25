#!/usr/bin/env python3
# Copyright (c) 2026 JG Systems Consulting Ltd. See LICENSE.
# SPDX-License-Identifier: MIT
"""Release gate (RR-B-15): required files, forbidden paths, forbidden
content, headers present on first-party .py files, version agreement
(CITATION/README against RELEASE-INFO), and Source-Commit resolves to an
ancestor of HEAD. Exits non-zero on any failure.

Also enforces the RR-B-37 escape guard (RR-B-35 keep/drop): session-state
directories must stay untracked, decided .gitignore rules must remain, and
frozen trees (docs/superpowers/) must keep their tracked file list pinned to
a sha256 baseline.

Complements (does not replace) validate.yml's existing content-integrity,
SKILL.md frontmatter, and version-consistency steps.

Source-Commit ancestor check walks local git history. Shallow clones may
false-fail; run `git fetch --unshallow` (or deepen) before relying on this
gate locally. CI integrity checkout sets fetch-depth: 0.
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

REQUIRED = [
    "LICENSE", "COPYRIGHT", "NOTICE", "README.md", "CHANGELOG.md",
    "SECURITY.md", "CITATION.cff", "RELEASE-INFO.txt", "SKILL.md",
    "SKILLS.md", "docs/index.html", "docs/DISTRIBUTION.md",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/improvement.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".cursor-plugin/plugin.json",
    "gemini-extension.json",
]

# Forbidden path fragments (RR-B-15): build/venv/cache artifacts must never be
# tracked. Judged against `git ls-files`, so local gitignored dirs are fine.
FORBIDDEN_PATH_PARTS = [
    "__pycache__", ".venv", ".worktrees", ".pytest_cache",
    ".ruff_cache", ".bak",
]

# RR-B-37 escape guard (decisions recorded in docs/DISTRIBUTION.md, RR-B-35,
# dated 2026-09-24): session dirs stay untracked; .gitignore rules must stay;
# docs/superpowers/ is kept as frozen process history with a pinned tracked
# file list. On a deliberate change, recompute and update the baseline:
#   python -c "import hashlib,subprocess; files=sorted(subprocess.check_output(
#     ['git','ls-files','docs/superpowers'],text=True).splitlines());
#     print(hashlib.sha256('\n'.join(files).encode()).hexdigest())"
NEVER_TRACK = (".zcode/", ".superpowers/")
IGNORE_RULES: tuple[str, ...] = (".zcode/", ".superpowers/", "packs/")
FROZEN_TREES: dict[str, str] = {
    "docs/superpowers/": "08849715934b6e44fabd4a71dc5f419696a5d5e71864e1d0c74365b389ce7e82",
}

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


def _tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    return out.splitlines()


def check_forbidden_paths(tracked: list[str]) -> list[str]:
    return [
        f"forbidden tracked path: {f}"
        for f in tracked
        if any(part in f for part in FORBIDDEN_PATH_PARTS)
    ]


def check_escape_guard(tracked: list[str]) -> list[str]:
    errors = []
    for f in tracked:
        if f.startswith(NEVER_TRACK):
            errors.append(f"internal artifact tracked (RR-B-37): {f}")
    gi = ROOT / ".gitignore"
    gi_text = gi.read_text(encoding="utf-8") if gi.is_file() else ""
    for rule in IGNORE_RULES:
        if rule not in gi_text:
            errors.append(f".gitignore lost the RR-B-37 rule: {rule}")
    for prefix, baseline in FROZEN_TREES.items():
        files = sorted(f for f in tracked if f.startswith(prefix))
        digest = hashlib.sha256("\n".join(files).encode()).hexdigest()
        if digest != baseline:
            errors.append(
                f"{prefix} tracked set changed (RR-B-37): {len(files)} files vs "
                "frozen baseline; if deliberate, update FROZEN_TREES"
            )
    return errors


def check_version_agreement(root: pathlib.Path) -> list[str]:
    """Return error strings unless CITATION.cff, the README badge, and the
    README agent-install prompt agree with RELEASE-INFO's Version: field
    (RR-S-11 drift class, caught locally without waiting for CI)."""
    def find(path: str, pattern: re.Pattern[str]) -> str | None:
        p = root / path
        if not p.is_file():
            return None  # required-file loop owns the missing-file report
        m = pattern.search(p.read_text(encoding="utf-8", errors="ignore"))
        return m.group(1) if m else None

    release = find("RELEASE-INFO.txt", re.compile(r"^Version:\s*(\d+\.\d+\.\d+)", re.M))
    if release is None:
        return ["RELEASE-INFO.txt: no Version: field found"]

    errors = []
    surfaces = {
        "CITATION.cff version": find("CITATION.cff", re.compile(r"^version:\s*(\d+\.\d+\.\d+)", re.M)),
        "README version badge": find("README.md", re.compile(r"version-(\d+\.\d+\.\d+)-informational")),
        "README agent-install prompt": find("README.md", re.compile(r"\(v(\d+\.\d+\.\d+)\)")),
    }
    for name, value in surfaces.items():
        if value is None:
            errors.append(f"{name}: not found (expected {release})")
        elif value != release:
            errors.append(f"{name}: {value} != RELEASE-INFO {release}")
    return errors


def check_site_version(root, release_re):
    """docs/index.html version strings must equal RELEASE-INFO.txt (ported from jgs-lit-memory)."""
    m = re.search(release_re, (root / "RELEASE-INFO.txt").read_text(encoding="utf-8"), re.M)
    if not m:
        return ["RELEASE-INFO.txt: no version line"]
    expected = m.group(1)
    page = (root / "docs" / "index.html").read_text(encoding="utf-8")
    loci = {
        "softwareVersion": r'"softwareVersion":\s*"(\d+\.\d+\.\d+)"',
        "masthead REV": r"REV <b>(\d+\.\d+\.\d+)</b>",
        "footer Rev": r'<span class="label">Rev</span><b>(\d+\.\d+\.\d+)</b>',
    }
    bad = []
    for name, pat in loci.items():
        v = re.search(pat, page)
        val = v.group(1) if v else None
        if val != expected:
            bad.append(f"{name}={val!r} (expected {expected})")
    if bad:
        return ["site page version mismatch or missing pattern: " + "; ".join(bad)]
    print(f"site page versions agree at {expected}")
    return []


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"required file missing: {rel}")

    errors.extend(check_source_commit(ROOT))

    tracked = _tracked_files()
    errors.extend(check_forbidden_paths(tracked))
    errors.extend(check_escape_guard(tracked))
    errors.extend(check_version_agreement(ROOT))
    errors.extend(check_site_version(ROOT, r"^Version:\s*(\d+\.\d+\.\d+)"))

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
