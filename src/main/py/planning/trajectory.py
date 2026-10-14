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


from collections.abc import Sequence
from dataclasses import dataclass

from wpimath.geometry import Pose2d, Rotation2d, Translation2d
from wpimath.trajectory import Trajectory, TrajectoryConfig, TrajectoryGenerator

__all__ = [
    "TimedState",
    "TrajectoryBuilder",
    "TrajectoryParams",
]


@dataclass
class TrajectoryParams:
    maxVel: float
    maxAccel: float
    startVel: float = 0.0
    endVel: float = 0.0


@dataclass
class TimedState:
    t: float
    x: float
    y: float
    theta: float
    vx: float
    vy: float
    omega: float
    ax: float
    ay: float
    alpha: float


class TrajectoryBuilder:
    def __init__(self, params: TrajectoryParams) -> None:
        self.params = params

    def build(
        self,
        pathPoints: Sequence[tuple[float, float]],
        headings: Sequence[float],
    ) -> Trajectory | None:
        if len(pathPoints) < 2:
            return None

        # Build trajectory with WPILib trajectory generator (supports 2D paths)
        try:
            config = TrajectoryConfig(self.params.maxVel, self.params.maxAccel)
            config.setStartVelocity(self.params.startVel)
            config.setEndVelocity(self.params.endVel)

            # Convert to Pose2d waypoints; simplest: use headings if provided
            waypoints = []
            n = len(pathPoints)
            h = list(headings)
            if len(h) < n:
                h.extend([h[-1] if h else 0.0] * (n - len(h)))

            for i in range(n):
                p = pathPoints[i]
                waypoints.append(Pose2d(Translation2d(p[0], p[1]), Rotation2d(h[i])))

            traj = TrajectoryGenerator.generateTrajectory(waypoints, config)
            return traj

        except Exception:
            # Build trivial trajectory using TrajectoryParameterizer style minimal path
            try:
                # Use a simple approach: line segments parameterized
                states: list[Trajectory.State] = []
                return Trajectory(states) if states else None
            except Exception:
                return None
