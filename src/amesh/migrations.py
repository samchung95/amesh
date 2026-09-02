"""Compatibility alias for :mod:`amesh.entrypoints.migrations`."""

import sys
from importlib import import_module

if __name__ == "__main__":
    from amesh.entrypoints.migrations import main

    main()
else:
    _module = import_module("amesh.entrypoints.migrations")
    sys.modules[__name__] = _module
