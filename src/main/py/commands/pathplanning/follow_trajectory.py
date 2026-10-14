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

import contextlib
from collections.abc import Callable, Sequence

from commands2 import Command, Subsystem
from wpimath.controller import (
    HolonomicDriveController,
    PIDController,
    ProfiledPIDController,
    ProfiledPIDControllerRadians,
)
from wpimath.geometry import Pose2d
from wpimath.kinematics import SwerveDrive4Kinematics, SwerveModuleState
from wpimath.trajectory import Trajectory

__all__ = ["FollowTrajectory"]


class FollowTrajectory(Command):
    def __init__(
        self,
        subsystem: Subsystem,
        trajectory: Trajectory,
        poseSupplier: Callable[[], Pose2d],
        kinematics: SwerveDrive4Kinematics,
        xController: PIDController,
        yController: PIDController,
        thetaController: ProfiledPIDControllerRadians | ProfiledPIDController,
        output: Callable[[Sequence[SwerveModuleState]], None],
    ) -> None:
        from commands2 import SwerveControllerCommand
        from wpimath.controller import ProfiledPIDControllerRadians

        tc: ProfiledPIDControllerRadians
        if isinstance(thetaController, ProfiledPIDControllerRadians):
            tc = thetaController
        else:
            from wpimath.trajectory import TrapezoidProfileRadians

            tc = ProfiledPIDControllerRadians(
                thetaController.getP(),
                thetaController.getI(),
                thetaController.getD(),
                TrapezoidProfileRadians.Constraints(
                    thetaController.getConstraints().maxVelocity,
                    thetaController.getConstraints().maxAcceleration,
                ),
            )
            try:
                goal = thetaController.getGoal()
                tc.setGoal(goal.position)
            except Exception:
                with contextlib.suppress(Exception):
                    tc.setGoal(thetaController.getSetpoint().position)

        self.cmd: Command = SwerveControllerCommand(
            trajectory,
            poseSupplier,
            kinematics,
            HolonomicDriveController(xController, yController, tc),
            output,
            (subsystem,),
        )

        self.addRequirements(subsystem)

    def initialize(self) -> None:
        self.cmd.initialize()  # type: ignore[no-untyped-call]

    def execute(self) -> None:
        self.cmd.execute()  # type: ignore[no-untyped-call]

    def end(self, interrupted: bool) -> None:
        self.cmd.end(interrupted)

    def isFinished(self) -> bool:
        return bool(self.cmd.isFinished())
