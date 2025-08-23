"""Adapters for integrating duckdantic with Python's type system.

This module provides adapters that allow duckdantic traits to work
seamlessly with Python's built-in type checking mechanisms.
"""

from __future__ import annotations

from duckdantic.adapters.abc import abc_for, duckisinstance, duckissubclass

__all__ = ["abc_for", "duckisinstance", "duckissubclass"]
