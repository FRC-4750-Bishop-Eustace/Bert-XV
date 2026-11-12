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

from collections.abc import Mapping
from pathlib import Path

from utils import (
    Constants,
    GetBool,
    GetInt,
    GetString,
)
from utils.vendor import RequireImport

from .config import GetChannels, ParseEnum
from .types import Encoder, EncoderParameters, EncoderType, Motor

__all__ = [
    "CreateEncoder",
    "CreateEncoderFromConfig",
    "Encoder",
    "EncoderParameters",
    "EncoderType",
]

# Bridge so `hardware.encoder` also acts as a package root for `hardware.encoder.{...}`
__path__ = [str(Path(__file__).resolve().parent / "encoder")]


def CreateEncoder(backend: EncoderType, params: EncoderParameters) -> "Encoder":
    if backend == EncoderType.STUB:
        from .encoder.stub import StubEncoder

        return StubEncoder(params)
    if backend == EncoderType.WPI:
        from .encoder.wpi_encoder import WPIEncoder

        return WPIEncoder(params)
    if backend == EncoderType.CANCODER:
        RequireImport("phoenix6")
        from .encoder.cancoder import CANcoderEncoder

        return CANcoderEncoder(params)
    if backend == EncoderType.ABSOLUTE:
        RequireImport("rev")
        from .encoder.absolute_encoder import AbsoluteEncoder

        return AbsoluteEncoder(params)
    raise ValueError(f"Unknown encoder type: {backend}")


def CreateEncoderFromConfig(config: Constants, motors: Mapping[str, Motor] | None = None) -> "Encoder":
    """Create an encoder from an ``encoders`` entry in a hardware configuration.

    Absolute encoders reference the motor they wrap through the ``motor`` entry.
    """

    backend = ParseEnum(EncoderType, GetString(config, "type"), "encoder type")
    inverted = GetBool(config, "inverted")

    device_id: int | tuple[int, int] | Motor
    if backend == EncoderType.ABSOLUTE:
        motor_name = GetString(config, "motor")
        if not motor_name:
            raise ValueError("Absolute encoder configuration requires a 'motor' entry")
        if motors is None or motor_name not in motors:
            raise KeyError(f"No motor named '{motor_name}' for absolute encoder")
        device_id = motors[motor_name]

    elif backend == EncoderType.WPI:
        device_id = GetChannels(config)

    elif backend == EncoderType.STUB:
        device_id = GetInt(config, "deviceId", 0)

    else:
        device_id = GetInt(config, "deviceId")

    return CreateEncoder(backend, EncoderParameters(device_id, inverted))
