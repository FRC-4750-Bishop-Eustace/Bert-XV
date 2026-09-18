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
from phoenix6.canbus import CANBus
from phoenix6.hardware import Pigeon2
from utils import CONSTANTS, GetString
from wpimath.geometry import Pose3d, Rotation3d, Translation3d


class Pigeon2IMU:
    def __init__(self, params: IMUParameters) -> None:
        self.params = params
        self.imu = Pigeon2(device_id=params.device_id, canbus=CANBus(GetString(CONSTANTS, "canbus")))

    def GetPosition(self) -> Translation3d | None:
        return Translation3d(
            self.imu.get_accum_gyro_x().value,
            self.imu.get_accum_gyro_y().value,
            self.imu.get_accum_gyro_z().value,
        )

    def GetRotation(self) -> Rotation3d | None:
        return self.imu.getRotation3d()

    def GetAcceleration(self) -> Translation3d | None:
        return Translation3d(
            self.imu.get_acceleration_x().value,
            self.imu.get_acceleration_y().value,
            self.imu.get_acceleration_z().value,
        )

    def GetRate(self) -> float | None:
        return float(self.imu.get_angular_velocity_z_device().value)

    def GetYaw(self) -> float | None:
        return self.imu.getRotation3d().Z()

    def Reset(self, _pose: Pose3d | None = None) -> None:
        pass
