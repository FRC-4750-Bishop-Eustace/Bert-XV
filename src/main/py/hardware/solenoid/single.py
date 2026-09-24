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
from wpilib import PneumaticsModuleType, Solenoid


class SingleSolenoid:
    def __init__(self, params: SolenoidParameters) -> None:
        assert isinstance(params.channel, int)

        self.params = params
        self.solenoid = Solenoid(
            params.module,
            PneumaticsModuleType.CTREPCM if params.type == PneumaticsModule.CTRE_PCM else PneumaticsModuleType.REVPH,
            params.channel,
        )

    def Set(self, state: int) -> None:
        self.solenoid.set(bool(state))

    def Get(self) -> int | None:
        return int(self.solenoid.get())

    def Toggle(self) -> None:
        self.solenoid.toggle()
