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

from hardware.types import IdleMode, MotorParameters
from phoenix6.canbus import CANBus
from phoenix6.configs import TalonFXSConfiguration
from phoenix6.hardware import TalonFXS
from phoenix6.signals import InvertedValue, NeutralModeValue
from utils import CONSTANTS, GetString


class TalonFXSMotor:
    def __init__(self, params: MotorParameters) -> None:
        self.params = params
        self.motor = TalonFXS(device_id=params.device_id, canbus=CANBus(GetString(CONSTANTS, "canbus")))

        self.SetParams(self.params)

    def SetParams(self, params: MotorParameters) -> None:
        self.params = params

        config = TalonFXSConfiguration()  # type: ignore[no-untyped-call]
        config.motor_output.inverted = (
            InvertedValue.CLOCKWISE_POSITIVE if params.inverted else InvertedValue.COUNTER_CLOCKWISE_POSITIVE
        )
        config.motor_output.neutral_mode = (
            NeutralModeValue.COAST if params.idle == IdleMode.COAST else NeutralModeValue.BRAKE
        )
        if params.current_limit:
            config.current_limits.supply_current_limit = params.current_limit
            config.current_limits.supply_current_limit_enable = True

        self.motor.configurator.apply(config)

    def SetSpeed(self, speed: float) -> None:
        self.motor.set(speed)

    def SetVoltage(self, voltage: float) -> None:
        self.motor.setVoltage(voltage)

    def GetPosition(self) -> float | None:
        return self.motor.get_position().value

    def GetVelocity(self) -> float | None:
        return self.motor.get_velocity().value

    def Stop(self) -> None:
        self.motor.stopMotor()  # type: ignore[no-untyped-call]
