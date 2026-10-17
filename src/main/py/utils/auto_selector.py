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

import commands2.cmd as cmd
from commands2 import Command
from wpilib import SendableChooser, SmartDashboard


def AutonomousSelector(cmds: dict[Hashable, Command] | None = None) -> Command:
    auto_commands: dict[Hashable, Command] = (
        cmds
        if cmds
        else {
            "None": cmd.none(),
        }
    )

    auto_chooser: SendableChooser = SendableChooser()
    for name in auto_commands:
        auto_chooser.addOption(str(name), str(name))

    selector = cmd.select(auto_commands, auto_chooser.getSelected)

    SmartDashboard.putData("Auto Choices", auto_chooser)

    return selector


def AutonomousSelectorWithPathing(cmds: dict[Hashable, Command] | None = None) -> Command:
    return AutonomousSelector(cmds)
