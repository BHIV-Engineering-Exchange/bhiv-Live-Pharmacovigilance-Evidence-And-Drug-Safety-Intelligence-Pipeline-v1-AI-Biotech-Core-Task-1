"""Expose the repository's root-level modules under the documented src package."""

from pathlib import Path

__path__.append(str(Path(__file__).resolve().parent.parent))
