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

from commands2 import Subsystem
from hardware import CreateIMUFromConfig
from utils import GetFloat, GetObject, GetPID, GetProfiledPID, Logger, constants
from wpilib import SmartDashboard
from wpimath.estimator import MecanumDrivePoseEstimator
from wpimath.geometry import Pose2d, Rotation2d, Rotation3d, Translation2d
from wpimath.kinematics import MecanumDriveKinematics, MecanumDriveWheelPositions

from ..drivetrain import CreateEncoders, CreateMotors, MakeChassisSpeeds
from .module import MecanumModule


class MecanumDrivetrain(Subsystem):
    def __init__(self, parent: "Logger") -> None:
        super().__init__()
        self.logger = parent.Child("drivetrain")

        motors = CreateMotors(constants.DRIVETRAIN_CONSTANTS)
        encoders = CreateEncoders(constants.DRIVETRAIN_CONSTANTS, motors)
        self.modules: list[MecanumModule] = [
            MecanumModule(motors["frontLeft"], encoders["frontLeft"]),  # Front left
            MecanumModule(motors["frontRight"], encoders["frontRight"]),  # Front right
            MecanumModule(motors["backLeft"], encoders["backLeft"]),  # Back left
            MecanumModule(motors["backRight"], encoders["backRight"]),  # Back right
        ]

        self.gyro = CreateIMUFromConfig(GetObject(constants.DRIVETRAIN_CONSTANTS, "imu"))

        half_length = GetFloat(constants.DRIVETRAIN_CONSTANTS, "chassisHalfLength")
        self.kinematics = MecanumDriveKinematics(
            Translation2d(-half_length, half_length),
            Translation2d(half_length, half_length),
            Translation2d(-half_length, -half_length),
            Translation2d(half_length, -half_length),
        )

        self.estimator = MecanumDrivePoseEstimator(
            self.kinematics,
            (self.gyro.GetRotation() or Rotation3d()).toRotation2d(),
            self.GetWheelPositions(),
            Pose2d(),
            (0.05, 0.05, math.pi / 36),
            (0.5, 0.5, math.pi / 6),
        )

        self.gyro.Reset()
        self.logger.Debug("IMU reset on startup")

        self.lateralPid = GetPID(constants.DRIVETRAIN_CONSTANTS, "lateralPID")
        self.angularPid = GetProfiledPID(constants.DRIVETRAIN_CONSTANTS, "angularPID")
        self.angularPid.enableContinuousInput(-math.pi, math.pi)

        SmartDashboard.putData("drivetrain/lateralPID", self.lateralPid)
        SmartDashboard.putData("drivetrain/angularPID", self.angularPid)

    def GetWheelPositions(self) -> MecanumDriveWheelPositions:
        positions = MecanumDriveWheelPositions()
        positions.frontLeft = self.modules[0].GetPosition()
        positions.frontRight = self.modules[1].GetPosition()
        positions.rearLeft = self.modules[2].GetPosition()
        positions.rearRight = self.modules[3].GetPosition()
        return positions

    def Drive(self, x: float, y: float, theta: float, field_relative: bool, period: float = 0.02) -> None:
        speeds = MakeChassisSpeeds(
            x,
            y,
            theta,
            field_relative,
            Rotation2d.fromDegrees(self.gyro.GetYaw() or 0.0),
            period,
        )
        states = self.kinematics.toWheelSpeeds(speeds)
        states.desaturate(GetFloat(constants.DRIVETRAIN_CONSTANTS, "maxLateralSpeed"))

        self.modules[0].SetDesiredState(states.frontLeft)
        self.modules[1].SetDesiredState(states.frontRight)
        self.modules[2].SetDesiredState(states.rearLeft)
        self.modules[3].SetDesiredState(states.rearRight)

    def Stop(self) -> None:
        self.Drive(0.0, 0.0, 0.0, False)
        self.logger.Info("Drivetrain stopped")

    def periodic(self) -> None:
        self.estimator.update(
            (self.gyro.GetRotation() or Rotation3d()).toRotation2d(),
            self.GetWheelPositions(),
        )

    def GetPose(self) -> Pose2d:
        return self.estimator.getEstimatedPosition()

    def GetPosition(self) -> Translation2d:
        return self.GetPose().translation()

    def GetRotation(self) -> Rotation2d:
        return self.GetPose().rotation()
