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

import heapq
import math
from dataclasses import dataclass
from typing import Protocol

from .gridmap import GridCoord

__all__ = [
    "AStarPlanner",
    "PlanningResult",
    "Route",
]


@dataclass
class Route:
    points: list[tuple[float, float]]  # World coordinates
    lengthM: float = 0.0


@dataclass
class PlanningResult:
    success: bool
    route: Route | None = None
    nodesExpanded: int = 0
    reason: str = ""


class OccupancyProvider(Protocol):
    def IsBlocked(self, gx: int, gy: int) -> bool:
        raise NotImplementedError

    def OutOfBounds(self, gx: int, gy: int) -> bool:
        raise NotImplementedError

    def ToGrid(self, x: float, y: float) -> GridCoord | None:
        raise NotImplementedError

    def ToWorld(self, gx: int, gy: int) -> tuple[float, float]:
        raise NotImplementedError

    def GetClearance(self, gx: int, gy: int) -> float:
        raise NotImplementedError


class AStarPlanner:
    def __init__(self, map: OccupancyProvider, resolution: float = 0.05) -> None:
        self.map = map
        self.resolution = resolution
        self.diagonalCost = math.sqrt(2.0)
        self.cardCost = 1.0
        self.clearance_penalty = 0.1  # Cost per meter of reduced clearance
        self.expansion_limit = 10000

    def Heuristic(self, gx1: int, gy1: int, gx2: int, gy2: int) -> float:
        dx = abs(gx1 - gx2)
        dy = abs(gy1 - gy2)
        return self.cardCost * (dx + dy) + (self.diagonalCost - 2.0 * self.cardCost) * min(dx, dy)

    def Plan(self, startX: float, startY: float, goalX: float, goalY: float) -> PlanningResult:
        s = self.map.ToGrid(startX, startY)
        g = self.map.ToGrid(goalX, goalY)
        if s is None or g is None:
            return PlanningResult(False, reason="start or goal out of bounds")

        if self.map.IsBlocked(s.gx, s.gy) or self.map.IsBlocked(g.gx, g.gy):
            return PlanningResult(False, reason="start or goal blocked")

        if s.gx == g.gx and s.gy == g.gy:
            return PlanningResult(True, Route(points=[(startX, startY)]), 1, "zero distance")

        maxG = 1000
        if abs(s.gx - g.gx) > maxG or abs(s.gy - g.gy) > maxG:
            return PlanningResult(False, reason="goal too far")

        # A* algorithm
        openHeap: list[tuple[float, int, int]] = []
        nodesExp = 0

        openSet: set[tuple[int, int]] = set()
        gScore: dict[tuple[int, int], float] = {}
        came_from: dict[tuple[int, int], tuple[int, int]] = {}
        heapq.heappush(openHeap, (0.0, s.gx, s.gy))
        openSet.add((s.gx, s.gy))
        gScore[(s.gx, s.gy)] = 0.0
        dirs8 = [
            (-1, -1),
            (0, -1),
            (1, -1),
            (-1, 0),
            (1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
        ]

        while openHeap:
            if nodesExp > self.expansion_limit:
                return PlanningResult(False, reason="expansion limit exceeded", nodesExpanded=nodesExp)

            _, cx, cy = heapq.heappop(openHeap)
            if (cx, cy) not in openSet:
                continue
            if cx == g.gx and cy == g.gy:
                break

            openSet.discard((cx, cy))
            for dx, dy in dirs8:
                nx, ny = cx + dx, cy + dy
                if self.map.OutOfBounds(nx, ny):
                    continue
                if self.map.IsBlocked(nx, ny):
                    continue

                # Prevent diagonal corner cutting
                if dx != 0 and dy != 0 and (self.map.IsBlocked(cx + dx, cy) or self.map.IsBlocked(cx, cy + dy)):
                    continue

                moveCost = self.diagonalCost if (dx != 0 and dy != 0) else self.cardCost
                clearance = self.map.GetClearance(nx, ny)
                if clearance < 0.1:
                    moveCost += (0.1 - clearance) * 10.0

                ng = gScore.get((cx, cy), 1e18) + moveCost
                keyn = (nx, ny)
                if ng < gScore.get(keyn, 1e18):
                    nodesExp += 1
                    came_from[keyn] = (cx, cy)
                    gScore[keyn] = ng
                    f = ng + self.Heuristic(nx, ny, g.gx, g.gy)

                    heapq.heappush(openHeap, (f, nx, ny))
                    openSet.add(keyn)

        if (g.gx, g.gy) not in came_from and not (s.gx == g.gx and s.gy == g.gy):
            return PlanningResult(False, reason="goal not reached", nodesExpanded=nodesExp)

        path: list[tuple[int, int]] = []
        cur = (g.gx, g.gy)
        while cur != (s.gx, s.gy):
            path.append(cur)
            if cur not in came_from:
                break

            cur = came_from[cur]

        path.append((s.gx, s.gy))
        path.reverse()
        points: list[tuple[float, float]] = []

        for gx, gy in path:
            wx, wy = self.map.ToWorld(gx, gy)
            points.append((wx, wy))

        return PlanningResult(True, Route(points=points), nodesExpanded=nodesExp, reason="ok")
