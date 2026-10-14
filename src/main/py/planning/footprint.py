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
from collections.abc import Callable
from dataclasses import dataclass

__all__ = [
    "IsPathClearLineOfSight",
    "RobotCenterRadius",
    "RobotFootprint",
]


@dataclass(frozen=True, slots=True)
class RobotFootprint:
    length: float  # Along x in robot frame
    width: float  # Along y in robot frame
    margin: float = 0.0

    @property
    def HalfLength(self) -> float:
        return self.length * 0.5

    @property
    def HalfWidth(self) -> float:
        return self.width * 0.5

    @property
    def CircumscribedRadius(self) -> float:
        return 0.5 * math.sqrt((self.length**2) + (self.width**2)) + self.margin


def RobotCenterRadius(length: float, width: float, margin: float = 0.0) -> float:
    return 0.5 * math.sqrt((length**2) + (width**2)) + margin


def IsPathClearLineOfSight(
    px1: float,
    py1: float,
    px2: float,
    py2: float,
    occupancyQuery: Callable[..., bool],  # Function f(x,y)->bool (True if blocked)
    footprint: RobotFootprint | None = None,
) -> bool:
    # Simple grid-step based LOS check; caller can pass in more accurate
    dx = px2 - px1
    dy = py2 - py1
    dist = math.hypot(dx, dy)
    if dist < 1e-6:
        return True

    steps = max(1, int(dist / 0.02))  # Sample every 2cm
    for i in range(1, steps + 1):
        t = i / steps
        x = px1 + dx * t
        y = py1 + dy * t

        try:
            if occupancyQuery(x, y, footprint):
                return False
        except Exception:
            pass

    return True
