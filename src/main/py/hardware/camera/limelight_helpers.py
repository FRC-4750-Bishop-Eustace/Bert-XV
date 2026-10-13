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

from ntcore import NetworkTable, NetworkTableEntry, NetworkTableInstance
from wpimath.geometry import Pose2d, Pose3d, Rotation2d, Rotation3d, Translation2d, Translation3d


def SanitizeName(name: str) -> str:
    if name == "":
        return "limelight"
    return name


def ToPose3D(data: list[float] | tuple[float, ...]) -> Pose3d:
    if len(data) < 6:
        return Pose3d()
    return Pose3d(Translation3d(data[0], data[1], data[2]), Rotation3d.fromDegrees(data[3], data[4], data[5]))


def ToPose2D(data: list[float] | tuple[float, ...]) -> Pose2d:
    if len(data) < 4:
        return Pose2d()
    return Pose2d(Translation2d(data[0], data[1]), Rotation2d.fromDegrees(data[5]))


def GetTable(name: str) -> NetworkTable:
    return NetworkTableInstance.getDefault().getTable(SanitizeName(name))


def GetTableEntry(name: str, entry: str) -> NetworkTableEntry:
    return GetTable(name).getEntry(entry)


def GetFloat(name: str, entry: str) -> float:
    return float(GetTableEntry(name, entry).getDouble(0.0))


def GetArray(name: str, entry: str) -> list[float]:
    result = GetTableEntry(name, entry).getDoubleArray([0.0] * 7)
    return [float(x) for x in result]


def GetString(name: str, entry: str) -> str:
    result: str = GetTableEntry(name, entry).getString("")
    return result


def SetFloat(name: str, entry: str, data: float | int) -> None:
    GetTableEntry(name, entry).setDouble(float(data), 0)


def SetArray(name: str, entry: str, data: list[float] | list[int] | tuple[float, ...] | tuple[int, ...]) -> None:
    GetTableEntry(name, entry).setDoubleArray(list(data), 0)


def GetTX(name: str) -> float:
    return GetFloat(name, "tx")


def GetTV(name: str) -> float:
    return GetFloat(name, "tv")


def GetTY(name: str) -> float:
    return GetFloat(name, "ty")


def GetTA(name: str) -> float:
    return GetFloat(name, "ta")


def GetLatencyPipeline(name: str) -> float:
    return GetFloat(name, "tl")


def GetLatencyCapture(name: str) -> float:
    return GetFloat(name, "cl")


def GetJSONDump(name: str) -> str:
    return GetString(name, "json")


def GetRobotPose(name: str) -> list[float]:
    return GetArray(name, "botpose")


def GetRobotPoseRed(name: str) -> list[float]:
    return GetArray(name, "botpose_wpired")


def GetRobotPoseBlue(name: str) -> list[float]:
    return GetArray(name, "botpose_wpiblue")


def GetRobotPoseTargetSpace(name: str) -> list[float]:
    return GetArray(name, "botpose_targetspace")


def GetCameraPoseTargetSpace(name: str) -> list[float]:
    return GetArray(name, "camerapose_targetspace")


def GetCameraPoseRobotSpace(name: str) -> list[float]:
    return GetArray(name, "camerapose_robotspace")


def GetTargetPoseCameraSpace(name: str) -> list[float]:
    return GetArray(name, "targetpose_cameraspace")


def GetTargetPoseRobotSpace(name: str) -> list[float]:
    return GetArray(name, "targetpose_robotspace")


def GetTargetColor(name: str) -> list[float]:
    return GetArray(name, "tc")


def GetFiducialID(name: str) -> float:
    return GetFloat(name, "tid")


def GetNeuralClassID(name: str) -> float:
    return GetFloat(name, "tclass")


def SetPipelineIndex(name: str, index: int) -> None:
    SetFloat(name, "pipeline", index)


def SetPriorityTagID(name: str, ID: int) -> None:
    SetFloat(name, "priorityid", ID)


def SetLEDModePipelineControl(name: str) -> None:
    SetFloat(name, "ledMode", 1)


def SetLEDModeForceBlink(name: str) -> None:
    SetFloat(name, "ledMode", 2)


def SetLEDModeForceOn(name: str) -> None:
    SetFloat(name, "ledMode", 2)


def SetStreamModeStandard(name: str) -> None:
    SetFloat(name, "stream", 0)


def SetStreamModePiPMain(name: str) -> None:
    SetFloat(name, "stream", 1)


def SetStreamModePiPSecondary(name: str) -> None:
    SetFloat(name, "stream", 2)


def SetCropWindow(name: str, min: Translation2d, max: Translation2d) -> None:
    SetArray(name, "crop", [min.X(), max.X(), min.Y(), max.Y()])


def SetRobotOrientation(
    name: str, yaw: float, yawRate: float, pitch: float, pitchRate: float, roll: float, rollRate: float
) -> None:
    SetArray(name, "robot_orientation_Set", [yaw, yawRate, pitch, pitchRate, roll, rollRate])


