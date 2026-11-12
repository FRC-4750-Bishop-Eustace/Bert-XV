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

from typing import TYPE_CHECKING, Protocol

from hardware import IMU
from utils import GetString, Logger, constants
from wpimath.controller import ProfiledPIDController
from wpimath.geometry import Pose2d, Rotation2d, Translation2d

if TYPE_CHECKING:
    from .mecanum.drivetrain import MecanumDrivetrain
    from .swerve.drivetrain import SwerveDrivetrain

    type DrivetrainType = MecanumDrivetrain | SwerveDrivetrain


class PoseEstimator(Protocol):
    """The pose estimator operations shared by the drivetrain and vision code"""

    def getEstimatedPosition(self) -> Pose2d:
        raise NotImplementedError

    def addVisionMeasurement(self, visionRobotPose: Pose2d, timestamp: float) -> None:
        raise NotImplementedError

    def setVisionMeasurementStdDevs(self, visionMeasurementStdDevs: tuple[float, float, float]) -> None:
        raise NotImplementedError


class Drivetrain(Protocol):
    """Interface every drivetrain implements so commands and subsystems stay generic"""

    @property
    def logger(self) -> Logger:
        raise NotImplementedError

    @property
    def gyro(self) -> IMU:
        raise NotImplementedError

    @property
    def estimator(self) -> PoseEstimator:
        raise NotImplementedError

    @property
    def angularPid(self) -> ProfiledPIDController:
        raise NotImplementedError

    def Drive(self, x: float, y: float, theta: float, field_relative: bool, period: float = 0.02) -> None:
        raise NotImplementedError

    def Stop(self) -> None:
        raise NotImplementedError

    def GetPose(self) -> Pose2d:
        raise NotImplementedError

    def GetPosition(self) -> Translation2d:
        raise NotImplementedError

    def GetRotation(self) -> Rotation2d:
        raise NotImplementedError

    def periodic(self) -> None:
        raise NotImplementedError


def CreateDrivetrain(parent: Logger) -> DrivetrainType:
    """Create the drivetrain selected by the ``type`` entry in the drivetrain constants"""

    kind = GetString(constants.DRIVETRAIN_CONSTANTS, "type").strip().lower()
    if kind == "swerve":
        from .swerve.drivetrain import SwerveDrivetrain

        return SwerveDrivetrain(parent)
    if kind == "mecanum":
        from .mecanum.drivetrain import MecanumDrivetrain

        return MecanumDrivetrain(parent)

    raise ValueError(f"Unknown drivetrain type '{kind}' (expected 'swerve' or 'mecanum')")
