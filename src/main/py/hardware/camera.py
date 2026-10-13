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

from .types import AprilTagAlgorithmType, AprilTagData, Camera, CameraParameters, CameraType

__all__ = [
    "AprilTagAlgorithmType",
    "AprilTagData",
    "Camera",
    "CameraParameters",
    "CameraType",
    "CreateCamera",
]

# Bridge so `hardware.camera` also acts as a package root for `hardware.camera.{...}`
__path__ = [str(Path(__file__).resolve().parent / "camera")]


def CreateCamera(backend: CameraType, params: CameraParameters) -> "Camera":
    from .camera.limelight import LimelightCamera
    from .camera.photon import PhotonCamera
    from .camera.stub import StubCamera

    if backend == CameraType.STUB:
        return StubCamera(params)
    if backend == CameraType.LIMELIGHT:
        return LimelightCamera(params)
    if backend == CameraType.PHOTON:
        return PhotonCamera(params)
    raise ValueError(f"Unknown camera type: {backend}")
