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

from commands2 import CommandScheduler, TimedCommandRobot
from urcl import URCL

from src.main.py.robot_container import RobotContainer


class Robot(TimedCommandRobot):
    def __init__(self) -> None:
        super().__init__()

    def robotInit(self) -> None:
        URCL.start()

        self.robot = RobotContainer()
        self.robot.ConfigureBindings()

        self.autoCmd = None
        self.cmdScheduler = CommandScheduler.getInstance()

    def robotPeriodic(self) -> None:
        self.cmdScheduler.run()
        self.robot.UpdateField()

    def autonomousInit(self) -> None:
        self.autoCmd = self.robot.GetAutonomousCommand()
        if self.autoCmd:
            self.autoCmd.schedule()

    def autonomousPeriodic(self) -> None:
        pass

    def teleopInit(self) -> None:
        if self.autoCmd:
            self.autoCmd.cancel()

    def teleopPeriodic(self) -> None:
        """
        The `teleopPeriodic` function is not directly used here but if it's not defined, WPILib sends an annoying warning message
        (this is the same for `autonomousPeriodic`, `disabledPeriodic`, `_simulationPeriodic`, and `testPeriodic`)
        """
        pass

    def disabledPeriodic(self) -> None:
        pass

    def _simulationPeriodic(self) -> None:
        pass

    def testPeriodic(self) -> None:
        pass
