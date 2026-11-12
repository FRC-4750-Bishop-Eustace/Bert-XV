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
from typing import cast

from wpilib import getDeployDirectory
from wpimath.controller import (
    PIDController,
    ProfiledPIDController,
    SimpleMotorFeedforwardMeters,
    SimpleMotorFeedforwardRadians,
)
from wpimath.geometry import Pose2d, Pose3d, Rotation2d, Rotation3d, Translation2d, Translation3d
from wpimath.trajectory import TrapezoidProfile

from .logger import Logger

type JSONValue = int | float | str | bool | list[JSONValue] | dict[str, JSONValue] | None
type Constants = dict[str, JSONValue]


def DeepMerge(base: Constants, override: Constants) -> Constants:
    result: Constants = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            merged = DeepMerge(cast(Constants, result[key]), value)
            result[key] = merged

        else:
            result[key] = value

    return result


def LoadJSONFile(path: Path, logger: Logger) -> Constants | None:
    try:
        with path.open("r", encoding="utf-8", buffering=1) as file:
            data = json.load(file)
            if isinstance(data, dict):
                return cast(Constants, data)

            logger.Warning(f"JSON file '{path}' does not contain a top-level object, skipping")
            return None

    except FileNotFoundError:
        return None

    except json.JSONDecodeError as e:
        logger.Except("Failed to parse constants file", e, path=path)
        return None

    except Exception as e:
        logger.Except("Failed to load constants file", e, path=path)
        return None


def LoadFromDirectory(directory: Path, logger: Logger) -> Constants:
    merged: Constants = {}
    if not directory.exists() or not directory.is_dir():
        return merged

    json_files = sorted(directory.rglob("*.json"))
    for json_file in json_files:
        if any(part.startswith(".") for part in json_file.relative_to(directory).parts):
            continue

        data = LoadJSONFile(json_file, logger)
        if data is not None:
            merged = DeepMerge(merged, data)
            merged = DeepMerge(merged, {json_file.stem: data})

    return merged


def LoadConstants(profile: str | Path | None = None) -> Constants:
    logger = Logger("constants")
    deploy_dir = Path(getDeployDirectory())

    merged: Constants = {}

    if profile is not None:
        profile_path = Path(profile) if isinstance(profile, str) else profile
        if profile_path.is_absolute() and profile_path.is_dir():
            merged = LoadFromDirectory(profile_path, logger)
            return merged

        # Treat as profile name, look in common locations
        profile_name = profile_path.name if profile_path.name else str(profile)
        profile_locations = [
            deploy_dir / "profiles" / profile_name,
            deploy_dir / profile_name,
            deploy_dir / "users" / profile_name,
        ]

        for ploc in profile_locations:
            if ploc.is_dir():
                merged = LoadFromDirectory(ploc, logger)
                if merged:
                    return merged

        logger.Warning(f"No constants found for profile '{profile_name}'")

    # If no profile specified or not found, try default profile locations
    default_locations = [
        deploy_dir / "profiles" / "default",
        deploy_dir / "default",
    ]

    for dloc in default_locations:
        if dloc.is_dir():
            merged = DeepMerge(merged, LoadFromDirectory(dloc, logger))

    # Fallback to legacy single file
    if not merged:
        legacy_path = deploy_dir / "constants.json"
        legacy_data = LoadJSONFile(legacy_path, logger)

        if legacy_data is not None:
            merged = legacy_data

        else:
            logger.Except("Constants file not found", FileNotFoundError(str(legacy_path)), path=legacy_path)

    return merged


def GetInt(const: Constants, key: str, default: int = 0) -> int:
    value = const.get(key)
    if value is None:
        return default

    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"Expected constants entry '{key}' to be a number, got {type(value).__name__}")
    return int(value)


def GetFloat(const: Constants, key: str, default: float = 0.0) -> float:
    value = const.get(key)
    if value is None:
        return default

    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"Expected constants entry '{key}' to be a number, got {type(value).__name__}")
    return float(value)


def GetString(const: Constants, key: str, default: str = "") -> str:
    value = const.get(key)
    if value is None:
        return default

    if not isinstance(value, str):
        raise TypeError(f"Expected constants entry '{key}' to be a string, got {type(value).__name__}")
    return value


def GetBool(const: Constants, key: str, default: bool = False) -> bool:
    value = const.get(key)
    if value is None:
        return default

    if not isinstance(value, bool):
        raise TypeError(f"Expected constants entry '{key}' to be a boolean, got {type(value).__name__}")
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


def GetObjectList(const: Constants, key: str) -> list[Constants]:
    entries = GetList(const, key)
    result: list[Constants] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise TypeError(f"Expected constants entry '{key}' to contain JSON objects, got {type(entry).__name__}")
        result.append(entry)
    return result


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
    return PIDController(pid[0], pid[1], pid[2])


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


def GetTranslation2d(const: Constants, key: str) -> Translation2d:
    translation = GetNumbers(const, key, 2)
    return Translation2d(translation[0], translation[1])


def GetTranslation3d(const: Constants, key: str) -> Translation3d:
    translation = GetNumbers(const, key, 3)
    return Translation3d(translation[0], translation[1], translation[2])


def GetRotation2d(const: Constants, key: str) -> Rotation2d:
    rotation = GetNumbers(const, key, 1)
    return Rotation2d.fromDegrees(rotation[0])


def GetRotation3d(const: Constants, key: str) -> Rotation3d:
    rotation = GetNumbers(const, key, 3)
    return Rotation3d.fromDegrees(rotation[0], rotation[1], rotation[2])


def GetPose2d(const: Constants, key: str) -> Pose2d:
    pose = GetNumbers(const, key, 3)
    return Pose2d(Translation2d(pose[0], pose[1]), Rotation2d.fromDegrees(pose[2]))


def GetPose3d(const: Constants, key: str) -> Pose3d:
    pose = GetNumbers(const, key, 6)
    return Pose3d(
        Translation3d(pose[0], pose[1], pose[2]),
        Rotation3d.fromDegrees(pose[3], pose[4], pose[5]),
    )


def GetFeedForwardMeters(const: Constants, key: str) -> SimpleMotorFeedforwardMeters:
    ff = GetNumbers(const, key, 2)
    return SimpleMotorFeedforwardMeters(ff[0], ff[1])


def GetFeedForwardRadians(const: Constants, key: str) -> SimpleMotorFeedforwardRadians:
    ff = GetNumbers(const, key, 2)
    return SimpleMotorFeedforwardRadians(ff[0], ff[1])


def __getattr__(name: str) -> Constants:
    if name == "CONSTANTS" or name.endswith("_CONSTANTS"):
        if "CONSTANTS" not in globals():
            raise AttributeError(f"Constants '{name}' accessed before InitializeConstants() was called")

        raise AttributeError(f"Constants '{name}' not found in the loaded constants")

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def InitializeConstants(profile: str | Path | None = None) -> None:
    constants = LoadConstants(profile)

    generated: dict[str, Constants] = {"CONSTANTS": constants}
    for key, value in constants.items():
        if not isinstance(value, dict):
            continue

        generated[f"{key.upper()}_CONSTANTS"] = value
        if key == "subsystems":
            for subsystem, subsystem_constants in value.items():
                if isinstance(subsystem_constants, dict):
                    generated[f"{subsystem.upper()}_CONSTANTS"] = subsystem_constants

    # Drop any constants generated by a previous initialization so stale names don't linger
    for name in [n for n in globals() if n == "CONSTANTS" or n.endswith("_CONSTANTS")]:
        del globals()[name]

    globals().update(generated)
