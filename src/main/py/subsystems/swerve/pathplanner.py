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

from commands2 import Command
from planning.footprint import RobotFootprint
from planning.planner import DynamicPlanner
from wpimath.geometry import Pose2d
from wpimath.trajectory import Trajectory

from .drivetrain import Drivetrain

__all__ = ["DynamicPathPlanner"]


class DynamicPathPlanner:
    def __init__(self, drivetrain: Drivetrain) -> None:
        from utils import DRIVE_CONSTANTS, GetFloat, GetInt

        self.drivetrain = drivetrain
        self.planner = DynamicPlanner(
            fieldWidth=8.069326,
            fieldLength=16.5409880001,
            kinematics=drivetrain.kinematics,
            footprint=RobotFootprint(
                length=2.0 * GetInt(DRIVE_CONSTANTS, "chassisHalfLength"),
                width=2.0 * GetInt(DRIVE_CONSTANTS, "chassisHalfLength"),
                margin=0.15,
            ),
            maxVel=GetFloat(DRIVE_CONSTANTS, "maxLateralSpeed"),
            maxAccel=3.0,
            maxAngVel=GetFloat(DRIVE_CONSTANTS, "maxAngularSpeed"),
            maxAngAccel=6.0,
            resolution=0.05,
            expansionLimit=200000,
            smoothingSpacing=0.05,
            headingCandidates=32,
            inflationRadius=0.15,
            replanAttempts=3,
        )

    def PlanTo(self, goal: Pose2d) -> bool:
        traj = self.planner.Plan(self.drivetrain.GetPose(), goal)
        return traj is not None

    def GenerateTrajectory(self, goal: Pose2d) -> Trajectory | None:
        return self.planner.Plan(self.drivetrain.GetPose(), goal)

    def GenerateTrajectoryFrom(self, start: Pose2d, goal: Pose2d) -> Trajectory | None:
        return self.planner.Plan(start, goal)

    def FollowPath(self, goal: Pose2d) -> Command:
        from commands.pathplanning.follow_trajectory import FollowTrajectory

        traj = self.planner.Plan(self.drivetrain.GetPose(), goal)
        if traj is None:
            traj = self.planner.PlanWithRecovery(self.drivetrain.GetPose(), goal)
        if traj is None:
            from commands2 import cmd

            return cmd.none()

        return FollowTrajectory(
            self.drivetrain,
            traj,
            self.drivetrain.GetPose,
            self.drivetrain.kinematics,
            self.drivetrain.lateralPid,
            self.drivetrain.lateralPid,
            self.drivetrain.angularPid,
            lambda states: self.drivetrain.SetModuleStates((states[0], states[1], states[2], states[3])),
        )

    def FollowPathFrom(self, start: Pose2d, goal: Pose2d) -> Command:
        from commands.pathplanning.follow_trajectory import FollowTrajectory

        traj = self.planner.Plan(start, goal)
        if traj is None:
            from commands2 import cmd

            return cmd.none()

        return FollowTrajectory(
            self.drivetrain,
            traj,
            self.drivetrain.GetPose,
            self.drivetrain.kinematics,
            self.drivetrain.lateralPid,
            self.drivetrain.lateralPid,
            self.drivetrain.angularPid,
            lambda states: self.drivetrain.SetModuleStates((states[0], states[1], states[2], states[3])),
        )

    def AddObstacle(self, x: float, y: float, radius: float) -> None:
        self.planner.AddObstacleCircle(x, y, radius)

    def ClearObstacles(self) -> None:
        self.planner.ClearObstacles()

    def UpdateObstacles(self, updater: Callable[[object], None]) -> None:
        self.planner.UpdateObstacles(updater)
