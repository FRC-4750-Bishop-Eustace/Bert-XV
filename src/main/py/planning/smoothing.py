# MIT License
#
# Copyright (c) 2026 Beʳᵗ FRC Team 4750
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

__all__ = [
    "CollisionChecker",
    "SmoothPath",
    "Smoother",
]


@dataclass
class SmoothPath:
    points: list[tuple[float, float]]


class CollisionChecker(Protocol):
    def IsCollision(self, x: float, y: float, theta: float | None = None) -> bool:
        raise NotImplementedError


class Smoother:
    def __init__(self, collisionChecker: CollisionChecker | None = None) -> None:
        self.collisionChecker = collisionChecker

    def removeRedundant(self, points: Sequence[tuple[float, float]]) -> list[tuple[float, float]]:
        if len(points) <= 2:
            return list(points)

        res: list[tuple[float, float]] = [points[0]]
        for p in points[1:-1]:
            last = res[-1]
            dx = p[0] - last[0]
            dy = p[1] - last[1]

            if abs(dx) > 1e-3 or abs(dy) > 1e-3:
                res.append(p)

        res.append(points[-1])
        return res

    def smooth(self, points: Sequence[tuple[float, float]], spacing: float = 0.1) -> SmoothPath:
        if len(points) < 2:
            return SmoothPath(list(points))

        pts = self.removeRedundant(points)

        # Simple linear resampling as a minimal safe baseline
        res: list[tuple[float, float]] = [pts[0]]
        for i in range(len(pts) - 1):
            p0 = pts[i]
            p1 = pts[i + 1]
            d = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            if d < 1e-6:
                continue

            steps = max(1, math.ceil(d / spacing))
            for j in range(1, steps):
                t = j / steps
                res.append((p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t))

        res.append(pts[-1])
        return SmoothPath(res)
