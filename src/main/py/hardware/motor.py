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

from pathlib import Path

from utils.vendor import RequireImport

from .types import IdleMode, Motor, MotorMode, MotorParameters, MotorType

__all__ = [
    "CreateMotor",
    "IdleMode",
    "Motor",
    "MotorMode",
    "MotorParameters",
    "MotorType",
]

# Bridge so `hardware.motor` also acts as a package root for `hardware.motor.{...}`
__path__ = [str(Path(__file__).resolve().parent / "motor")]


def CreateMotor(backend: MotorType, params: MotorParameters) -> "Motor":
    if backend == MotorType.STUB:
        from .motor.stub import StubMotor

        return StubMotor(params)
    if backend == MotorType.SPARK_MAX:
        RequireImport("rev")
        from .motor.spark_max import SparkMAXMotor

        return SparkMAXMotor(params)
    if backend == MotorType.SPARK_FLEX:
        RequireImport("rev")
        from .motor.spark_flex import SparkFlexMotor

        return SparkFlexMotor(params)
    if backend == MotorType.TALON_FX:
        RequireImport("phoenix6")
        from .motor.talon_fx import TalonFXMotor

        return TalonFXMotor(params)
    if backend == MotorType.TALON_FXS:
        RequireImport("phoenix6")
        from .motor.talon_fxs import TalonFXSMotor

        return TalonFXSMotor(params)
    raise ValueError(f"Unknown motor type: {backend}")
