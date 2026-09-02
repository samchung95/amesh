"""Backward-compatible import path for the AMESH API composition module.

The implementation lives in :mod:`amesh.api.application`.  Replacing this
module entry with that object (instead of copying its exports) keeps legacy
imports and monkeypatches operating on the implementation module's globals.
"""

from __future__ import annotations

import sys as _sys
from typing import TYPE_CHECKING

from amesh.api import application as _application

if TYPE_CHECKING:
    from amesh.api.application import app as app
    from amesh.api.application import (
        get_trusted_plugin_runtime as get_trusted_plugin_runtime,
    )

_sys.modules[__name__] = _application
