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
from utils import CONSTANTS, GetFloat, GetInt, GetObject, GetPID, GetProfiledPID, Logger
from wpilib import SmartDashboard
from wpimath.estimator import SwerveDrive4PoseEstimator
from wpimath.geometry import Pose2d, Rotation2d, Rotation3d, Translation2d
from wpimath.kinematics import ChassisSpeeds, SwerveDrive4Kinematics

from .swerve_module import SwerveModule

_DRIVE_CONSTANTS = GetObject(GetObject(CONSTANTS, "subsystems"), "drivetrain")


class Drivetrain(Subsystem):
    def __init__(self, parent: "Logger") -> None:
        super().__init__()
        self.logger = parent.Child("drivetrain")
        self.modules: list[SwerveModule] = [
            SwerveModule(  # Front left
                [
                    GetInt(_DRIVE_CONSTANTS, "frontLeftLateralMotor"),
                    GetInt(_DRIVE_CONSTANTS, "frontLeftAngularMotor"),
                ],
                [
                    GetInt(_DRIVE_CONSTANTS, "frontLeftLateralEncoder"),
                    GetInt(_DRIVE_CONSTANTS, "frontLeftAngularEncoder"),
                ],
            ),
            SwerveModule(  # Front right
                [
                    GetInt(_DRIVE_CONSTANTS, "frontRightLateralMotor"),
                    GetInt(_DRIVE_CONSTANTS, "frontRightAngularMotor"),
                ],
                [
                    GetInt(_DRIVE_CONSTANTS, "frontRightLateralEncoder"),
                    GetInt(_DRIVE_CONSTANTS, "frontRightAngularEncoder"),
                ],
            ),
            SwerveModule(  # Back right
                [
                    GetInt(_DRIVE_CONSTANTS, "backRightLateralMotor"),
                    GetInt(_DRIVE_CONSTANTS, "backRightAngularMotor"),
                ],
                [
                    GetInt(_DRIVE_CONSTANTS, "backRightLateralEncoder"),
                    GetInt(_DRIVE_CONSTANTS, "backRightAngularEncoder"),
                ],
            ),
            SwerveModule(  # Back left
                [
                    GetInt(_DRIVE_CONSTANTS, "backLeftLateralMotor"),
                    GetInt(_DRIVE_CONSTANTS, "backLeftAngularMotor"),
                ],
                [
                    GetInt(_DRIVE_CONSTANTS, "backLeftLateralEncoder"),
                    GetInt(_DRIVE_CONSTANTS, "backLeftAngularEncoder"),
                ],
            ),
        ]

        self.gyro = CreateIMU(IMUType.NAVX, IMUParameters(0))

        self.kinematics = SwerveDrive4Kinematics(
            Translation2d(GetInt(_DRIVE_CONSTANTS, "chassisHalfLength"), GetInt(_DRIVE_CONSTANTS, "chassisHalfLength")),
            Translation2d(
                GetInt(_DRIVE_CONSTANTS, "chassisHalfLength"), -GetInt(_DRIVE_CONSTANTS, "chassisHalfLength")
            ),
            Translation2d(
                -GetInt(_DRIVE_CONSTANTS, "chassisHalfLength"), -GetInt(_DRIVE_CONSTANTS, "chassisHalfLength")
            ),
            Translation2d(
                -GetInt(_DRIVE_CONSTANTS, "chassisHalfLength"), GetInt(_DRIVE_CONSTANTS, "chassisHalfLength")
            ),
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

        SmartDashboard.putData("swerve/lateralPID", GetPID(_DRIVE_CONSTANTS, "lateralPID"))
        SmartDashboard.putData("swerve/angularPID", GetProfiledPID(_DRIVE_CONSTANTS, "angularPID"))

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
        self.kinematics.desaturateWheelSpeeds(states, GetFloat(_DRIVE_CONSTANTS, "maxLateralSpeed"))

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
