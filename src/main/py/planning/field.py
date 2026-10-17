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

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from wpimath.geometry import Pose2d, Rotation2d, Translation2d

__all__ = ["Alliance", "Field", "FieldConstants"]


class Alliance(Enum):
    BLUE = 0
    RED = 1


@dataclass(frozen=True)
class FieldConstants:
    fieldLength: float = 16.5409880001
    fieldWidth: float = 8.069326


class Field:
    def __init__(self, constants: FieldConstants | None = None) -> None:
        self.constants = constants or FieldConstants()

    @property
    def Length(self) -> float:
        return self.constants.fieldLength

    @property
    def Width(self) -> float:
        return self.constants.fieldWidth

    def ToRedAlliance(self, pose: Pose2d) -> Pose2d:
        translation = Translation2d(self.Length - pose.translation().X(), self.Width - pose.translation().Y())
        rotation = pose.rotation().rotateBy(Rotation2d.fromDegrees(180))
        return Pose2d(translation, rotation)

    def ToBlueAlliance(self, pose: Pose2d) -> Pose2d:
        return pose

    def MirrorForAlliance(self, pose: Pose2d, alliance: Alliance) -> Pose2d:
        if alliance == Alliance.RED:
            return self.ToRedAlliance(pose)
        return pose
