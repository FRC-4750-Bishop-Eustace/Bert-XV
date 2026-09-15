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

from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Protocol, runtime_checkable

# Bridge so `hardware.solenoid` also acts as a package root for `hardware.solenoid.{...}`
__path__ = [str(Path(__file__).resolve().parent / "solenoid")]


class PneumaticsModule(IntEnum):
    CTRE_PCM = 0
    REV_PH = 1


@dataclass(frozen=True, slots=True)
class SolenoidParameters:
    module: int
    type: PneumaticsModule
    channel: int | tuple[int, int]


@runtime_checkable
class Solenoid(Protocol):
    params: SolenoidParameters

    def Set(self, state: int) -> None: ...

    def Get(self) -> int | None: ...

    def Toggle(self) -> None: ...
