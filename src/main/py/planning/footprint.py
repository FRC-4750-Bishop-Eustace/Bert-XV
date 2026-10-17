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

from .gridmap import GridMap

__all__ = [
    "FootprintChecker",
    "IsFootprintClear",
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

    @property
    def InscribedRadius(self) -> float:
        return min(self.HalfLength, self.HalfWidth) + self.margin


def RobotCenterRadius(length: float, width: float, margin: float = 0.0) -> float:
    return 0.5 * math.sqrt((length**2) + (width**2)) + margin


class FootprintChecker:
    def __init__(self, gridMap: GridMap, footprint: RobotFootprint, resolution: float = 0.05) -> None:

        self.gridMap = gridMap
        self.footprint = footprint
        self.resolution = resolution
        self.checkResolution = min(resolution, 0.01)

    def IsClear(self, x: float, y: float, theta: float = 0.0) -> bool:
        r = self.footprint.CircumscribedRadius

        # Sample points in footprint or use grid cells
        if r < 1e-3:
            g = self.gridMap.ToGrid(x, y)
            return g is not None and not self.gridMap.IsBlocked(g.gx, g.gy)

        rCells = math.ceil(r / self.gridMap.resolution)
        g0 = self.gridMap.ToGrid(x, y)
        if g0 is None:
            return False

        cosT = math.cos(theta)
        sinT = math.sin(theta)
        halfL = self.footprint.HalfLength
        halfW = self.footprint.HalfWidth

        # Check grid cells within circumscribed radius
        for dy in range(-rCells, rCells + 1):
            for dx in range(-rCells, rCells + 1):
                gx, gy = g0.gx + dx, g0.gy + dy
                if self.gridMap.OutOfBounds(gx, gy):
                    return False
                if self.gridMap.IsBlocked(gx, gy):
                    wx, wy = self.gridMap.ToWorld(gx, gy)

                    # Transform to robot frame
                    rx = (wx - x) * cosT + (wy - y) * sinT
                    ry = -(wx - x) * sinT + (wy - y) * cosT
                    if abs(rx) <= halfL + 0.01 and abs(ry) <= halfW + 0.01:
                        return False
        return True

    def CheckCollision(self, x: float, y: float, theta: float = 0.0) -> bool:
        return not self.IsClear(x, y, theta)


def IsFootprintClear(
    x: float,
    y: float,
    theta: float,
    footprint: RobotFootprint,
    gridMap: GridMap,
) -> bool:
    checker = FootprintChecker(gridMap, footprint)
    return checker.IsClear(x, y, theta)


def IsPathClearLineOfSight(
    px1: float,
    py1: float,
    px2: float,
    py2: float,
    occupancyQuery: Callable[..., bool],
    footprint: RobotFootprint | None = None,
) -> bool:
    dx = px2 - px1
    dy = py2 - py1
    dist = math.hypot(dx, dy)
    if dist < 1e-6:
        return True

    steps = max(1, int(dist / 0.02))
    for i in range(1, steps + 1):
        t = i / steps
        x = px1 + dx * t
        y = py1 + dy * t

        try:
            if footprint is not None:
                if occupancyQuery(x, y, 0.0):
                    return False
            else:
                if occupancyQuery(x, y):
                    return False

        except Exception:
            pass

    return True
