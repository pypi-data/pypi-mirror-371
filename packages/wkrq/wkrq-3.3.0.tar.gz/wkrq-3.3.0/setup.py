#!/usr/bin/env python
"""
Backwards compatibility setup.py for older pip versions.
Modern installations should use pyproject.toml directly.
"""

from setuptools import setup

if __name__ == "__main__":
    setup()