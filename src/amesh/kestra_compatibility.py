"""Backward-compatible import path for the Kestra compatibility feature.

The implementation lives in :mod:`amesh.compatibility.kestra`. Replacing this
module entry with that object preserves legacy imports and monkeypatch behavior.
"""

from __future__ import annotations

import sys as _sys

from amesh.compatibility import kestra as _kestra

_sys.modules[__name__] = _kestra
