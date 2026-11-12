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

from collections.abc import Hashable
from functools import partial
from pathlib import Path

import commands2.cmd as cmd
from commands2 import Command
from wpilib import SendableChooser, SmartDashboard, getDeployDirectory

from .constants import InitializeConstants


def ProfileSelector() -> Command:
    profiles: dict[Hashable, Command] = {}
    profiles_dir = Path(getDeployDirectory()) / "profiles"
    if profiles_dir.is_dir():
        for profile in sorted(profiles_dir.iterdir()):
            if not profile.is_dir() or profile.name.startswith("."):
                continue

            profiles[profile.name] = cmd.runOnce(partial(InitializeConstants, profile.name)).ignoringDisable(True)

    if not profiles:
        profiles["default"] = cmd.runOnce(InitializeConstants).ignoringDisable(True)

    profile_chooser: SendableChooser = SendableChooser()
    default_profile = "default" if "default" in profiles else next(iter(profiles))
    for name in profiles:
        if name == default_profile:
            profile_chooser.setDefaultOption(str(name), str(name))
        else:
            profile_chooser.addOption(str(name), str(name))

    selector = cmd.select(profiles, profile_chooser.getSelected)

    SmartDashboard.putData("Profile Choices", profile_chooser)

    return selector
