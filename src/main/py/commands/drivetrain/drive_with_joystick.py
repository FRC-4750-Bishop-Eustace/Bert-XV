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

from typing import cast

from commands2 import Command, Subsystem
from subsystems import Drivetrain
from utils import GetFloat, GetInt, constants
from wpilib import DriverStation, SmartDashboard
from wpilib.interfaces import GenericHID
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from wpimath.geometry import Translation2d


class DriveWithJoystick(Command):
    def __init__(self, drivetrain: Drivetrain, controller: GenericHID, point: Translation2d | None = None) -> None:
        self.drivetrain = drivetrain
        self.controller = controller
        self.point = point
        self.slew_rates: list[SlewRateLimiter] = [
            SlewRateLimiter(GetFloat(constants.CONTROLLERS_CONSTANTS, "lateralSlewRate")),  # X/Y
            SlewRateLimiter(GetFloat(constants.CONTROLLERS_CONSTANTS, "angularSlewRate")),  # Theta
        ]
        self.field_relative = True

        self.addRequirements(cast(Subsystem, self.drivetrain))

        SmartDashboard.putBoolean("FieldRelative", self.field_relative)

    def ToggleFieldRelative(self) -> None:
        self.field_relative = not self.field_relative
        SmartDashboard.putBoolean("FieldRelative", self.field_relative)

        self.drivetrain.logger.Info(
            f"Field relative toggled {'on' if self.field_relative else 'off'}", field_relative=self.field_relative
        )

    def ResetGyro(self) -> None:
        self.drivetrain.logger.Info("Resetting IMU")
        self.drivetrain.gyro.Reset()

    def SetLockingPoint(self, point: Translation2d | None) -> None:
        self.point = point
        self.drivetrain.angularPid.reset(self.drivetrain.angularPid.getGoal())

    def execute(self) -> None:
        if not DriverStation.isTeleopEnabled():
            return

        x = -self.slew_rates[0].calculate(
            applyDeadband(
                self.controller.getRawAxis(GetInt(constants.PORTS_CONSTANTS, "axisLeftY", -1)),  # -Y
                GetFloat(constants.CONTROLLERS_CONSTANTS, "lateralDeadband"),
            )
            * GetFloat(constants.DRIVETRAIN_CONSTANTS, "maxLateralSpeed"),
        )
        y = -self.slew_rates[0].calculate(
            applyDeadband(
                self.controller.getRawAxis(GetInt(constants.PORTS_CONSTANTS, "axisLeftX", -1)),  # -X
                GetFloat(constants.CONTROLLERS_CONSTANTS, "lateralDeadband"),
            )
            * GetFloat(constants.DRIVETRAIN_CONSTANTS, "maxLateralSpeed"),
        )

        if self.controller.getPOV() == GetInt(constants.PORTS_CONSTANTS, "dpadUp", -1):
            x = GetFloat(constants.DRIVETRAIN_CONSTANTS, "microLateralSpeed")
        if self.controller.getPOV() == GetInt(constants.PORTS_CONSTANTS, "dpadRight", -1):
            y = -GetFloat(constants.DRIVETRAIN_CONSTANTS, "microLateralSpeed")
        if self.controller.getPOV() == GetInt(constants.PORTS_CONSTANTS, "dpadDown", -1):
            x = -GetFloat(constants.DRIVETRAIN_CONSTANTS, "microLateralSpeed")
        if self.controller.getPOV() == GetInt(constants.PORTS_CONSTANTS, "dpadLeft", -1):
            y = GetFloat(constants.DRIVETRAIN_CONSTANTS, "microLateralSpeed")

        theta: float = 0.0
        if not self.point:  # Point locking disabled
            theta = -self.slew_rates[1].calculate(
                applyDeadband(
                    self.controller.getRawAxis(GetInt(constants.PORTS_CONSTANTS, "axisRightX", -1)),  # +X
                    GetFloat(constants.CONTROLLERS_CONSTANTS, "angularDeadband"),
                )
                * GetFloat(constants.DRIVETRAIN_CONSTANTS, "maxAngularSpeed"),
            )
            if self.controller.getRawButton(GetInt(constants.PORTS_CONSTANTS, "L1")) == 1:
                theta = GetFloat(constants.DRIVETRAIN_CONSTANTS, "microAngularSpeed")
            if self.controller.getRawButton(GetInt(constants.PORTS_CONSTANTS, "R1")) == 1:
                theta = -GetFloat(constants.DRIVETRAIN_CONSTANTS, "microAngularSpeed")
        else:  # Point locking enabled
            target = (self.point - self.drivetrain.GetPosition()).angle()
            theta = self.drivetrain.angularPid.calculate(self.drivetrain.GetRotation().radians(), target.radians())

        self.drivetrain.Drive(x, y, theta, self.field_relative)
