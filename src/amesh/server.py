"""Compatibility alias for :mod:`amesh.entrypoints.server`."""

import sys
from importlib import import_module

if __name__ == "__main__":
    from amesh.entrypoints.server import main

    main()
else:
    _module = import_module("amesh.entrypoints.server")
    sys.modules[__name__] = _module
