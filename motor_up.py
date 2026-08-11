#!/usr/bin/env python3
"""Raise the shade its full travel. Called from cron at sunrise.

SUBJECT: cron entry point for the roller shade; travel constants live in
shade.py, which documents where they were measured.
"""

import sys

from shade import move

if __name__ == "__main__":
    move("up", dry_run="--dry-run" in sys.argv)
