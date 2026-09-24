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


class MotorType(IntEnum):
    STUB = 0
    SPARK_MAX = 1
    SPARK_FLEX = 2
    TALON_FX = 3
    TALON_FXS = 4


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

    def SetParams(self, params: MotorParameters) -> None:
        raise NotImplementedError

    def SetSpeed(self, speed: float) -> None:
        raise NotImplementedError

    def SetVoltage(self, voltage: float) -> None:
        raise NotImplementedError

    def GetPosition(self) -> float | None:
        raise NotImplementedError

    def GetVelocity(self) -> float | None:
        raise NotImplementedError

    def Stop(self) -> None:
        raise NotImplementedError


def CreateMotor(backend: MotorType, params: MotorParameters) -> "Motor":
    from .motor.spark_flex import SparkFlexMotor
    from .motor.spark_max import SparkMAXMotor
    from .motor.stub import StubMotor
    from .motor.talon_fx import TalonFXMotor
    from .motor.talon_fxs import TalonFXSMotor

    match backend:
        case MotorType.STUB:
            return StubMotor(params)
        case MotorType.SPARK_MAX:
            return SparkMAXMotor(params)
        case MotorType.SPARK_FLEX:
            return SparkFlexMotor(params)
        case MotorType.TALON_FX:
            return TalonFXMotor(params)
        case MotorType.TALON_FXS:
            return TalonFXSMotor(params)
        case _:
            raise ValueError(f"Unknown motor type: {backend}")
