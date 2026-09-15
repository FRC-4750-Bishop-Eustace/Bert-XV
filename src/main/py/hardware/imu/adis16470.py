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
from wpilib import ADIS16470_IMU
from wpimath.geometry import Pose3d, Rotation3d, Translation3d


class ADIS16470IMU:
    def __init__(self, params: IMUParameters) -> None:
        self.params = params
        self.imu = ADIS16470_IMU()

        self.imu.calibrate()

    def GetPosition(self) -> Translation3d | None:
        return Translation3d(
            self.imu.getAngle(ADIS16470_IMU.IMUAxis.kX),
            self.imu.getAngle(ADIS16470_IMU.IMUAxis.kY),
            self.imu.getAngle(ADIS16470_IMU.IMUAxis.kZ),
        )

    def GetRotation(self) -> Rotation3d | None:
        return Rotation3d(
            self.imu.getAngle(ADIS16470_IMU.IMUAxis.kRoll),
            self.imu.getAngle(ADIS16470_IMU.IMUAxis.kPitch),
            self.imu.getAngle(ADIS16470_IMU.IMUAxis.kYaw),
        )

    def GetAcceleration(self) -> Translation3d | None:
        return Translation3d(
            self.imu.getAccelX(),
            self.imu.getAccelY(),
            self.imu.getAccelZ(),
        )

    def GetRate(self) -> float | None:
        return self.imu.getRate(ADIS16470_IMU.IMUAxis.kYaw)

    def GetYaw(self) -> float | None:
        return self.imu.getAngle(ADIS16470_IMU.IMUAxis.kYaw)

    def Reset(self, pose: Pose3d | None = None) -> None:
        self.imu.reset()
        if pose:
            self.imu.setGyroAngle(ADIS16470_IMU.IMUAxis.kPitch, pose.rotation().x)
            self.imu.setGyroAngle(ADIS16470_IMU.IMUAxis.kYaw, pose.rotation().y)
            self.imu.setGyroAngle(ADIS16470_IMU.IMUAxis.kRoll, pose.rotation().z)
