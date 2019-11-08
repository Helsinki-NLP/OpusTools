"""Utility functions"""

import bz2
import gzip


def file_open(filename, mode='r'):
    """Open file with implicit gzip/bz2 support

    Uses text mode by default regardless of the compression.

    """
    if filename.endswith('.bz2'):
        if mode in {'r', 'w', 'x', 'a'}:
            mode += 't'
        return bz2.open(filename, mode)
    if filename.endswith('.gz'):
        if mode in {'r', 'w', 'x', 'a'}:
            mode += 't'
        return gzip.open(filename, mode)
    return open(filename, mode)
