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

from .auto_selector import AutonomousSelector
from .constants import (
    Constants,
    GetBool,
    GetFeedForwardMeters,
    GetFeedForwardRadians,
    GetFloat,
    GetInt,
    GetList,
    GetNumbers,
    GetObject,
    GetObjectList,
    GetPID,
    GetPose2d,
    GetPose3d,
    GetProfiledPID,
    GetRotation2d,
    GetRotation3d,
    GetString,
    GetTranslation2d,
    GetTranslation3d,
    InitializeConstants,
    LoadConstants,
)
from .health import Health
from .logger import Logger, LogLevel
from .profile_selector import ProfileSelector
from .uuid import GetLogDirectory, NewUUID

__all__ = [
    "AutonomousSelector",
    "Constants",
    "GetBool",
    "GetFeedForwardMeters",
    "GetFeedForwardRadians",
    "GetFloat",
    "GetInt",
    "GetList",
    "GetLogDirectory",
    "GetNumbers",
    "GetObject",
    "GetObjectList",
    "GetPID",
    "GetPose2d",
    "GetPose3d",
    "GetProfiledPID",
    "GetRotation2d",
    "GetRotation3d",
    "GetString",
    "GetTranslation2d",
    "GetTranslation3d",
    "Health",
    "InitializeConstants",
    "LoadConstants",
    "LogLevel",
    "Logger",
    "NewUUID",
    "ProfileSelector",
]
