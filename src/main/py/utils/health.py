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

import time

from wpilib import DriverStation, RobotController, SmartDashboard

from .constants import CONSTANTS
from .logger import Logger


class Health:
    def __init__(self, parent: "Logger", quit_on_fatal: bool = False) -> None:
        self.logger = parent.Child("health")
        self.quit_on_fatal = quit_on_fatal

        self.fatal = False
        self.lastMsgTime = 0.0
        self.channelOvercurrentTime = [0.0] * 24
        self.brownout = False
        self.lowVoltageStart: float | None = None

    def Update(self) -> None:
        if DriverStation.isEStopped():
            self.fatal = True

        if self.fatal:
            return

        voltage = RobotController.getBatteryVoltage()
        brownout = RobotController.isBrownedOut()
        temperature = RobotController.getCPUTemp()
        can = RobotController.getCANStatus()

        if brownout and not self.brownout:
            self.brownout = True
            self.TriggerFault("Robot brownout detected")

        elif voltage <= CONSTANTS["lowVoltage"]:
            # Check for (and ignore) voltage spikes
            now = time.monotonic()
            if self.lowVoltageStart is None:
                self.lowVoltageStart = now
            elif now - self.lowVoltageStart >= CONSTANTS["voltageDebounce"]:
                self.lowVoltageStart = None

                if voltage <= CONSTANTS["criticalVoltage"]:
                    self.TriggerFault(
                        f"Critical battery percentage: {(100.0 * voltage / 12.0):.1f}% ({voltage:.2f}V)", True
                    )
                else:
                    self.TriggerFault(f"Low battery percentage: {(100.0 * voltage / 12.0):.1f}% ({voltage:.2f}V)")
        else:
            self.lowVoltageStart = None

        if temperature >= CONSTANTS["highCPUTemperature"]:
            if temperature >= CONSTANTS["criticalCPUTemperature"]:
                self.TriggerFault(f"Critical CPU temperature: {temperature:.2f} °C", True)
            else:
                self.TriggerFault(f"High CPU temperature: {temperature:.2f} °C")

        if can.percentBusUtilization >= CONSTANTS["highCANUtilization"]:
            if can.percentBusUtilization >= CONSTANTS["criticalCANUtilization"]:
                self.TriggerFault(f"Max CAN bus utilization used: {can.percentBusUtilization}%", True)
            else:
                self.TriggerFault(f"High CAN bus utilization used: {can.percentBusUtilization}%")

        if can.txFullCount > 0:
            self.TriggerFault("CAN TX buffer full")

        SmartDashboard.putBoolean("Health/FatalFault", self.fatal)
        SmartDashboard.putBoolean("Health/Brownout", brownout)
        SmartDashboard.putNumber("Health/BatteryVoltage", voltage)
        SmartDashboard.putNumber("Health/CPUTemperature", temperature)
        SmartDashboard.putNumber("Health/CANUsage", can.percentBusUtilization)

    def TriggerFault(self, msg: str, fatal: bool = False) -> None:
        if self.fatal:
            return

        if fatal:
            self.logger.Fatal(msg)
        else:
            self.logger.Error(msg)

        self.fatal = fatal
        if fatal and self.quit_on_fatal:
            self.EnforceShutdown()

    def IsSafe(self) -> bool:
        return not self.fatal

    def EnforceShutdown(self) -> None:
        # An E-stop cannot be triggered within code
        self.TriggerFault("Manual shutdown (E-stop) required", True)
