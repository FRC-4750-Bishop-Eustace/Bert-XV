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

from wpimath.geometry import Pose2d
from wpimath.kinematics import SwerveDrive4Kinematics
from wpimath.trajectory import Trajectory

from .astar import AStarPlanner
from .footprint import RobotFootprint
from .gridmap import GridMap
from .heading import HeadingOptimizer
from .smoothing import Smoother
from .trajectory import TrajectoryBuilder, TrajectoryParams

__all__ = ["DynamicPlanner"]


class DynamicPlanner:
    def __init__(
        self,
        fieldWidth: float,
        fieldLength: float,
        kinematics: SwerveDrive4Kinematics,
        footprint: RobotFootprint,
        maxVel: float,
        maxAccel: float,
        maxAngVel: float,
        maxAngAccel: float,
        resolution: float = 0.05,
    ) -> None:
        self.fieldWidth = fieldWidth
        self.fieldLength = fieldLength
        self.kinematics = kinematics
        self.footprint = footprint
        self.maxVel = maxVel
        self.maxAccel = maxAccel
        self.maxAngVel = maxAngVel
        self.maxAngAccel = maxAngAccel
        self.resolution = resolution
        self.map = GridMap(fieldWidth, fieldLength, resolution)
        self.map.BuildClearance()
        self.astar = AStarPlanner(self.map, resolution)
        self.smoother = Smoother()
        self.headingOpt = HeadingOptimizer(headingCandidates=32)
        self.trajParams = TrajectoryParams(maxVel, maxAccel, 0.0, 0.0)

    def Plan(self, start: Pose2d, goal: Pose2d) -> Trajectory | None:
        pres = self.astar.Plan(start.X(), start.Y(), goal.X(), goal.Y())
        if not pres.success or pres.route is None:
            return None

        spath = self.smoother.smooth(pres.route.points, spacing=0.05)
        if len(spath.points) < 2:
            spath.points = list(pres.route.points)

        hprof = self.headingOpt.Optimize(spath.points, start.rotation().radians(), goal.rotation().radians())
        tb = TrajectoryBuilder(self.trajParams)
        traj = tb.build(spath.points, hprof.headingsRad)

        return traj
