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

__all__ = [
    "HeadingOptimizer",
    "HeadingProfile",
]


@dataclass
class HeadingProfile:
    headingsRad: list[float]


class HeadingOptimizer:
    def __init__(self, headingCandidates: int = 32) -> None:
        self.headingCandidates = headingCandidates

    def Wrap(self, a: float) -> float:
        while a > math.pi:
            a -= 2.0 * math.pi
        while a < -math.pi:
            a += 2.0 * math.pi
        return a

    def Optimize(
        self,
        pathPoints: Sequence[tuple[float, float]],
        startHeading: float,
        goalHeading: float,
    ) -> HeadingProfile:
        if len(pathPoints) == 0:
            return HeadingProfile([self.Wrap(startHeading)])

        n = len(pathPoints)
        cand = self.headingCandidates

        headingsCand: list[float] = [self.Wrap(-math.pi + 2.0 * math.pi * i / cand) for i in range(cand)]

        res: list[float] = [0.0] * n

        best = 0
        bestd = abs(self.Wrap(headingsCand[0] - startHeading))
        for i in range(cand):
            d = abs(self.Wrap(headingsCand[i] - startHeading))
            if d < bestd:
                bestd = d
                best = i

        res[0] = headingsCand[best]
        for i in range(1, n):
            prev = res[i - 1]
            best = 0
            bestc = 1e18

            for j in range(cand):
                h = headingsCand[j]
                ad = abs(self.Wrap(h - prev))
                td = 0.0
                if i == n - 1:
                    td = abs(self.Wrap(h - goalHeading)) * 2.0

                cost = ad + td
                if cost < bestc:
                    bestc = cost
                    best = j

            res[i] = headingsCand[best]

        res[-1] = self.Wrap(goalHeading)
        return HeadingProfile(res)
