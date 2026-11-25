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

from typing import Any

from hardware.config import GetControllerConfig, ParseController, ParseControllerPorts
from wpilib.interfaces import GenericHID

from . import constants
from .constants import Constants, GetInt


class Controller:
    def __init__(self, hid: GenericHID | str) -> None:
        self.name: str | None
        self.hid: GenericHID | None
        self.ports: Constants

        if isinstance(hid, str):
            self.name = hid
            config = GetControllerConfig(constants.CONTROLLERS_CONSTANTS, hid)
            self.hid = ParseController(config)
            self.ports = ParseControllerPorts(config)
        else:
            self.name = type(hid).__name__
            self.hid = hid
            self.ports = {}

    def GetPort(self, key: str, default: int = 0) -> int:
        return GetInt(self.ports, key, default)

    def GetAxis(self, axis: int | str, default: float = 0.0) -> float:
        if self.hid is None:
            return default

        if isinstance(axis, str):
            axis = GetInt(self.ports, axis, -1)

        if not 0 <= axis < self.hid.getAxisCount():
            return default

        return self.hid.getRawAxis(axis)

    def GetButton(self, button: int | str, default: bool = False) -> bool:
        if self.hid is None:
            return default

        if isinstance(button, str):
            button = GetInt(self.ports, button, 0)

        if not 1 <= button <= self.hid.getButtonCount():
            return default

        return self.hid.getRawButton(button)

    def GetPOV(self, pov: int | str = 0, default: int = -1) -> int:
        if self.hid is None:
            return default

        if isinstance(pov, str):
            pov = GetInt(self.ports, pov, -1)

        if not 0 <= pov < self.hid.getPOVCount():
            return default

        return self.hid.getPOV(pov)

    def __getattr__(self, name: str) -> Any:
        if self.hid is None:
            return None

        return getattr(self.hid, name)
