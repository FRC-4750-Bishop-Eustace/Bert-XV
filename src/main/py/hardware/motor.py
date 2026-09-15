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

# Bridge so `hardware.motor` also acts as a package root for `hardware.motor.{...}`
__path__ = [str(Path(__file__).resolve().parent / "motor")]


class MotorMode(IntEnum):
    BRUSHLESS = 0
    BRUSHED = 1


class IdleMode(IntEnum):
    COAST = 0
    BRAKE = 1


@dataclass(frozen=True, slots=True)
class MotorParameters:
    device_id: int

    mode: MotorMode = MotorMode.BRUSHLESS
    inverted: bool = False
    idle: IdleMode = IdleMode.COAST

    velocity_factor: float | None = None
    position_factor: float | None = None

    current_limit: float | None = None


@runtime_checkable
class Motor(Protocol):
    params: MotorParameters

    def SetParams(self, params: MotorParameters) -> None: ...

    def SetSpeed(self, speed: float) -> None: ...

    def SetVoltage(self, voltage: float) -> None: ...

    def GetPosition(self) -> float | None: ...

    def GetVelocity(self) -> float | None: ...

    def Stop(self) -> None: ...
