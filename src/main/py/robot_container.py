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

import commands2.cmd as cmd
from commands import DriveWithJoystick
from commands2 import Command, InstantCommand
from commands2.button import JoystickButton
from subsystems import Drivetrain
from utils import CONSTANTS, GetInt, GetObject, Logger
from wpilib import Field2d, Joystick, PS4Controller, SmartDashboard

_CTRL_CONSTANTS = GetObject(CONSTANTS, "controllers")
_PORT_CONSTANTS = GetObject(CONSTANTS, "ports")


class RobotContainer:
    def __init__(self, logger: "Logger") -> None:
        self.logger = logger

        self.controller = PS4Controller(GetInt(_CTRL_CONSTANTS, "controllerPort"))
        self.dashboard = Joystick(GetInt(_CTRL_CONSTANTS, "dashboardPort"))

        self.field = Field2d()

        self.swerve = Drivetrain(self.logger)
        self.drive = DriveWithJoystick(self.swerve, self.controller)

        SmartDashboard.putData("Field", self.field)

        self.SetDefaults()
        self.ConfigureBindings()

    def SetDefaults(self) -> None:
        self.swerve.setDefaultCommand(self.drive)

    def ConfigureBindings(self) -> None:
        JoystickButton(self.controller, GetInt(_PORT_CONSTANTS, "faceDown")).onTrue(
            InstantCommand(
                self.drive.ToggleFieldRelative,
                self.swerve,
            ),
        )
        JoystickButton(self.controller, GetInt(_PORT_CONSTANTS, "faceUp")).onTrue(
            InstantCommand(
                self.drive.ToggleFieldRelative,
                self.swerve,
            ),
        )

    def UpdateField(self) -> None:
        self.field.setRobotPose(self.swerve.GetPose())

    def GetAutonomousCommand(self) -> Command:
        return cmd.none()
