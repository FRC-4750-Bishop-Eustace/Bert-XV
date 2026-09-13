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

from .logger import Logger


def LoadConstants(path: Path) -> dict[str, int | float]:
    logger = Logger("constants")
    try:
        with path.open("r", encoding="utf-8", buffering=1) as file:
            return cast(dict[str, int | float], json.load(file))
    except FileNotFoundError as e:
        logger.Except("Constants file not found", e, path=path)
    except json.JSONDecodeError as e:
        logger.Except("Failed to parse constants file", e, path=path)
    return {}


CONSTANTS = LoadConstants(Path(getDeployDirectory()) / "constants.json")
