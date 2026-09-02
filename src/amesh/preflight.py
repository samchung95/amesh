"""Compatibility alias for :mod:`amesh.entrypoints.preflight`."""

import sys
from importlib import import_module

if __name__ == "__main__":
    from amesh.entrypoints.preflight import main

    main()
else:
    _module = import_module("amesh.entrypoints.preflight")
    sys.modules[__name__] = _module
