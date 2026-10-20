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
from hardware import CreateIMU, IMUParameters, IMUType
from utils import GetFloat, GetInt, GetPID, GetProfiledPID, Logger, constants
from wpilib import SmartDashboard
from wpimath.estimator import SwerveDrive4PoseEstimator
from wpimath.geometry import Pose2d, Rotation2d, Rotation3d, Translation2d
from wpimath.kinematics import ChassisSpeeds, SwerveDrive4Kinematics

from .swerve_module import SwerveModule


class Drivetrain(Subsystem):
    def __init__(self, parent: "Logger") -> None:
        super().__init__()
        self.logger = parent.Child("drivetrain")
        self.modules: list[SwerveModule] = [
            SwerveModule(  # Front left
                [
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "frontLeftLateralMotor"),
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "frontLeftAngularMotor"),
                ],
                [
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "frontLeftLateralEncoder"),
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "frontLeftAngularEncoder"),
                ],
            ),
            SwerveModule(  # Front right
                [
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "frontRightLateralMotor"),
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "frontRightAngularMotor"),
                ],
                [
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "frontRightLateralEncoder"),
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "frontRightAngularEncoder"),
                ],
            ),
            SwerveModule(  # Back right
                [
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "backRightLateralMotor"),
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "backRightAngularMotor"),
                ],
                [
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "backRightLateralEncoder"),
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "backRightAngularEncoder"),
                ],
            ),
            SwerveModule(  # Back left
                [
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "backLeftLateralMotor"),
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "backLeftAngularMotor"),
                ],
                [
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "backLeftLateralEncoder"),
                    GetInt(constants.DRIVETRAIN_CONSTANTS, "backLeftAngularEncoder"),
                ],
            ),
        ]

        self.gyro = CreateIMU(IMUType.NAVX, IMUParameters(0))

        half_length = GetInt(constants.DRIVETRAIN_CONSTANTS, "chassisHalfLength")
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

        SmartDashboard.putData("swerve/lateralPID", self.lateralPid)
        SmartDashboard.putData("swerve/angularPID", self.angularPid)

    def Drive(self, x: float, y: float, theta: float, field_relative: float, period: float = 0.02) -> None:
        states = self.kinematics.toSwerveModuleStates(
            ChassisSpeeds.discretize(
                ChassisSpeeds.fromFieldRelativeSpeeds(
                    x,
                    y,
                    theta,
                    Rotation2d.fromDegrees(self.gyro.GetYaw() or 0.0),
                )
                if field_relative
                else ChassisSpeeds(
                    x,
                    y,
                    theta,
                ),
                period,
            ),
        )
        self.kinematics.desaturateWheelSpeeds(states, GetFloat(constants.DRIVETRAIN_CONSTANTS, "maxLateralSpeed"))

        self.modules[0].SetDesiredState(states[0])
        self.modules[1].SetDesiredState(states[1])
        self.modules[2].SetDesiredState(states[2])
        self.modules[3].SetDesiredState(states[3])

    def Stop(self) -> None:
        self.Drive(0.0, 0.0, 0.0, False)
        self.logger.Info("Drivetrain stopped")

    def periodic(self) -> None:
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
