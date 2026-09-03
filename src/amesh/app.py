"""Backward-compatible import path for the AMESH API composition module.

Normal imports retain the implementation module's identity so dependency
overrides and legacy monkeypatches still reach their owning feature module.
Module execution deliberately leaves ``__main__`` untouched.
"""

from __future__ import annotations

import sys as _sys
from typing import TYPE_CHECKING

from amesh.api import application as _application

if TYPE_CHECKING:
    from fastapi import FastAPI

    from amesh.api.dependencies import (
        get_trusted_plugin_runtime as get_trusted_plugin_runtime,
    )

    app: FastAPI

if __name__ != "__main__":
    _sys.modules[__name__] = _application
