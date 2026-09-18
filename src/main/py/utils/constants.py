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

import json
from pathlib import Path
from typing import Final, cast

from wpilib import getDeployDirectory
from wpimath.controller import (
    PIDController,
    ProfiledPIDController,
    SimpleMotorFeedforwardMeters,
    SimpleMotorFeedforwardRadians,
)
from wpimath.trajectory import TrapezoidProfile

from .logger import Logger

type JSONValue = int | float | str | bool | list[JSONValue] | dict[str, JSONValue] | None
type Constants = dict[str, JSONValue]


def LoadConstants(path: Path) -> Constants:
    logger = Logger("constants")
    try:
        with path.open("r", encoding="utf-8", buffering=1) as file:
            return cast(Constants, json.load(file))
    except FileNotFoundError as e:
        logger.Except("Constants file not found", e, path=path)
    except json.JSONDecodeError as e:
        logger.Except("Failed to parse constants file", e, path=path)
    return {}


def GetInt(const: Constants, key: str) -> int:
    value = const[key]
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"Expected constants entry '{key}' to be a number, got {type(value).__name__}")
    return int(value)


def GetFloat(const: Constants, key: str) -> float:
    value = const[key]
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"Expected constants entry '{key}' to be a number, got {type(value).__name__}")
    return float(value)


def GetString(const: Constants, key: str) -> str:
    value = const[key]
    if not isinstance(value, str):
        raise TypeError(f"Expected constants entry '{key}' to be a string, got {type(value).__name__}")
    return value


def GetBool(const: Constants, key: str) -> bool:
    value = const[key]
    if not isinstance(value, bool):
        raise TypeError(f"Expected constants entry 'key' to be a boolean, got {type(value).__name__}")
    return value


def GetList(const: Constants, key: str) -> list[JSONValue]:
    value = const[key]
    if not isinstance(value, list):
        raise TypeError(f"Expected constants entry '{key}' to be a JSON array, got {type(value).__name__}")
    return value


def GetObject(const: Constants, key: str) -> Constants:
    value = const[key]
    if not isinstance(value, dict):
        raise TypeError(f"Expected constants entry '{key}' to be a JSON object, got {type(value).__name__}")
    return value


def GetNumbers(const: Constants, key: str, count: int) -> list[float]:
    numbers = GetList(const, key)
    if len(numbers) != count:
        raise TypeError(f"Expected constants entry '{key}' to have exactly {count} numbers, got {len(numbers)}")
    result: list[float] = []
    for n in numbers:
        if isinstance(n, bool) or not isinstance(n, int | float):
            raise TypeError(f"Expected constants entry '{key}' to be a list of numbers, got {type(n).__name__}")
        result.append(float(n))
    return result


def GetPID(const: Constants, key: str) -> PIDController:
    pid = GetNumbers(const, key, 3)
    return PIDController(
        pid[0],
        pid[1],
        pid[2],
    )


def GetProfiledPID(const: Constants, key: str) -> ProfiledPIDController:
    pid = GetNumbers(const, key, 3)
    return ProfiledPIDController(
        pid[0],
        pid[1],
        pid[2],
        TrapezoidProfile.Constraints(
            GetFloat(const, "maxAngularVelocity"),
            GetFloat(const, "maxAngularAcceleration"),
        ),
    )


def GetFeedForwardMeters(const: Constants, key: str) -> SimpleMotorFeedforwardMeters:
    ff = GetNumbers(const, key, 2)
    return SimpleMotorFeedforwardMeters(
        ff[0],
        ff[1],
    )


def GetFeedForwardRadians(const: Constants, key: str) -> SimpleMotorFeedforwardRadians:
    ff = GetNumbers(const, key, 2)
    return SimpleMotorFeedforwardRadians(
        ff[0],
        ff[1],
    )


CONSTANTS: Final[Constants] = LoadConstants(Path(getDeployDirectory()) / "constants.json")
