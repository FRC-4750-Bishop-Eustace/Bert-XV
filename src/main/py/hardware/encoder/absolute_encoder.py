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

from hardware.encoder import EncoderParameters
from hardware.motor.spark_flex import SparkFlexMotor
from hardware.motor.spark_max import SparkMAXMotor


class AbsoluteEncoder:
    def __init__(self, params: EncoderParameters) -> None:
        assert isinstance(params.device_id, (SparkMAXMotor, SparkFlexMotor))

        self.params = params
        self.encoder = params.device_id.motor.getEncoder()

    def GetPosition(self) -> float | None:
        return self.encoder.getPosition()

    def GetVelocity(self) -> float | None:
        return self.encoder.getVelocity()

    def Reset(self) -> None:
        pass
