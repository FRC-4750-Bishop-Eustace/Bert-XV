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
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass

__all__ = [
    "CostMap",
    "GridCoord",
    "GridMap",
]


@dataclass(frozen=True, slots=True)
class GridCoord:
    gx: int
    gy: int


class GridMap:
    def __init__(
        self,
        fieldWidth: float,
        fieldLength: float,
        resolution: float = 0.05,
        costap: CostMap | None = None,
        inflationRadius: float = 0.0,
    ) -> None:
        self.fieldWidth = fieldWidth
        self.fieldLength = fieldLength
        self.resolution = resolution
        self.costap = costap or CostMap()
        self.inflationRadius = inflationRadius

        self.gridx = max(1, math.ceil(self.fieldWidth / self.resolution))
        self.gridy = max(1, math.ceil(self.fieldLength / self.resolution))
        self.grid = bytearray(self.gridx * self.gridy)
        self.clearanceGrid = bytearray(self.gridx * self.gridy)  # Store distance class 0-255
        self.clearanceDirty = True

    def ToGrid(self, x: float, y: float) -> GridCoord | None:
        gx = math.floor(x / self.resolution)
        gy = math.floor(y / self.resolution)
        if gx < 0 or gy < 0 or gx >= self.gridx or gy >= self.gridy:
            return None

        return GridCoord(gx, gy)

    def ToWorld(self, gx: int, gy: int) -> tuple[float, float]:
        return (gx + 0.5) * self.resolution, (gy + 0.5) * self.resolution

    def Index(self, gx: int, gy: int) -> int:
        return gy * self.gridx + gx

    def IsBlocked(self, gx: int, gy: int) -> bool:
        if gx < 0 or gy < 0 or gx >= self.gridx or gy >= self.gridy:
            return True

        return self.grid[self.Index(gx, gy)] != 0

    def SetBlocked(self, gx: int, gy: int, blocked: bool = True) -> None:
        if gx < 0 or gy < 0 or gx >= self.gridx or gy >= self.gridy:
            return

        self.grid[self.Index(gx, gy)] = 255 if blocked else 0
        self.clearanceDirty = True

    def ClearObstacles(self) -> None:
        for i in range(len(self.grid)):
            self.grid[i] = 0
        self.clearanceDirty = True

    def AddObstacleCircle(self, x: float, y: float, radius: float) -> None:
        r = max(radius, self.inflationRadius)
        g = self.ToGrid(x, y)
        if g is None:
            return

        rCells = math.ceil(r / self.resolution)
        for dy in range(-rCells, rCells + 1):
            for dx in range(-rCells, rCells + 1):
                gx, gy = g.gx + dx, g.gy + dy
                if self.OutOfBounds(gx, gy):
                    continue

                wx, wy = self.ToWorld(gx, gy)
                d = math.hypot(wx - x, wy - y)
                if d <= r + 1e-3:
                    self.grid[self.Index(gx, gy)] = 255

        self.clearanceDirty = True

    def AddObstaclePolygon(self, points: list[tuple[float, float]]) -> None:
        if len(points) < 3:
            return

        minx = min(p[0] for p in points)
        maxx = max(p[0] for p in points)
        miny = min(p[1] for p in points)
        maxy = max(p[1] for p in points)

        sx = self.ToGrid(minx, miny)
        ex = self.ToGrid(maxx, maxy)
        if sx is None or ex is None:
            return

        for gy in range(sx.gy, ex.gy + 2):
            for gx in range(sx.gx, ex.gx + 2):
                if self.OutOfBounds(gx, gy):
                    continue

                wx, wy = self.ToWorld(gx, gy)
                if self.PointInPolygon(wx, wy, points):
                    self.grid[self.Index(gx, gy)] = 255

        self.clearanceDirty = True

    def PointInPolygon(self, x: float, y: float, poly: list[tuple[float, float]]) -> bool:
        inside = False
        n = len(poly)
        j = n - 1

        for i in range(n):
            xi, yi = poly[i]
            xj, yj = poly[j]
            intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi)
            if intersect:
                inside = not inside

            j = i

        return inside

    def UpdateObstacles(self, updater: Callable[[GridMap], None]) -> None:
        updater(self)
        self.clearanceDirty = True

    def OutOfBounds(self, gx: int, gy: int) -> bool:
        return gx < 0 or gy < 0 or gx >= self.gridx or gy >= self.gridy

    def InBounds(self, gx: int, gy: int) -> bool:
        return not self.OutOfBounds(gx, gy)

    def BuildClearance(self, force: bool = False) -> None:
        if not force and not self.clearanceDirty:
            return

        for i in range(len(self.clearanceGrid)):
            if self.grid[i] == 255:
                self.clearanceGrid[i] = 0
            else:
                self.clearanceGrid[i] = 255

        queue: deque[tuple[int, int]] = deque()
        for gy in range(self.gridy):
            for gx in range(self.gridx):
                if self.clearanceGrid[self.Index(gx, gy)] == 0:
                    queue.append((gx, gy))

        # 8-neighborhood for better distance approximation
        neighbors = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]

        while queue:
            cx, cy = queue.popleft()
            cval = self.clearanceGrid[self.Index(cx, cy)]
            for nx, ny in neighbors:
                ng, nh = cx + nx, cy + ny
                if self.OutOfBounds(ng, nh):
                    continue
                idx = self.Index(ng, nh)
                nd = cval + 1
                if nd < self.clearanceGrid[idx]:
                    self.clearanceGrid[idx] = min(255, nd)
                    queue.append((ng, nh))

        self.clearanceDirty = False

    def GetClearance(self, gx: int, gy: int) -> float:
        self.BuildClearance()
        if self.OutOfBounds(gx, gy):
            return 0.0

        return float(self.clearanceGrid[self.Index(gx, gy)]) * self.resolution


class CostMap:
    def __init__(self) -> None:
        pass
