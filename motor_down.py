#!/usr/bin/env python3
"""Lower the shade its full travel. Called from cron at sunset.

SUBJECT: cron entry point for the roller shade; travel constants live in
shade.py, which documents where they were measured.
"""

import sys

from shade import move

if __name__ == "__main__":
    move("down", dry_run="--dry-run" in sys.argv)
