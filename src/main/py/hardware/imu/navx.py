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

from hardware.imu import IMUParameters
from navx import AHRS
from wpimath.geometry import Pose3d, Rotation3d, Translation3d


class NavXIMU:
    def __init__(self, params: IMUParameters) -> None:
        self.params = params
        self.imu = AHRS.create_spi()

        self.imu.reset()

    def GetPosition(self) -> Translation3d | None:
        return Translation3d(
            self.imu.getDisplacementX(),
            self.imu.getDisplacementY(),
            self.imu.getDisplacementZ(),
        )

    def GetRotation(self) -> Rotation3d | None:
        return self.imu.getRotation3d()

    def GetAcceleration(self) -> Translation3d | None:
        return Translation3d(
            self.imu.getRawAccelX(),
            self.imu.getRawAccelY(),
            self.imu.getRawAccelZ(),
        )

    def GetRate(self) -> float | None:
        return self.imu.getRate()

    def GetYaw(self) -> float | None:
        return -self.imu.getYaw()

    def Reset(self, _pose: Pose3d | None = None) -> None:
        self.imu.reset()
        self.imu.zeroYaw()
