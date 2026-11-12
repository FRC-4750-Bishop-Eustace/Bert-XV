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

from collections.abc import Mapping

from hardware import CreateEncoderFromConfig, CreateMotorFromConfig, Encoder, Motor
from utils import Constants, GetObjectList, GetString
from wpimath.geometry import Rotation2d
from wpimath.kinematics import ChassisSpeeds

__all__ = [
    "CreateEncoders",
    "CreateMotors",
    "MakeChassisSpeeds",
]


def MakeChassisSpeeds(
    x: float,
    y: float,
    theta: float,
    field_relative: bool,
    yaw: Rotation2d,
    period: float = 0.02,
) -> ChassisSpeeds:
    """Build the discretized chassis speeds shared by every drivetrain"""

    speeds = ChassisSpeeds.fromFieldRelativeSpeeds(x, y, theta, yaw) if field_relative else ChassisSpeeds(x, y, theta)
    return ChassisSpeeds.discretize(speeds, period)


def CreateMotors(config: Constants) -> dict[str, Motor]:
    """Create every motor listed in a drivetrain configuration, keyed by name"""

    entries = GetObjectList(config, "motors")
    return {GetString(entry, "name"): CreateMotorFromConfig(entry) for entry in entries}


def CreateEncoders(config: Constants, motors: Mapping[str, Motor]) -> dict[str, Encoder]:
    """Create every encoder listed in a drivetrain configuration, keyed by name"""

    entries = GetObjectList(config, "encoders")
    return {GetString(entry, "name"): CreateEncoderFromConfig(entry, motors) for entry in entries}
