"""Compatibility alias for :mod:`amesh.entrypoints.worker`."""

import sys
from importlib import import_module

if __name__ == "__main__":
    from amesh.entrypoints.worker import main

    main()
else:
    _module = import_module("amesh.entrypoints.worker")
    sys.modules[__name__] = _module