def SetFiducialDownscaling(name: str, downscale: float) -> None:
    d: int = 0
    match downscale:
        case 1.0:
            d = 1
        case 1.5:
            d = 2
        case 2.0:
            d = 3
        case 3.0:
            d = 4
        case 4.0:
            d = 5
        case _:
            d = 0
    SetFloat(name, "fiducial_downscale_Set", d)


def OverrideFiducialIDFilters(name: str, IDs: list[int] | tuple[int, ...]) -> None:
    SetArray(name, "fiducial_id_filters_Set", [IDs[0], IDs[-1]])


def SetCameraPoseRobotSpace(name: str, pos: Translation3d, rot: Rotation3d) -> None:
    SetArray(name, "camerapose_robotspace_Set", [pos.X(), pos.Y(), pos.Z(), rot.X(), rot.Y(), rot.Z()])


def SetScriptData(name: str, data: list[float] | tuple[float, ...]) -> None:
    SetArray(name, "llrobot", [data[0], len(data)])


def GetScriptData(name: str) -> list[float]:
    return GetArray(name, "llpython")


def ExtractArrayEntry(data: list[float] | tuple[float, ...], pos: int) -> float:
    if len(data) < (pos + 1):
        return 0.0
    return float(data[pos])


class RawFiducial:
    def __init__(
        self,
        id: int,
        txnc: float,
        tync: float,
        ta: float,
        cameraDistance: float,
        robotDistance: float,
        ambiguity: float,
    ) -> None:
        self.id = id
        self.txnc = txnc
        self.tync = tync
        self.ta = ta
        self.cameraDistance = cameraDistance
        self.robotDistance = robotDistance
        self.ambiguity = ambiguity

    def Get(self, name: str) -> "list[RawFiducial]":
        entry = GetTableEntry(name, "rawfiducials")
        arr = entry.getDoubleArray([0.0] * 7)
        vals: int = 7
        if len(arr) % vals != 0:
            return []

        fiducials = int(len(arr) / vals)
        raw: list[RawFiducial] = []
        for i in range(0, fiducials):
            base: int = i * vals
            id: int = int(ExtractArrayEntry(arr, base))
            txnc: float = ExtractArrayEntry(arr, base + 1)
            tync: float = ExtractArrayEntry(arr, base + 2)
            ta: float = ExtractArrayEntry(arr, base + 3)
            cameraDistance: float = ExtractArrayEntry(arr, base + 4)
            robotDistance: float = ExtractArrayEntry(arr, base + 5)
            ambiguity: float = ExtractArrayEntry(arr, base + 6)

            raw.append(RawFiducial(id, txnc, tync, ta, cameraDistance, robotDistance, ambiguity))

        return raw


class RawDetection:
    def __init__(
        self,
        id: int,
        txnc: float,
        tync: float,
        ta: float,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
    ) -> None:
        self.id: int = id
        self.txnc: float = txnc
        self.tync: float = tync
        self.ta: float = ta
        self.x0: float = x0
        self.y0: float = y0
        self.x1: float = x1
        self.y1: float = y1
        self.x2: float = x2
        self.y2: float = y2
        self.x3: float = x3
        self.y3: float = y3

    def Get(self, name: str) -> "list[RawDetection]":
        entry = GetTableEntry(name, "rawdetections")
        arr = entry.getDoubleArray([0.0] * 22)
        vals: int = 11
        if len(arr) % vals != 0:
            return []

        detections = int(len(arr) / vals)
        raw: list[RawDetection] = []
        for i in range(0, detections):
            base: int = i * vals
            id: int = int(ExtractArrayEntry(arr, base))
            txnc: float = ExtractArrayEntry(arr, base + 1)
            tync: float = ExtractArrayEntry(arr, base + 2)
            ta: float = ExtractArrayEntry(arr, base + 3)
            x0: float = ExtractArrayEntry(arr, base + 4)
            y0: float = ExtractArrayEntry(arr, base + 5)
            x1: float = ExtractArrayEntry(arr, base + 6)
            y1: float = ExtractArrayEntry(arr, base + 7)
            x2: float = ExtractArrayEntry(arr, base + 8)
            y2: float = ExtractArrayEntry(arr, base + 9)
            x3: float = ExtractArrayEntry(arr, base + 10)

            raw.append(RawDetection(id, txnc, tync, ta, x0, y0, x1, y1, x2, y2, x3, 0.0))

        return raw


