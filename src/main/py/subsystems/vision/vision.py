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

from commands2 import Subsystem
from utils import Logger
from wpilib import Timer
from wpimath.geometry import Pose2d

from ..swerve.drivetrain import Drivetrain


class Vision(Subsystem):
    def __init__(self, parent: "Logger", swerve: "Drivetrain") -> None:
        super().__init__()
        self.logger = parent.Child("vision")
        self.swerve = swerve
        self.block = False
        self.stddevs = (1.0, 1.0, 1.0)
        self.pose = Pose2d()

    def BlockVisionUpdates(self, block: bool = True) -> None:
        self.block = block

    def UseHeuristic(self) -> bool:
        # TODO: Use a heuristic model to decide whether to read via the MT1 or MT2 algorithm (or neither)
        return False

    def periodic(self) -> None:
        if not self.block and self.UseHeuristic():
            self.swerve.estimator.setVisionMeasurementStdDevs(self.stddevs)
            self.swerve.estimator.addVisionMeasurement(self.pose, Timer.getFPGATimestamp())
