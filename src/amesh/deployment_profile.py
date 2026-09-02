"""Compatibility alias for :mod:`amesh.entrypoints.deployment_profile`."""

import sys
from importlib import import_module

if __name__ == "__main__":
    from amesh.entrypoints.deployment_profile import main

    main()
else:
    _module = import_module("amesh.entrypoints.deployment_profile")
    sys.modules[__name__] = _module
