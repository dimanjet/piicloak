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

if __name__ == '__main__':
    from .app import main
    main()
