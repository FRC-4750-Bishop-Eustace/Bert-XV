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

from enum import IntEnum

from utils import Constants, GetList

__all__ = [
    "GetChannels",
    "ParseEnum",
]


def ParseEnum[T: IntEnum](enum: type[T], value: str, field: str) -> T:
    """Parse a JSON string such as ``"spark_max"`` into an enum member."""

    normalized = value.strip().upper().replace("-", "_").replace(" ", "_")
    try:
        return enum[normalized]
    except KeyError as error:
        choices = ", ".join(member.name.lower() for member in enum)
        raise ValueError(f"Unknown {field} '{value}' (expected one of: {choices})") from error


def GetChannels(config: Constants, key: str = "channels") -> tuple[int, int]:
    """Read a two-channel encoder or solenoid configuration entry."""

    channels = GetList(config, key)
    if len(channels) != 2:
        raise TypeError(f"Expected hardware entry '{key}' to contain exactly 2 channels, got {len(channels)}")

    result: list[int] = []
    for channel in channels:
        if isinstance(channel, bool) or not isinstance(channel, int):
            raise TypeError(f"Expected hardware entry '{key}' to contain integers, got {type(channel).__name__}")
        result.append(channel)

    return (result[0], result[1])
