#!/usr/bin/env python3
"""
PIICloak command-line entry point.

Usage:
    python -m piicloak

Environment variables:
    PIICLOAK_PORT=8000
    PIICLOAK_HOST=0.0.0.0
    PIICLOAK_WORKERS=4
"""

import sys


def main():
    """Dispatch CLI commands."""
    if len(sys.argv) > 1 and sys.argv[1] == "redact":
        from .redaction import redact_main

        raise SystemExit(redact_main(sys.argv[2:]))

    from .app import main as _serve

    _serve()


if __name__ == "__main__":
    main()
