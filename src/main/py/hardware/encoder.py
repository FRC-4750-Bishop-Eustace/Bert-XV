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

from .motor import Motor

# Bridge so `hardware.encoder` also acts as a package root for `hardware.encoder.{...}`
__path__ = [str(Path(__file__).resolve().parent / "encoder")]


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

    def GetPosition(self) -> float | None: ...

    def GetVelocity(self) -> float | None: ...

    def Reset(self) -> None: ...


from .encoder.absolute_encoder import AbsoluteEncoder  # noqa: E402
from .encoder.cancoder import CANcoderEncoder  # noqa: E402
from .encoder.stub import StubEncoder  # noqa: E402
from .encoder.wpi_encoder import WPIEncoder  # noqa: E402


def CreateEncoder(backend: EncoderType, params: EncoderParameters) -> "Encoder":
    match backend:
        case EncoderType.STUB:
            return StubEncoder(params)
        case EncoderType.WPI:
            return WPIEncoder(params)
        case EncoderType.CANCODER:
            return CANcoderEncoder(params)
        case EncoderType.ABSOLUTE:
            return AbsoluteEncoder(params)