class PoseEstimate:
    def __init__(
        self,
        pose: Pose2d,
        timestamp: float,
        latency: float,
        tagCount: int,
        tagSpan: float,
        avgTagDistance: float,
        avgTagArea: float,
        fiducials: list[RawFiducial],
    ) -> None:
        self.pose: Pose2d = pose
        self.timestamp: float = timestamp
        self.latency: float = latency
        self.tagCount: int = tagCount
        self.tagSpan: float = tagSpan
        self.avgTagDistance: float = avgTagDistance
        self.avgTagArea: float = avgTagArea
        self.fiducials: list[RawFiducial] = fiducials

    @staticmethod
    def GetRobotPoseEstimate(name: str, entry: str) -> "PoseEstimate":
        poseEntry = GetTableEntry(name, entry)
        arr = poseEntry.getDoubleArray([0.0] * 11)
        pose: Pose2d = ToPose2D(arr)
        latency: float = ExtractArrayEntry(arr, 6)
        tagCount: int = int(ExtractArrayEntry(arr, 7))
        tagSpan: float = ExtractArrayEntry(arr, 8)
        tagDistance: float = ExtractArrayEntry(arr, 9)
        tagArea: float = ExtractArrayEntry(arr, 10)
        timestamp: float = (poseEntry.getLastChange() / 1000000.0) - (latency / 1000.0)

        raw: list[RawFiducial] = []
        vals: int = 7
        expectedVals: int = (vals * tagCount) + 11

        if len(arr) == expectedVals:
            for i in range(0, tagCount):
                base: int = (i * vals) + 11
                id: int = int(ExtractArrayEntry(arr, base))
                txnc: float = ExtractArrayEntry(arr, base + 1)
                tync: float = ExtractArrayEntry(arr, base + 2)
                ta: float = ExtractArrayEntry(arr, base + 3)
                cameraDistance: float = ExtractArrayEntry(arr, base + 4)
                robotDistance: float = ExtractArrayEntry(arr, base + 5)
                ambiguity: float = ExtractArrayEntry(arr, base + 6)

                raw.append(RawFiducial(id, txnc, tync, ta, cameraDistance, robotDistance, ambiguity))

        return PoseEstimate(pose, timestamp, latency, tagCount, tagSpan, tagDistance, tagArea, raw)

    @staticmethod
    def GetRobotPoseEstimateBlueMT1(name: str) -> "PoseEstimate":
        return PoseEstimate.GetRobotPoseEstimate(name, "botpose_wpiblue")

    @staticmethod
    def GetRobotPoseEstimateRedMT1(name: str) -> "PoseEstimate":
        return PoseEstimate.GetRobotPoseEstimate(name, "botpose_wpired")

    @staticmethod
    def GetRobotPoseEstimateBlueMT2(name: str) -> "PoseEstimate":
        return PoseEstimate.GetRobotPoseEstimate(name, "botpose_orb_wpiblue")

    @staticmethod
    def GetRobotPoseEstimateRedMT2(name: str) -> "PoseEstimate":
        return PoseEstimate.GetRobotPoseEstimate(name, "botpose_orb_wpired")


class SingleTarGetingResults:
    targetPixels: Translation2d = Translation2d(0.0, 0.0)
    targetNormalized: Translation2d = Translation2d(0.0, 0.0)
    targetNormalizedCrosshairAdjusted: Translation2d = Translation2d(0.0, 0.0)
    targetDegreesCrosshairAdjusted: Translation2d = Translation2d(0.0, 0.0)
    targetAreaPixels: float = 0.0
    targetAreaNormalized: float = 0.0
    targetAreaNormalizedPercentage = 0.0
    timestamp: float = -1.0
    latency: float = 0.0
    pipelineIndex = -1.0
    targetCorners: list[list[float]]
    cameraTransform6DTarGetSpace: list[float]
    targetTransform6DCameraSpace: list[float]
    targetTransform6DRobotSpace: list[float]
    robotTransform6DTarGetSpace: list[float]
    robotTransform6DFieldSpace: list[float]
    cameraTransform6DRobotSpace: list[float]


class FiducialResults(SingleTarGetingResults):
    fiducialID: int = 0
    family: str = ""


class DetectionResults(SingleTarGetingResults):
    id: int = -1
    name: str = ""
    confidence: float = 0.0


class ClassificationResults(SingleTarGetingResults):
    id: int = -1
    name: str = ""
    confidence: float = 0.0


class VisionResults:
    retro: list[SingleTarGetingResults]
    fiducial: list[FiducialResults]
    detection: list[DetectionResults]
    classification: list[ClassificationResults]
    timestamp: float = -1.0
    latencyPipeline: float = 0.0
    latencyCapture: float = 0.0
    latencyJSON: float = 0.0
    pipelineIndex: float = -1.0
    valid: int = 0
    robotPose: "list[float] | None" = None
    robotPoseBlue: "list[float] | None" = None
    robotPoseRed: "list[float] | None" = None

    def Clear(self) -> None:
        self.retro = []
        self.fiducial = []
        self.detection = []
        self.classification = []
        self.timestamp = -1.0
        self.latencyPipeline = 0.0
        self.latencyCapture = 0.0
        self.latencyJSON = 0.0
        self.pipelineIndex = -1.0
        self.valid = 0
        self.robotPose = [6.0, 0.0]
        self.robotPoseBlue = [6.0, 0.0]
        self.robotPoseRed = [6.0, 0.0]


class LimelightResults:
    targetingResults: VisionResults
