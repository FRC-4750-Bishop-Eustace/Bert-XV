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

from hardware import CreateIMUFromConfig
from utils import GetFloat, GetObject, GetPID, GetProfiledPID, Logger, constants
from wpilib import SmartDashboard
from wpimath.estimator import SwerveDrive4PoseEstimator
from wpimath.geometry import Pose2d, Rotation2d, Rotation3d, Translation2d
from wpimath.kinematics import SwerveDrive4Kinematics

from ...subsystem_base import SubsystemBase
from ..helpers import CreateEncoders, CreateMotors, MakeChassisSpeeds
from .module import SwerveModule


class SwerveDrivetrain(SubsystemBase):
    def __init__(self, parent: "Logger") -> None:
        super().__init__(parent, "drivetrain")

    def Initialize(self) -> None:
        motors = CreateMotors(constants.DRIVETRAIN_CONSTANTS)
        encoders = CreateEncoders(constants.DRIVETRAIN_CONSTANTS, motors)
        self.modules: list[SwerveModule] = [
            SwerveModule(  # Front left
                motors["frontLeftLateral"],
                motors["frontLeftAngular"],
                encoders["frontLeftLateral"],
                encoders["frontLeftAngular"],
            ),
            SwerveModule(  # Front right
                motors["frontRightLateral"],
                motors["frontRightAngular"],
                encoders["frontRightLateral"],
                encoders["frontRightAngular"],
            ),
            SwerveModule(  # Back right
                motors["backRightLateral"],
                motors["backRightAngular"],
                encoders["backRightLateral"],
                encoders["backRightAngular"],
            ),
            SwerveModule(  # Back left
                motors["backLeftLateral"],
                motors["backLeftAngular"],
                encoders["backLeftLateral"],
                encoders["backLeftAngular"],
            ),
        ]

        self.gyro = CreateIMUFromConfig(GetObject(constants.DRIVETRAIN_CONSTANTS, "imu"))

        half_length = GetFloat(constants.DRIVETRAIN_CONSTANTS, "chassisHalfLength")
        self.kinematics = SwerveDrive4Kinematics(
            Translation2d(half_length, half_length),
            Translation2d(half_length, -half_length),
            Translation2d(-half_length, -half_length),
            Translation2d(-half_length, half_length),
        )
        self.estimator = SwerveDrive4PoseEstimator(
            self.kinematics,
            (self.gyro.GetRotation() or Rotation3d()).toRotation2d(),
            (
                self.modules[0].GetPosition(),
                self.modules[1].GetPosition(),
                self.modules[2].GetPosition(),
                self.modules[3].GetPosition(),
            ),
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

    def Drive(self, x: float, y: float, theta: float, field_relative: bool, period: float = 0.02) -> None:
        speeds = MakeChassisSpeeds(
            x,
            y,
            theta,
            field_relative,
            Rotation2d.fromDegrees(self.gyro.GetYaw() or 0.0),
            period,
        )
        states = self.kinematics.toSwerveModuleStates(speeds)
        self.kinematics.desaturateWheelSpeeds(states, GetFloat(constants.DRIVETRAIN_CONSTANTS, "maxLateralSpeed"))

        self.modules[0].SetDesiredState(states[0])
        self.modules[1].SetDesiredState(states[1])
        self.modules[2].SetDesiredState(states[2])
        self.modules[3].SetDesiredState(states[3])

    def Stop(self) -> None:
        self.Drive(0.0, 0.0, 0.0, False)
        self.logger.Info("Drivetrain stopped")

    def Periodic(self) -> None:
        self.estimator.update(
            (self.gyro.GetRotation() or Rotation3d()).toRotation2d(),
            (
                self.modules[0].GetPosition(),
                self.modules[1].GetPosition(),
                self.modules[2].GetPosition(),
                self.modules[3].GetPosition(),
            ),
        )

    def GetPose(self) -> Pose2d:
        return self.estimator.getEstimatedPosition()

    def GetPosition(self) -> Translation2d:
        return self.GetPose().translation()

    def GetRotation(self) -> Rotation2d:
        return self.GetPose().rotation()
