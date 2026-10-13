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

from hardware.types import AprilTagAlgorithmType, AprilTagData, CameraParameters
from wpilib import Timer
from wpimath.geometry import Pose2d


class StubCamera:
    def __init__(self, params: CameraParameters) -> None:
        self.params = params
        self.data = AprilTagData(Pose2d(), 0.0, 0, 0.0, 0.0, 0.0, Timer.getFPGATimestamp(), 0.0, 0.0)
        self.yaw = 0.0

    def GetData(self, _algo: AprilTagAlgorithmType) -> AprilTagData | None:
        return self.data

    def SetOrientation(self, yaw: float) -> None:
        self.yaw = yaw
