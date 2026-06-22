#!/usr/bin/env bash
# Copyright (c) 2026 JG Systems Consulting Ltd. — MIT License (see LICENSE).
# SPDX-License-Identifier: MIT
# Thin wrapper around install.py — see `./install.sh --help`.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=python3; command -v python3 >/dev/null 2>&1 || PY=python
exec "$PY" "$DIR/install.py" "$@"
