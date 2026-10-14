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

from dataclasses import dataclass

from wpimath.geometry import Pose2d
from wpimath.trajectory import Trajectory

from .footprint import RobotFootprint

__all__ = [
    "Planner",
    "PlanningRequest",
    "PlanningResult",
]


@dataclass
class PlanningRequest:
    startPose: Pose2d
    goalPose: Pose2d
    field_width: float
    field_length: float
    footprint: RobotFootprint
    maxVel: float
    maxAccel: float
    maxAngVel: float
    maxAngAccel: float


@dataclass
class PlanningResult:
    success: bool
    trajectory: Trajectory | None = None
    reason: str = ""


class Planner:
    def Plan(self, req: PlanningRequest) -> PlanningResult:
        raise NotImplementedError
