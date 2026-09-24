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

from pathlib import Path

from .types import IMU, IMUParameters, IMUType

__all__ = [
    "IMU",
    "CreateIMU",
    "IMUParameters",
    "IMUType",
]

# Bridge so `hardware.imu` also acts as a package root for `hardware.imu.{...}`
__path__ = [str(Path(__file__).resolve().parent / "imu")]


def CreateIMU(backend: IMUType, params: IMUParameters) -> "IMU":
    from .imu.adis16470 import ADIS16470IMU
    from .imu.navx import NavXIMU
    from .imu.pigeon2 import Pigeon2IMU
    from .imu.stub import StubIMU

    if backend == IMUType.STUB:
        return StubIMU(params)
    if backend == IMUType.ADIS16470:
        return ADIS16470IMU(params)
    if backend == IMUType.NAVX:
        return NavXIMU(params)
    if backend == IMUType.PIGEON2:
        return Pigeon2IMU(params)
    raise ValueError(f"Unknown IMU type: {backend}")
