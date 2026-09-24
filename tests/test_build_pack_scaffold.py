# Copyright (c) 2026 JG Systems Consulting Ltd. See LICENSE.
# SPDX-License-Identifier: MIT
"""Regression tests: build_pack scaffolds are contained, deterministic, YAML-safe.

Covers spec 2026-09-24-pack-scaffold-provenance criteria 1-4:
  1. the slug gate refuses absolute / dot-dot / non-kebab / Windows-reserved
     slugs before any filesystem effect, including a missing --out-dir;
  2. PACK.yaml titles round-trip through parse_simple_yaml for adversarial
     characters with no injected keys;
  3. the LICENSE stub carries the raw title with no JSON escape artifacts;
  4. the scaffold is rendered from templates/PACK.yaml (no embedded template
     copy) with the fill-later markers left intact.
"""

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_pack  # noqa: E402
from validate_pack import parse_simple_yaml  # noqa: E402

OUT_DIR = "packs"
# Clean Tier-1 triple: no Excluded substring, no vetting warnings, no --force.
CLEAN = {
    "title": "Fill Demo Handbook",
    "publisher": "Example Press",
    "version": "1st ed. (2020)",
    "license": "Public Domain (US Government work)",
}
EXPECTED_KEYS = {
    "slug", "title", "publisher", "source_version", "license", "license_tier",
    "commercial_use", "share_alike", "attribution_required",
}
TOKENS = ("<SLUG>", "<TITLE>", "<PUBLISHER>", "<VERSION>", "<LICENSE>",
          "<TIER>", "<COMMERCIAL_USE>", "<SHARE_ALIKE>", "<ATTRIBUTION_REQUIRED>")


def run(tmp_path, slug, out_dir=None, **overrides):
    """Call build_pack.main with the clean triple; return the exit code."""
    argv = ["build_pack.py", "--slug", slug,
            "--out-dir", str(out_dir or tmp_path / OUT_DIR)]
    for key, value in {**CLEAN, **overrides}.items():
        argv += [f"--{key.replace('_', '-')}", value]
    return build_pack.main(argv)


def scaffold(tmp_path, slug, out_dir=None, **overrides):
    """Successful scaffold; returns the pack directory."""
    rc = run(tmp_path, slug, out_dir=out_dir, **overrides)
    assert rc == 0, f"build_pack failed with rc={rc}"
    return (out_dir or tmp_path / OUT_DIR) / slug


def test_slug_absolute_path_rejected(tmp_path):
    rc = run(tmp_path, "/tmp/evil")
    assert rc == 1
    # Nothing created under the out-dir, and nothing at the absolute target.
    assert not (tmp_path / OUT_DIR).exists()
    assert not Path("/tmp/evil").exists()


def test_slug_dotdot_rejected(tmp_path):
    before = set(tmp_path.iterdir())
    assert run(tmp_path, "../../x") == 1
    # Nothing under the out-dir and nothing outside it either.
    assert set(tmp_path.iterdir()) == before


def test_slug_bad_kebab_rejected(tmp_path):
    before = set(tmp_path.iterdir())
    assert run(tmp_path, "Bad Slug") == 1
    assert set(tmp_path.iterdir()) == before


def test_slug_reserved_con_rejected(tmp_path):
    for slug in ("con", "CON"):
        before = set(tmp_path.iterdir())
        assert run(tmp_path, slug) == 1
        assert set(tmp_path.iterdir()) == before


def test_slug_rejected_when_outdir_missing(tmp_path):
    out_dir = tmp_path / "deep" / "packs"
    assert not out_dir.exists()
    assert run(tmp_path, "Bad Slug", out_dir=out_dir) == 1
    # The rejection must not create the out-dir (or any pack inside it).
    assert not out_dir.exists()


@pytest.mark.parametrize("title", [
    'The "Quoted" Handbook',
    "Colon: Spaced Title",
    "Hash # Tagged",
    "Line1\nLine2",
])
def test_yaml_title_roundtrip_special_chars(tmp_path, title):
    pack = scaffold(tmp_path, "yaml-demo", title=title)
    meta = parse_simple_yaml((pack / "PACK.yaml").read_text(encoding="utf-8"))
    assert meta["title"] == title
    # No injected keys: exactly the template's top-level scalar set.
    assert set(meta) == EXPECTED_KEYS


def test_license_raw_title_no_json_artifacts(tmp_path):
    title = 'The "Quote" Handbook'
    pack = scaffold(tmp_path, "license-demo", title=title)
    license_text = (pack / "LICENSE").read_text(encoding="utf-8")
    assert title in license_text
    assert '\\"' not in license_text  # no JSON escape leaked into prose


def test_no_embedded_pack_yaml_template():
    source = (REPO_ROOT / "tools" / "build_pack.py").read_text(encoding="utf-8")
    assert "PACK_YAML_TEMPLATE" not in source


def test_scaffold_deterministic_and_matches_template_shape(tmp_path):
    pack_a = scaffold(tmp_path, "det-demo", out_dir=tmp_path / "a")
    pack_b = scaffold(tmp_path, "det-demo", out_dir=tmp_path / "b")
    raw_a = (pack_a / "PACK.yaml").read_bytes()
    assert raw_a == (pack_b / "PACK.yaml").read_bytes()

    text = raw_a.decode("utf-8")
    # Fill-later markers survive the build untouched.
    assert 'built_on: "TODO"' in text
    assert "source_pages: 0" in text
    assert "chapters: 0" in text
    # All nine build-filled tokens substituted.
    assert all(token not in text for token in TOKENS)
    assert not re.search(r"<[A-Z][A-Z_]*>", text)
