"""Compatibility alias for :mod:`amesh.entrypoints.role`."""

import sys
from importlib import import_module

if __name__ == "__main__":
    from amesh.entrypoints.role import main

    main()
else:
    _module = import_module("amesh.entrypoints.role")
    sys.modules[__name__] = _module
