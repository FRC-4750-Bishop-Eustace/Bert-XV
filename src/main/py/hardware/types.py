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
from typing import Protocol, runtime_checkable

from wpimath.geometry import Pose3d, Rotation3d, Translation3d


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


class EncoderType(IntEnum):
    STUB = 0
    WPI = 1
    CANCODER = 2
    ABSOLUTE = 3


@dataclass(frozen=True, slots=True)
class EncoderParameters:
    device_id: int | tuple[int, int] | Motor
    inverted: bool = False


@runtime_checkable
class Encoder(Protocol):
    params: EncoderParameters

    def GetPosition(self) -> float | None:
        raise NotImplementedError

    def GetVelocity(self) -> float | None:
        raise NotImplementedError

    def Reset(self) -> None:
        raise NotImplementedError


class IMUType(IntEnum):
    STUB = 0
    ADIS16470 = 1
    NAVX = 2
    PIGEON2 = 3


@dataclass(frozen=True, slots=True)
class IMUParameters:
    device_id: int


@runtime_checkable
class IMU(Protocol):
    params: IMUParameters

    def GetPosition(self) -> Translation3d | None:
        raise NotImplementedError

    def GetRotation(self) -> Rotation3d | None:
        raise NotImplementedError

    def GetAcceleration(self) -> Translation3d | None:
        raise NotImplementedError

    def GetRate(self) -> float | None:
        raise NotImplementedError

    def GetYaw(self) -> float | None:
        raise NotImplementedError

    def Reset(self, pose: Pose3d | None = None) -> None:
        raise NotImplementedError


class SolenoidType(IntEnum):
    STUB = 0
    SINGLE = 1
    DOUBLE = 2


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

    def Set(self, state: int) -> None:
        raise NotImplementedError

    def Get(self) -> int | None:
        raise NotImplementedError

    def Toggle(self) -> None:
        raise NotImplementedError
