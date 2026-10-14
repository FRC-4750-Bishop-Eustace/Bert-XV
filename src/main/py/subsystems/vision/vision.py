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

from commands2 import Subsystem
from hardware import AprilTagAlgorithmType, AprilTagData, Camera, CameraParameters, CameraType, CreateCamera
from utils import VISION_CONSTANTS, GetList, GetPose3d, GetString, Logger
from wpilib import Timer
from wpimath.geometry import Pose2d

from ..swerve.drivetrain import Drivetrain


class Vision(Subsystem):
    def __init__(self, parent: "Logger", swerve: "Drivetrain") -> None:
        super().__init__()
        self.logger = parent.Child("vision")
        self.swerve = swerve
        self.block = False
        self.stddevs = (1.0, 1.0, 1.0)

        self.cameras = []
        for cam in GetList(VISION_CONSTANTS, "cameras"):
            if not isinstance(cam, dict):
                raise TypeError(f"Expected vision camera entry to be a JSON object, got {type(cam).__name__}")

            backend = CameraType.STUB
            typ = GetString(cam, "type")
            if typ == "limelight":
                backend = CameraType.LIMELIGHT
            elif typ == "photon":
                backend = CameraType.PHOTON
            self.cameras.append(
                CreateCamera(backend, CameraParameters(GetString(cam, "name"), GetPose3d(cam, "offset")))
            )

    def BlockVisionUpdates(self, block: bool = True) -> None:
        self.block = block

    def UseHeuristic(self, camera: "Camera") -> AprilTagData | None:
        data: AprilTagData | None = None

        # MegaTag 1 algorithm
        mt1 = camera.GetData(AprilTagAlgorithmType.MT1_BLUE) or AprilTagData(
            Pose2d(), 0.0, 0, 0.0, 0.0, 0.0, Timer.getFPGATimestamp(), 0.0, 0.0
        )
        if mt1.tagCount > 0:
            if mt1.tagCount >= 2:
                self.stddevs = (0.4, 0.4, 0.5)
                data = mt1

            elif mt1.tagCount == 1 and mt1.ambiguity < 0.8 and mt1.cameraDistance < 4.0:
                scale = min(mt1.cameraDistance / 4.0, 1.0)

                self.stddevs = (
                    0.5 + 0.7 * scale,
                    0.5 + 0.7 * scale,
                    0.6 + 0.6 * scale,
                )
                data = mt1

        # MegaTag 2 algorithm
        mt2 = camera.GetData(AprilTagAlgorithmType.MT2_BLUE) or AprilTagData(
            Pose2d(), 0.0, 0, 0.0, 0.0, 0.0, Timer.getFPGATimestamp(), 0.0, 0.0
        )
        gyro_rate = abs(self.swerve.gyro.GetRate() or 0.0)
        if mt2.tagCount == 1 and gyro_rate < 360:
            camera.SetOrientation(self.swerve.gyro.GetYaw() or 0.0)

            self.stddevs = (
                0.6 + 0.002 * gyro_rate,
                0.6 + 0.002 * gyro_rate,
                1.0 + 0.01 * gyro_rate,
            )
            data = mt2

        return data

    def periodic(self) -> None:
        if self.block:
            return

        for camera in self.cameras:
            data = self.UseHeuristic(camera)

            if data is not None:
                self.swerve.estimator.setVisionMeasurementStdDevs(self.stddevs)
                self.swerve.estimator.addVisionMeasurement(data.pose, data.timestamp)
