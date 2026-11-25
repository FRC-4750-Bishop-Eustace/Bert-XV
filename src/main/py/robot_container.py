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
from commands2 import Command
from commands2.button import Trigger
from subsystems import CreateDrivetrain, Vision
from utils import AutonomousSelector, Controller, Logger
from wpilib import Field2d, SmartDashboard


class RobotContainer:
    def __init__(self, logger: "Logger") -> None:
        self.logger = logger

        self.controller = Controller("driver")
        self.dashboard = Controller("dashboard")

        self.field = Field2d()

        self.selector = AutonomousSelector()

        self.drivetrain = CreateDrivetrain(self.logger)
        self.drive = DriveWithJoystick(self.drivetrain, self.controller)

        self.vision = Vision(self.logger, self.drivetrain)

        SmartDashboard.putData("Field", self.field)

        self.SetDefaults()
        self.ConfigureBindings()

    def SetDefaults(self) -> None:
        self.drivetrain.setDefaultCommand(self.drive)

    def ConfigureBindings(self) -> None:
        Trigger(lambda: self.controller.GetButton("faceDown")).onTrue(
            cmd.runOnce(
                self.drive.ToggleFieldRelative,
                self.drivetrain,
            ),
        )

    def UpdateField(self) -> None:
        self.field.setRobotPose(self.drivetrain.GetPose())

    def GetAutonomousCommand(self) -> Command:
        return self.selector
