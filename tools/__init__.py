"""Dev and build related tools for git-tags."""

import sys
from os import _exit as exit

__all__ = ["abort"]


def abort(message):
    """Print error message and exit."""
    print(message, file=sys.stderr)
    exit(1)
