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

import math

import wpimath
from hardware import Encoder, Motor
from utils import GetFeedForwardMeters, GetPID, GetProfiledPID, constants
from wpimath.geometry import Rotation2d
from wpimath.kinematics import SwerveModulePosition, SwerveModuleState


class SwerveModule:
    def __init__(
        self,
        lateral_motor: Motor,
        angular_motor: Motor,
        lateral_encoder: Encoder,
        angular_encoder: Encoder,
    ) -> None:
        self.lateral_motor = lateral_motor
        self.lateral_encoder = lateral_encoder
        self.lateral_pid = GetPID(constants.DRIVETRAIN_CONSTANTS, "lateralPID")
        self.lateral_ff = GetFeedForwardMeters(constants.DRIVETRAIN_CONSTANTS, "lateralFeedforward")

        self.angular_motor = angular_motor
        self.angular_encoder = angular_encoder
        self.angular_pid = GetProfiledPID(constants.DRIVETRAIN_CONSTANTS, "angularPID")
        self.angular_ff = GetFeedForwardMeters(constants.DRIVETRAIN_CONSTANTS, "angularFeedforward")

        self.angular_pid.enableContinuousInput(-math.pi, math.pi)

    def GetState(self) -> SwerveModuleState:
        return SwerveModuleState(
            self.lateral_encoder.GetVelocity() or 0.0,
            Rotation2d.fromRotations(self.angular_encoder.GetPosition() or 0.0),
        )

    def GetPosition(self) -> SwerveModulePosition:
        return SwerveModulePosition(
            self.lateral_encoder.GetPosition() or 0.0,
            Rotation2d.fromRotations(self.angular_encoder.GetPosition() or 0.0),
        )

    def SetDesiredState(self, state: SwerveModuleState) -> None:
        rots = Rotation2d.fromRotations(self.angular_encoder.GetPosition() or 0.0)

        state.optimize(rots)
        state.cosineScale(rots)

        self.lateral_motor.SetVoltage(
            self.lateral_pid.calculate(
                self.lateral_encoder.GetVelocity() or 0.0,
                state.speed,
            )
            + self.lateral_ff.calculate(state.speed)
        )
        self.angular_motor.SetVoltage(
            self.angular_pid.calculate(
                wpimath.units.rotationsToRadians(self.angular_encoder.GetPosition() or 0.0),
                state.angle.radians(),
            )
            + self.angular_ff.calculate(self.angular_pid.getSetpoint().velocity)
        )
