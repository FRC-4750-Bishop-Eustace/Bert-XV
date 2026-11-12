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

from collections.abc import Mapping
from typing import TYPE_CHECKING, Protocol

from hardware import IMU, CreateEncoderFromConfig, CreateMotorFromConfig, Encoder, Motor
from utils import Constants, GetObjectList, GetString, Logger, constants
from wpimath.controller import ProfiledPIDController
from wpimath.geometry import Pose2d, Rotation2d, Translation2d
from wpimath.kinematics import ChassisSpeeds

if TYPE_CHECKING:
    from .mecanum.drivetrain import MecanumDrivetrain
    from .swerve.drivetrain import SwerveDrivetrain

    type DrivetrainType = MecanumDrivetrain | SwerveDrivetrain


class PoseEstimator(Protocol):
    """The pose estimator operations shared by the drivetrain and vision code."""

    def getEstimatedPosition(self) -> Pose2d: ...

    def addVisionMeasurement(self, visionRobotPose: Pose2d, timestamp: float) -> None: ...

    def setVisionMeasurementStdDevs(self, visionMeasurementStdDevs: tuple[float, float, float]) -> None: ...


class Drivetrain(Protocol):
    """Interface every drivetrain implements so commands and subsystems stay generic."""

    @property
    def logger(self) -> Logger: ...

    @property
    def gyro(self) -> IMU: ...

    @property
    def estimator(self) -> PoseEstimator: ...

    @property
    def angularPid(self) -> ProfiledPIDController: ...

    def Drive(self, x: float, y: float, theta: float, field_relative: bool, period: float = 0.02) -> None: ...

    def Stop(self) -> None: ...

    def GetPose(self) -> Pose2d: ...

    def GetPosition(self) -> Translation2d: ...

    def GetRotation(self) -> Rotation2d: ...

    def periodic(self) -> None: ...


def MakeChassisSpeeds(
    x: float,
    y: float,
    theta: float,
    field_relative: bool,
    yaw: Rotation2d,
    period: float = 0.02,
) -> ChassisSpeeds:
    """Build the discretized chassis speeds shared by every drivetrain."""

    speeds = ChassisSpeeds.fromFieldRelativeSpeeds(x, y, theta, yaw) if field_relative else ChassisSpeeds(x, y, theta)
    return ChassisSpeeds.discretize(speeds, period)


def CreateMotors(config: Constants) -> dict[str, Motor]:
    """Create every motor listed in a drivetrain configuration, keyed by name."""

    entries = GetObjectList(config, "motors")
    return {GetString(entry, "name"): CreateMotorFromConfig(entry) for entry in entries}


def CreateEncoders(config: Constants, motors: Mapping[str, Motor]) -> dict[str, Encoder]:
    """Create every encoder listed in a drivetrain configuration, keyed by name."""

    entries = GetObjectList(config, "encoders")
    return {GetString(entry, "name"): CreateEncoderFromConfig(entry, motors) for entry in entries}


def CreateDrivetrain(parent: Logger) -> DrivetrainType:
    """Create the drivetrain selected by the ``type`` entry in the drivetrain constants."""

    kind = GetString(constants.DRIVETRAIN_CONSTANTS, "type").strip().lower()
    if kind == "swerve":
        from .swerve.drivetrain import SwerveDrivetrain

        return SwerveDrivetrain(parent)
    if kind == "mecanum":
        from .mecanum.drivetrain import MecanumDrivetrain

        return MecanumDrivetrain(parent)

    raise ValueError(f"Unknown drivetrain type '{kind}' (expected 'swerve' or 'mecanum')")
