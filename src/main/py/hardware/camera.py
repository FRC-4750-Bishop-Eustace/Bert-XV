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

from utils import Constants, GetPose3d, GetString
from utils.vendor import RequireImport

from .config import ParseEnum
from .types import AprilTagAlgorithmType, AprilTagData, Camera, CameraParameters, CameraType

__all__ = [
    "AprilTagAlgorithmType",
    "AprilTagData",
    "Camera",
    "CameraParameters",
    "CameraType",
    "CreateCamera",
    "CreateCameraFromConfig",
]

# Bridge so `hardware.camera` also acts as a package root for `hardware.camera.{...}`
__path__ = [str(Path(__file__).resolve().parent / "camera")]


def CreateCamera(backend: CameraType, params: CameraParameters) -> "Camera":
    if backend == CameraType.STUB:
        from .camera.stub import StubCamera

        return StubCamera(params)
    if backend == CameraType.LIMELIGHT:
        RequireImport("ntcore")
        from .camera.limelight import LimelightCamera

        return LimelightCamera(params)
    if backend == CameraType.PHOTON:
        RequireImport("photonlibpy", "robotpy_apriltag")
        from .camera.photon import PhotonCamera

        return PhotonCamera(params)
    raise ValueError(f"Unknown camera type: {backend}")


def CreateCameraFromConfig(config: Constants) -> "Camera":
    """Create a camera from a ``cameras`` entry in a vision configuration."""

    backend = ParseEnum(CameraType, GetString(config, "type"), "camera type")
    return CreateCamera(backend, CameraParameters(GetString(config, "name"), GetPose3d(config, "offset")))
