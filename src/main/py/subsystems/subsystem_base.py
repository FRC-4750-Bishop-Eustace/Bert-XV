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

from typing import override

from commands2 import CommandScheduler, Subsystem
from utils import Logger
from wpiutil import SendableBuilder


class SubsystemBase(Subsystem):
    def __init__(self, logger: Logger, name: str | None = None) -> None:
        super().__init__()

        self.parent = logger
        self.name = (name or "").strip() or type(self).__name__
        self.logger = self.parent.Child(self.name)

        self.initialized = False
        self.enabled = True

        super().setName(self.name)
        CommandScheduler.getInstance().registerSubsystem(self)

    def GetName(self) -> str:
        return self.name

    def SetName(self, name: str) -> None:
        self.setName(name)

    @override
    def getName(self) -> str:
        return self.name

    @override
    def setName(self, name: str) -> None:
        normalized = (name or "").strip() or type(self).__name__
        if normalized == self.name:
            return

        self.name = normalized
        self.logger = self.parent.Child(self.name)
        super().setName(self.name)

    def GetLogger(self) -> Logger:
        return self.logger

    def Initialize(self) -> None:
        raise NotImplementedError

    def Periodic(self) -> None:
        raise NotImplementedError

    def SimulationPeriodic(self) -> None: ...

    @override
    def periodic(self) -> None:
        if not self.initialized:
            self.logger.Debug("Initializing subsystem")
            try:
                self.Initialize()
            except Exception as e:
                self.logger.Except("Unhandled exception in Initialize", e)
                raise

            self.initialized = True

        if not self.enabled:
            return

        try:
            self.Periodic()
        except Exception as e:
            self.logger.Except("Unhandled exception in Periodic", e)
            raise

    @override
    def simulationPeriodic(self) -> None:
        if not self.enabled:
            return

        try:
            self.SimulationPeriodic()
        except Exception as e:
            self.logger.Except("Unhandled exception in SimulationPeriodic", e)
            raise

    @override
    def initSendable(self, builder: SendableBuilder) -> None:
        super().initSendable(builder)
        builder.addStringProperty("Name", self.GetName, lambda _: None)
        builder.addBooleanProperty("Initialized", self.IsInitialized, lambda _: None)
        builder.addBooleanProperty("Enabled", self.IsEnabled, lambda _: None)

    def IsInitialized(self) -> bool:
        return self.initialized

    def IsEnabled(self) -> bool:
        return self.enabled

    def SetEnabled(self, enabled: bool) -> None:
        if enabled == self.enabled:
            return

        self.enabled = enabled
        if enabled:
            self.logger.Info("Subsystem enabled")
            self.OnEnable()
        else:
            self.OnDisable()
            self.Stop()
            self.logger.Info("Subsystem disabled")

    def OnEnable(self) -> None: ...

    def OnDisable(self) -> None: ...

    def Stop(self) -> None: ...
