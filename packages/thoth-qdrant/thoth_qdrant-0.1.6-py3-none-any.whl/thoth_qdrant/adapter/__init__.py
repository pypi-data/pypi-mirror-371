# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the Apache License 2.0.
# See the LICENSE.md file in the project root for full license information.

"""Adapter implementations for Thoth Qdrant."""

from .qdrant_native import QdrantNativeAdapter

__all__ = ["QdrantNativeAdapter"]