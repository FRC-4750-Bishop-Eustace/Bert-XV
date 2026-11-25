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

from utils import Constants, GetInt, GetList, GetObjectList, GetString
from wpilib import Joystick, PS4Controller, PS5Controller, StadiaController, XboxController
from wpilib.interfaces import GenericHID

from .types import ControllerType

__all__ = [
    "GetChannels",
    "GetController",
    "GetControllerConfig",
    "ParseController",
    "ParseControllerPorts",
    "ParseEnum",
]

CONTROLLER_TYPES: dict[ControllerType, type[GenericHID]] = {
    ControllerType.JOYSTICK: Joystick,
    ControllerType.PS4: PS4Controller,
    ControllerType.PS5: PS5Controller,
    ControllerType.STADIA: StadiaController,
    ControllerType.XBOX: XboxController,
}


def ParseEnum[T: IntEnum](enum: type[T], value: str, field: str) -> T:
    normalized = value.strip().upper().replace("-", "_").replace(" ", "_")
    try:
        return enum[normalized]
    except KeyError as error:
        choices = ", ".join(member.name.lower() for member in enum)
        raise ValueError(f"Unknown {field} '{value}' (expected one of: {choices})") from error


def GetChannels(config: Constants, key: str = "channels") -> tuple[int, int]:
    channels = GetList(config, key)
    if len(channels) != 2:
        raise TypeError(f"Expected hardware entry '{key}' to contain exactly 2 channels, got {len(channels)}")

    result: list[int] = []
    for channel in channels:
        if isinstance(channel, bool) or not isinstance(channel, int):
            raise TypeError(f"Expected hardware entry '{key}' to contain integers, got {type(channel).__name__}")
        result.append(channel)

    return (result[0], result[1])


def GetControllerConfig(config: Constants, name: str) -> Constants | None:
    for entry in GetObjectList(config, "controllers"):
        if GetString(entry, "name") == name:
            return entry

    return None


def ParseController(config: Constants | None) -> GenericHID | None:
    if config is None:
        return None

    backend = ParseEnum(ControllerType, GetString(config, "type"), "controller type")
    return CONTROLLER_TYPES[backend](GetInt(config, "port"))


def ParseControllerPorts(config: Constants | None) -> Constants:
    if config is None:
        return {}

    ports = config.get("ports")
    if ports is None:
        return {}

    if not isinstance(ports, dict):
        raise TypeError(f"Expected controller entry 'ports' to be a JSON object, got {type(ports).__name__}")

    return ports


def GetController(config: Constants, name: str) -> GenericHID | None:
    return ParseController(GetControllerConfig(config, name))
