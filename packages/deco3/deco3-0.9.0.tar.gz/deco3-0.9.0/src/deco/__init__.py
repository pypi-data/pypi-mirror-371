# flake8-in-file-ignores: noqa: F401

# Copyright (c) 2016 Alex Sherman
# Copyright (c) 2025 Adam Karpierz
# SPDX-License-Identifier: MIT

from .__about__ import * ; del __about__  # type: ignore[name-defined]  # noqa

from ._concurrent import concurrent, synchronized
