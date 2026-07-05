"""Entry point for running the package directly via `python -m package_name`."""
import sys

if __package__ in (None, ""):
    # being run as a plain script (no -m, no package context) — patch sys.path
    import os
    sys.path.insert(
        0,
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
    from dadascribe.cli import main
else:
    from .cli import main

if __name__ == "__main__":
    sys.exit(main())