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

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src" / "main" / "py"))

from commands2 import CommandScheduler, TimedCommandRobot
from robot_container import RobotContainer
from utils import Health, Logger, ProfileSelector
from utils.vendor import VENDOR_LIBRARIES, CheckImport


class Robot(TimedCommandRobot):
    def __init__(self) -> None:
        super().__init__()

    def robotInit(self) -> None:
        self._logger = Logger("robot")  # `self.logger` already exists as an internal method of `TimedCommandRobot`

        self.profileSelector = ProfileSelector()
        self.profileSelector.schedule()

        self.cmdScheduler = CommandScheduler.getInstance()
        self.cmdScheduler.run()

        for module, name in VENDOR_LIBRARIES.items():
            error = CheckImport(module)
            if error is not None:
                self._logger.Warning(f"{name} could not be found", module=module, error=str(error))

        self.robot = RobotContainer(self._logger)
        self.health = Health(self._logger)

        self.autoCmd = self.robot.GetAutonomousCommand() or None

    def robotPeriodic(self) -> None:
        self.cmdScheduler.run()

        self.robot.UpdateField()

        self.health.Update()

    def autonomousInit(self) -> None:
        self._logger.Trace("Autonomous mode started")

        if self.autoCmd:
            self.autoCmd.schedule()

    def autonomousPeriodic(self) -> None:
        pass

    def teleopInit(self) -> None:
        self._logger.Trace("Teleoperated mode started")

        if self.autoCmd:
            self.autoCmd.cancel()

    def teleopPeriodic(self) -> None:
        """
        The `teleopPeriodic` function is not directly used here but if it's not defined,
        WPILib/RobotPy sends an annoying warning message

        This is the same for `autonomousPeriodic`, `disabledPeriodic`, `_simulationPeriodic`, and `testPeriodic`
        """
        pass

    def disabledInit(self) -> None:
        self._logger.Trace("Disabled mode started")

    def disabledPeriodic(self) -> None:
        pass

    def _simulationInit(self) -> None:
        self._logger.Trace("Simulation mode started")

    def _simulationPeriodic(self) -> None:
        pass

    def testInit(self) -> None:
        self._logger.Trace("Test mode started")

    def testPeriodic(self) -> None:
        pass
