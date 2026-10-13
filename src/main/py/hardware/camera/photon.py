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
from photonlibpy import PhotonCamera as Photon
from photonlibpy import PhotonPoseEstimator
from robotpy_apriltag import AprilTagField, AprilTagFieldLayout
from wpilib import Timer
from wpimath.geometry import Rotation2d, Transform3d


class PhotonCamera:
    def __init__(self, params: CameraParameters) -> None:
        self.params = params
        self.camera = Photon(params.name)
        self.field = AprilTagFieldLayout.loadField(AprilTagField.kDefaultField)
        self.estimator = PhotonPoseEstimator(
            self.field,
            Transform3d(params.offset.translation(), params.offset.rotation()),
        )

    def GetData(self, algo: AprilTagAlgorithmType) -> AprilTagData | None:
        match algo:
            case AprilTagAlgorithmType.MT1_BLUE | AprilTagAlgorithmType.MT2_BLUE:
                self.field.setOrigin(AprilTagFieldLayout.OriginPosition.kBlueAllianceWallRightSide)
            case AprilTagAlgorithmType.MT1_RED | AprilTagAlgorithmType.MT2_RED:
                self.field.setOrigin(AprilTagFieldLayout.OriginPosition.kRedAllianceWallRightSide)
            case _:
                raise ValueError(f"Unknown AprilTag algorithm type: {algo}")

        results = self.camera.getAllUnreadResults()
        if not results:
            return None
        result = results[-1]

        if not result.hasTargets():
            return None

        multitag = algo in (AprilTagAlgorithmType.MT1_BLUE, AprilTagAlgorithmType.MT1_RED)
        if multitag:
            estimate = self.estimator.estimateCoprocMultiTagPose(result)
        else:
            estimate = self.estimator.estimatePnpDistanceTrigSolvePose(result)
        if estimate is None:
            estimate = self.estimator.estimateLowestAmbiguityPose(result)
        if estimate is None:
            return None

        translations = [target.getBestCameraToTarget().translation() for target in result.getTargets()]
        areas = [target.getArea() for target in result.getTargets()]
        distances = [translation.norm() for translation in translations]
        tagDistance = sum(distances) / len(distances)
        span = max(
            ((a - b).norm() for i, a in enumerate(translations) for b in translations[i + 1 :]),
            default=0.0,
        )

        if multitag and result.multitagResult is not None:
            ambiguity = result.multitagResult.estimatedPose.ambiguity
        else:
            ambiguities = [
                target.getPoseAmbiguity() for target in result.getTargets() if target.getPoseAmbiguity() >= 0.0
            ]
            ambiguity = min(ambiguities) if ambiguities else 0.0

        return AprilTagData(
            estimate.estimatedPose.toPose2d(),
            result.getLatencyMillis(),
            len(translations),
            span,
            tagDistance,
            sum(areas) / len(areas),
            result.getTimestampSeconds(),
            ambiguity,
            tagDistance,
        )

    def SetOrientation(self, yaw: float) -> None:
        self.estimator.addHeadingData(Timer.getFPGATimestamp(), Rotation2d.fromDegrees(yaw))
