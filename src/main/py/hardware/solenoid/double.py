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

from hardware.types import PneumaticsModule, SolenoidParameters
from wpilib import DoubleSolenoid as DblSolenoid
from wpilib import PneumaticsModuleType


class DoubleSolenoid:
    def __init__(self, params: SolenoidParameters) -> None:
        assert (
            isinstance(params.channel, tuple)
            and len(params.channel) == 2
            and all(isinstance(c, int) for c in params.channel)
        )

        self.params = params
        self.solenoid = DblSolenoid(
            params.module,
            PneumaticsModuleType.CTREPCM if params.type == PneumaticsModule.CTRE_PCM else PneumaticsModuleType.REVPH,
            params.channel[0],
            params.channel[1],
        )

    def Set(self, state: int) -> None:
        self.solenoid.set(
            DblSolenoid.Value.kForward
            if state == 1
            else DblSolenoid.Value.kReverse
            if state == -1
            else DblSolenoid.Value.kOff
        )

    def Get(self) -> int | None:
        return (
            1
            if self.solenoid.get() == DblSolenoid.Value.kForward
            else -1
            if self.solenoid.get() == DblSolenoid.Value.kReverse
            else 0
        )

    def Toggle(self) -> None:
        self.solenoid.toggle()
