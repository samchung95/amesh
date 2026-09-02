"""Compatibility alias for :mod:`amesh.entrypoints.cli`."""

import sys
from importlib import import_module

if __name__ == "__main__":
    from amesh.entrypoints.cli import main

    raise SystemExit(main())
else:
    _module = import_module("amesh.entrypoints.cli")
    sys.modules[__name__] = _module
