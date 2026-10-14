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
    ) -> None:
        self.fieldWidth = fieldWidth
        self.fieldLength = fieldLength
        self.resolution = resolution
        self.costap = costap or CostMap()

        self.gridx = max(1, math.ceil(self.fieldWidth / self.resolution))
        self.gridy = max(1, math.ceil(self.fieldLength / self.resolution))
        self.grid = bytearray(self.gridx * self.gridy)
        self.clearanceGrid = bytearray(self.gridx * self.gridy)  # Store distance class 0-255

    def ToGrid(self, x: float, y: float) -> GridCoord | None:
        # Allow slight tolerance
        if not (0.0 <= x <= self.fieldWidth + 1e-9 and 0.0 <= y <= self.fieldLength + 1e-9):
            pass

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

    def OutOfBounds(self, gx: int, gy: int) -> bool:
        return gx < 0 or gy < 0 or gx >= self.gridx or gy >= self.gridy

    def InBounds(self, gx: int, gy: int) -> bool:
        return not self.OutOfBounds(gx, gy)

    def BuildClearance(self) -> None:
        # Simple 2D distance transform approximation using BFS from obstacles
        INF = 255
        for i in range(len(self.clearanceGrid)):
            if self.grid[i] == 255:
                self.clearanceGrid[i] = 0
            else:
                self.clearanceGrid[i] = INF

        queue: list[tuple[int, int]] = []
        head = 0
        for gy in range(self.gridy):
            for gx in range(self.gridx):
                if self.clearanceGrid[self.Index(gx, gy)] == 0:
                    queue.append((gx, gy))

        # BFS
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

        while head < len(queue):
            cx, cy = queue[head]
            head += 1
            cval = self.clearanceGrid[self.Index(cx, cy)]

            for nx, ny in neighbors:
                ng = cx + nx
                nh = cy + ny
                if ng < 0 or nh < 0 or ng >= self.gridx or nh >= self.gridy:
                    continue

                if self.clearanceGrid[self.Index(ng, nh)] > cval + 1:
                    nd = min(255, cval + 1)
                    self.clearanceGrid[self.Index(ng, nh)] = nd

                    if nd < INF:
                        queue.append((ng, nh))

    def GetClearance(self, gx: int, gy: int) -> float:
        if self.OutOfBounds(gx, gy):
            return 0.0

        return float(self.clearanceGrid[self.Index(gx, gy)]) * self.resolution


class CostMap:
    def __init__(self) -> None:
        pass
