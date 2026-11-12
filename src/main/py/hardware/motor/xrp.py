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

from hardware.types import MotorParameters
from xrp import XRPMotor as _XRPMotor


class XRPMotor:
    def __init__(self, params: MotorParameters) -> None:
        self.params = params
        self.motor = _XRPMotor(params.device_id)

        self.SetParams(self.params)

    def SetParams(self, params: MotorParameters) -> None:
        self.params = params

        self.motor.setInverted(params.inverted)

    def SetSpeed(self, speed: float) -> None:
        self.motor.set(speed)

    def SetVoltage(self, voltage: float) -> None:
        self.motor.set(voltage / 12.0)

    def GetPosition(self) -> float | None:
        return self.motor.get()

    def GetVelocity(self) -> float | None:
        return self.motor.get()

    def Stop(self) -> None:
        self.motor.stopMotor()
