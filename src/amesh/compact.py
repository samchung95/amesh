"""Compatibility alias for :mod:`amesh.entrypoints.compact`."""

import sys
from importlib import import_module

if __name__ == "__main__":
    from amesh.entrypoints.compact import main

    main()
else:
    _module = import_module("amesh.entrypoints.compact")
    sys.modules[__name__] = _module
