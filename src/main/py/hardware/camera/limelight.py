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

from hardware.types import AprilTagAlgorithmType, AprilTagData, CameraParameters

from .limelight_helpers import PoseEstimate, SetCameraPoseRobotSpace


class LimelightCamera:
    def __init__(self, params: CameraParameters) -> None:
        self.params = params

        SetCameraPoseRobotSpace(params.name, params.offset.translation(), params.offset.rotation())

    def GetData(self, algo: AprilTagAlgorithmType) -> AprilTagData | None:
        estimate = None
        match algo:
            case AprilTagAlgorithmType.MT1_BLUE:
                estimate = PoseEstimate.GetRobotPoseEstimateBlueMT1(self.params.name)
            case AprilTagAlgorithmType.MT1_RED:
                estimate = PoseEstimate.GetRobotPoseEstimateRedMT1(self.params.name)
            case AprilTagAlgorithmType.MT2_BLUE:
                estimate = PoseEstimate.GetRobotPoseEstimateBlueMT2(self.params.name)
            case AprilTagAlgorithmType.MT2_RED:
                estimate = PoseEstimate.GetRobotPoseEstimateRedMT2(self.params.name)
            case _:
                raise ValueError(f"Unknown AprilTag algorithm type: {algo}")

        return AprilTagData(
            estimate.pose,
            estimate.latency,
            estimate.tagCount,
            estimate.tagSpan,
            estimate.avgTagDistance,
            estimate.avgTagArea,
            estimate.timestamp,
        )
