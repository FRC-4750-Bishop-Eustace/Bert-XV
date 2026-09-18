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

from commands2 import Command
from subsystems import Drivetrain
from utils import CONSTANTS, GetFloat, GetInt, GetObject
from wpilib import DriverStation, SmartDashboard
from wpilib.interfaces import GenericHID
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter

_CTRL_CONSTANTS = GetObject(CONSTANTS, "controllers")
_PORT_CONSTANTS = GetObject(CONSTANTS, "ports")
_DRIVE_CONSTANTS = GetObject(GetObject(CONSTANTS, "subsystems"), "drivetrain")


class DriveWithJoystick(Command):
    def __init__(self, swerve: Drivetrain, controller: GenericHID) -> None:
        self.swerve = swerve
        self.controller = controller
        self.slew_rates: list[SlewRateLimiter] = [
            SlewRateLimiter(GetFloat(_CTRL_CONSTANTS, "lateralSlewRate")),  # X/Y
            SlewRateLimiter(GetFloat(_CTRL_CONSTANTS, "angularSlewRate")),  # Theta
        ]
        self.field_relative = True

        self.addRequirements(self.swerve)

        SmartDashboard.putBoolean("FieldRelative", self.field_relative)

    def ToggleFieldRelative(self) -> None:
        self.field_relative = not self.field_relative
        SmartDashboard.putBoolean("FieldRelative", self.field_relative)

        self.swerve.logger.Info(
            f"Field relative toggled {'on' if self.field_relative else 'off'}", field_relative=self.field_relative
        )

    def ResetGyro(self) -> None:
        self.swerve.logger.Info("Resetting IMU")
        self.swerve.gyro.Reset()

    def execute(self) -> None:
        if not DriverStation.isTeleopEnabled():
            return

        x = -self.slew_rates[0].calculate(
            applyDeadband(
                self.controller.getRawAxis(GetInt(_PORT_CONSTANTS, "axisLeftY") or -1),  # -Y
                GetFloat(_CTRL_CONSTANTS, "lateralDeadband"),
            )
            * GetFloat(_DRIVE_CONSTANTS, "maxLateralSpeed"),
        )
        y = -self.slew_rates[0].calculate(
            applyDeadband(
                self.controller.getRawAxis(GetInt(_PORT_CONSTANTS, "axisLeftX") or -1),  # -X
                GetFloat(_CTRL_CONSTANTS, "lateralDeadband"),
            )
            * GetFloat(_DRIVE_CONSTANTS, "maxLateralSpeed"),
        )
        theta = -self.slew_rates[1].calculate(
            applyDeadband(
                self.controller.getRawAxis(GetInt(_PORT_CONSTANTS, "axisRightX") or -1),  # +X
                GetFloat(_CTRL_CONSTANTS, "angularDeadband"),
            )
            * GetFloat(_DRIVE_CONSTANTS, "maxAngularSpeed"),
        )

        if self.controller.getPOV() == (GetInt(_PORT_CONSTANTS, "dpadUp") or -1):
            x = GetFloat(_DRIVE_CONSTANTS, "microLateralSpeed")
        if self.controller.getPOV() == (GetInt(_PORT_CONSTANTS, "dpadRight") or -1):
            y = -GetFloat(_DRIVE_CONSTANTS, "microLateralSpeed")
        if self.controller.getPOV() == (GetInt(_PORT_CONSTANTS, "dpadDown") or -1):
            x = -GetFloat(_DRIVE_CONSTANTS, "microLateralSpeed")
        if self.controller.getPOV() == (GetInt(_PORT_CONSTANTS, "dpadLeft") or -1):
            y = GetFloat(_DRIVE_CONSTANTS, "microLateralSpeed")

        if self.controller.getRawButton(GetInt(_PORT_CONSTANTS, "L1")) == 1:
            theta = GetFloat(_DRIVE_CONSTANTS, "microAngularSpeed")
        if self.controller.getRawButton(GetInt(_PORT_CONSTANTS, "R1")) == 1:
            theta = -GetFloat(_DRIVE_CONSTANTS, "microAngularSpeed")

        self.swerve.Drive(x, y, theta, self.field_relative)
