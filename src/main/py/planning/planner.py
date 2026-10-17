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

from collections.abc import Callable

from wpimath.geometry import Pose2d
from wpimath.kinematics import SwerveDrive4Kinematics
from wpimath.trajectory import Trajectory

from .astar import AStarPlanner
from .footprint import FootprintChecker, RobotFootprint
from .gridmap import GridMap
from .heading import HeadingOptimizer
from .smoothing import CollisionChecker, Smoother
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
        headingCandidates: int = 32,
        expansionLimit: int = 100000,
        smoothingSpacing: float = 0.05,
        inflationRadius: float = 0.0,
        replanAttempts: int = 3,
        goalTolerance: float = 0.1,
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
        self.smoothingSpacing = smoothingSpacing
        self.replanAttempts = replanAttempts
        self.goalTolerance = goalTolerance

        self.map = GridMap(fieldWidth, fieldLength, resolution, inflationRadius=inflationRadius)
        self.map.BuildClearance()
        self.astar = AStarPlanner(self.map, resolution, expansionLimit)
        self.footprintChecker = FootprintChecker(self.map, footprint, resolution)

        class GridCollisionChecker(CollisionChecker):
            def __init__(self, checker: FootprintChecker) -> None:
                self.checker = checker

            def IsCollision(self, x: float, y: float, theta: float | None = None) -> bool:
                return self.checker.CheckCollision(x, y, theta if theta is not None else 0.0)

            def IsClear(self, x: float, y: float, theta: float | None = None) -> bool:
                return self.checker.IsClear(x, y, theta if theta is not None else 0.0)

        self.collisionChecker = GridCollisionChecker(self.footprintChecker)
        self.smoother = Smoother(self.collisionChecker)
        self.headingOpt = HeadingOptimizer(headingCandidates=headingCandidates)
        self.trajParams = TrajectoryParams(maxVel, maxAccel, 0.0, 0.0)
        self.lastTrajectory: Trajectory | None = None
        self.lastPath: list[tuple[float, float]] | None = None

    def AddObstacleCircle(self, x: float, y: float, radius: float) -> None:
        self.map.AddObstacleCircle(x, y, radius)
        self.map.BuildClearance(force=True)

    def AddObstaclePolygon(self, points: list[tuple[float, float]]) -> None:
        self.map.AddObstaclePolygon(points)
        self.map.BuildClearance(force=True)

    def ClearObstacles(self) -> None:
        self.map.ClearObstacles()
        self.map.BuildClearance(force=True)

    def UpdateObstacles(self, updater: Callable[[GridMap], None]) -> None:
        self.map.UpdateObstacles(updater)
        self.map.BuildClearance(force=True)

    def Plan(self, start: Pose2d, goal: Pose2d, attempt: int = 0) -> Trajectory | None:
        try:
            pres = self.astar.Plan(start.X(), start.Y(), goal.X(), goal.Y())
            if not pres.success or pres.route is None:
                if attempt < self.replanAttempts:
                    # Try with more clearance if possible
                    return self.Plan(start, goal, attempt + 1)

                return None

            spath = self.smoother.Smooth(pres.route.points, spacing=self.smoothingSpacing)
            if len(spath.points) < 2:
                spath.points = list(pres.route.points)

            self.lastPath = list(spath.points)
            hprof = self.headingOpt.Optimize(spath.points, start.rotation().radians(), goal.rotation().radians())
            tb = TrajectoryBuilder(self.trajParams)
            traj = tb.build(spath.points, hprof.headingsRad)
            self.lastTrajectory = traj
            return traj

        except Exception:
            if attempt < self.replanAttempts:
                return self.Plan(start, goal, attempt + 1)

            return None

    def PlanWithRecovery(self, start: Pose2d, goal: Pose2d) -> Trajectory | None:
        traj = self.Plan(start, goal)
        if traj is not None:
            return traj

        return self.FallbackPlan(start, goal)

    def FallbackPlan(self, start: Pose2d, goal: Pose2d) -> Trajectory | None:
        try:
            from wpimath.trajectory import TrajectoryConfig, TrajectoryGenerator

            config = TrajectoryConfig(self.maxVel, self.maxAccel)
            traj = TrajectoryGenerator.generateTrajectory(start, [], goal, config)
            self.lastTrajectory = traj
            return traj

        except Exception:
            return None
