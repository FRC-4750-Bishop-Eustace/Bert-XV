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

from hardware.types import IdleMode, MotorMode, MotorParameters
from rev import PersistMode, ResetMode, SparkFlex, SparkFlexConfig


class SparkFlexMotor:
    def __init__(self, params: MotorParameters) -> None:
        self.params = params
        self.motor = SparkFlex(
            params.device_id,
            SparkFlex.MotorType.kBrushless if params.mode == MotorMode.BRUSHLESS else SparkFlex.MotorType.kBrushed,
        )
        self.encoder = self.motor.getEncoder()
        self.config = SparkFlexConfig()

        self.SetParams(self.params)

    def SetParams(self, params: MotorParameters) -> None:
        self.params = params

        self.config.inverted(self.params.inverted)
        self.config.setIdleMode(
            SparkFlexConfig.IdleMode.kCoast if self.params.idle == IdleMode.COAST else SparkFlexConfig.IdleMode.kBrake
        )

        if params.velocity_factor:
            self.config.encoder.velocityConversionFactor(params.velocity_factor)
        if params.position_factor:
            self.config.encoder.positionConversionFactor(params.position_factor)
        if params.current_limit:
            self.config.smartCurrentLimit(int(params.current_limit), int(params.current_limit))

        self.motor.configure(
            self.config,
            ResetMode.kNoResetSafeParameters,
            PersistMode.kPersistParameters,
        )

    def SetSpeed(self, speed: float) -> None:
        self.motor.set(speed)

    def SetVoltage(self, voltage: float) -> None:
        self.motor.setVoltage(voltage)

    def GetPosition(self) -> float | None:
        return self.encoder.getPosition()

    def GetVelocity(self) -> float | None:
        return self.encoder.getVelocity()

    def Stop(self) -> None:
        self.motor.stopMotor()
