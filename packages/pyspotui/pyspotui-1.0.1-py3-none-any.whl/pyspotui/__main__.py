"""Module entry point so `python -m pyspotui` and `uv run pyspotui` work.

Handles execution both as a module (-m) and as a script executed via uv where
the package context might not be set yet.
"""
import os
import sys

if __package__ is None or __package__ == "":  # executed directly, fix sys.path
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pyspotui.main import main  # noqa: E402

if __name__ == "__main__":  # pragma: no cover
    main()
