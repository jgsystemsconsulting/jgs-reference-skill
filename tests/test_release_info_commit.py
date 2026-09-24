# Copyright (c) 2026 JG Systems Consulting Ltd. See LICENSE.
# SPDX-License-Identifier: MIT
"""Source-Commit ancestor gate for scripts/check_release.py (P6 residual).

Temp git repos via subprocess (not monkeypatched git). Skips when git is
unavailable, matching tests/test_repo_hygiene.py.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_release  # noqa: E402


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            timeout=30,
            text=True,
            encoding="utf-8",
            errors="surrogateescape",
        )
    except (OSError, subprocess.SubprocessError) as exc:
        pytest.skip(f"git unavailable: {exc}")


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    init = _git(repo, "init")
    if init.returncode != 0:
        pytest.skip(f"git init failed: {init.stderr}")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "user.email", "test@example.com")
    # Normalize branch name across git defaults (master vs main).
    branch = _git(repo, "checkout", "-b", "main")
    if branch.returncode != 0:
        branch = _git(repo, "checkout", "main")
    if branch.returncode != 0:
        pytest.skip(f"cannot ensure main branch: {branch.stderr}")
    (repo / "README").write_text("one\n", encoding="utf-8")
    _git(repo, "add", "README")
    commit = _git(repo, "commit", "-m", "c1")
    if commit.returncode != 0:
        pytest.skip(f"git commit failed: {commit.stderr}")
    return repo


def _head(repo: Path) -> str:
    proc = _git(repo, "rev-parse", "HEAD")
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.strip()


def _write_info(repo: Path, body: str) -> None:
    (repo / "RELEASE-INFO.txt").write_text(body, encoding="utf-8")


def test_ancestor_full_hash_passes(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    full = _head(repo)
    _write_info(repo, f"Version: 0.0.0\nSource-Commit: {full}\n")
    assert check_release.check_source_commit(repo) == []


def test_ancestor_short_hash_passes(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    full = _head(repo)
    short = full[:7]
    _write_info(repo, f"Version: 0.0.0\nSource-Commit: {short}\n")
    assert check_release.check_source_commit(repo) == []


def test_phantom_hash_fails(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    phantom = "a" * 40
    _write_info(repo, f"Version: 0.0.0\nSource-Commit: {phantom}\n")
    errs = check_release.check_source_commit(repo)
    assert len(errs) == 1
    assert "does not resolve to a commit" in errs[0]
    assert phantom in errs[0]


def test_real_but_unrelated_non_ancestor_fails(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    # Second lineage not merged into main; pin that tip while HEAD stays on main.
    _git(repo, "checkout", "-b", "other")
    (repo / "README").write_text("other\n", encoding="utf-8")
    _git(repo, "add", "README")
    c2 = _git(repo, "commit", "-m", "c2-other")
    assert c2.returncode == 0, c2.stderr
    other = _head(repo)
    _git(repo, "checkout", "main")
    assert _head(repo) != other
    _write_info(repo, f"Version: 0.0.0\nSource-Commit: {other}\n")
    errs = check_release.check_source_commit(repo)
    assert len(errs) == 1
    assert "not an ancestor of HEAD" in errs[0]
    assert other in errs[0]


def test_malformed_token_fails(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_info(repo, "Version: 0.0.0\nSource-Commit: not-a-hash\n")
    errs = check_release.check_source_commit(repo)
    assert len(errs) == 1
    assert "malformed" in errs[0]
    assert "not-a-hash" in errs[0]


def test_too_short_hex_fails(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_info(repo, "Version: 0.0.0\nSource-Commit: abc\n")
    errs = check_release.check_source_commit(repo)
    assert len(errs) == 1
    assert "malformed" in errs[0]


def test_duplicate_field_fails(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    full = _head(repo)
    _write_info(
        repo,
        f"Source-Commit: {full}\nVersion: 0.0.0\nSource-Commit: {full}\n",
    )
    errs = check_release.check_source_commit(repo)
    assert len(errs) == 1
    assert "duplicate Source-Commit field" in errs[0]


def test_missing_field_fails(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_info(repo, "Version: 0.0.0\n")
    errs = check_release.check_source_commit(repo)
    assert len(errs) == 1
    assert "missing Source-Commit field" in errs[0]


def test_empty_file_missing_field(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_info(repo, "")
    errs = check_release.check_source_commit(repo)
    assert len(errs) == 1
    assert "missing Source-Commit field" in errs[0]


def test_missing_file_skips_validation(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    assert not (repo / "RELEASE-INFO.txt").exists()
    assert check_release.check_source_commit(repo) == []


def test_not_a_git_repository_message(tmp_path: Path) -> None:
    bare = tmp_path / "not-repo"
    bare.mkdir()
    _write_info(bare, "Source-Commit: " + ("b" * 40) + "\n")
    # git may be present but cwd is not a work tree
    try:
        subprocess.run(
            ["git", "--version"],
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        pytest.skip(f"git unavailable: {exc}")
    errs = check_release.check_source_commit(bare)
    assert len(errs) == 1
    assert "not a git repository" in errs[0]


def test_non_utf8_bytes_currently_crash_helper(tmp_path: Path) -> None:
    """Pin the known crash path: read_text(encoding="utf-8") in
    check_source_commit catches only OSError, so a non-UTF-8 byte raises
    UnicodeDecodeError out of the helper (a bare traceback for CLI users,
    not a ::error:: line). The wanted fix is to also catch
    UnicodeDecodeError and return an error string; when that lands this
    test fails and must be flipped to assert the returned error.
    """
    repo = _init_repo(tmp_path)
    (repo / "RELEASE-INFO.txt").write_bytes(
        b"Version: 0.0.0\nSource-Commit: \xff\xfe\n"
    )
    with pytest.raises(UnicodeDecodeError):
        check_release.check_source_commit(repo)
