#!/usr/bin/env python3
"""Simple introspection aid for OpenClaw interfaces.

This script attempts to load the openclaw package (if present) and print
basic entry points or exported API surface to help documentation planning.
"""

import importlib
import sys


def main():
    infos = []
    try:
        openclaw = importlib.import_module("openclaw")
        infos.append(("module_openclaw", True))
        if hasattr(openclaw, "__all__"):
            infos.append(("__all__", getattr(openclaw, "__all__")))
    except Exception as e:
        infos.append(("module_openclaw", False))

    # Try common CLI entry if available
    try:
        main_mod = importlib.import_module("openclaw")
        if hasattr(main_mod, "__name__"):
            infos.append(("openclaw_module_name", main_mod.__name__))
    except Exception:
        pass

    print({k: v for k, v in infos})


if __name__ == "__main__":
    main()
