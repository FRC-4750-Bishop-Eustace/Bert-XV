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
from phoenix6.canbus import CANBus
from phoenix6.hardware import CANcoder
from utils import CONSTANTS, GetString


class CANcoderEncoder:
    def __init__(self, params: EncoderParameters) -> None:
        assert isinstance(params.device_id, int)

        self.params = params
        self.encoder = CANcoder(device_id=params.device_id, canbus=CANBus(GetString(CONSTANTS, "canbus")))

    def GetPosition(self) -> float | None:
        return self.encoder.get_position().value

    def GetVelocity(self) -> float | None:
        return self.encoder.get_velocity().value

    def Reset(self) -> None:
        self.encoder.set_position(0.0)
