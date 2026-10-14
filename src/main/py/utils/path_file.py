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

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

__all__ = ["LoadPathFile", "PathPoint", "SavePathFile"]


@dataclass(frozen=True, slots=True)
class PathPoint:
    x: float
    y: float
    heading: float


def LoadPathFile(path: Path) -> list[PathPoint]:
    pts: list[PathPoint] = []

    try:
        with path.open("rb") as f:
            d = f.read()

        if len(d) < 12:
            return pts

        magic = d[0:4]
        if magic != b"PATH":
            return pts

        ver = struct.unpack("<I", d[4:8])[0]
        if ver != 1:
            return pts

        count = struct.unpack("<I", d[8:12])[0]
        off = 12
        for _ in range(count):
            if off + 12 > len(d):
                break

            x, y, h = struct.unpack("<fff", d[off : off + 12])
            off += 12

            pts.append(PathPoint(x=x, y=y, heading=h))

    except Exception:
        pass

    return pts


def SavePathFile(path: Path, points: list[PathPoint]) -> None:
    data = struct.pack("<4sI", b"PATH", 1)
    data += struct.pack("<I", len(points))
    for p in points:
        data += struct.pack("<fff", p.x, p.y, p.heading)
    with path.open("wb") as f:
        f.write(data)
