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

from collections.abc import Hashable

import commands2.cmd as cmd
from commands import DriveWithJoystick
from commands2 import Command
from commands2.button import JoystickButton
from subsystems import Drivetrain
from utils import CTRL_CONSTANTS, PORT_CONSTANTS, GetInt, Logger
from wpilib import Field2d, Joystick, PS4Controller, SendableChooser, SmartDashboard


class RobotContainer:
    def __init__(self, logger: "Logger") -> None:
        self.logger = logger

        self.controller = PS4Controller(GetInt(CTRL_CONSTANTS, "controllerPort"))
        self.dashboard = Joystick(GetInt(CTRL_CONSTANTS, "dashboardPort"))

        self.field = Field2d()

        self.auto_commands: dict[Hashable, Command] = {
            "None": cmd.none(),
        }
        self.auto_chooser: SendableChooser = SendableChooser()
        for name in self.auto_commands:
            self.auto_chooser.addOption(str(name), str(name))
        self.selector = cmd.select(self.auto_commands, self.auto_chooser.getSelected)

        self.swerve = Drivetrain(self.logger)
        self.drive = DriveWithJoystick(self.swerve, self.controller)

        SmartDashboard.putData("Field", self.field)
        SmartDashboard.putData("Auto Choices", self.auto_chooser)

        self.SetDefaults()
        self.ConfigureBindings()

    def SetDefaults(self) -> None:
        self.swerve.setDefaultCommand(self.drive)

    def ConfigureBindings(self) -> None:
        JoystickButton(self.controller, GetInt(PORT_CONSTANTS, "faceDown")).onTrue(
            cmd.runOnce(
                self.drive.ToggleFieldRelative,
                self.swerve,
            ),
        )
        JoystickButton(self.controller, GetInt(PORT_CONSTANTS, "faceUp")).onTrue(
            cmd.runOnce(
                self.drive.ToggleFieldRelative,
                self.swerve,
            ),
        )

    def UpdateField(self) -> None:
        self.field.setRobotPose(self.swerve.GetPose())

    def GetAutonomousCommand(self) -> Command:
        return self.selector
