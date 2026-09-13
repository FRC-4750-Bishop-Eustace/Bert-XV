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

import json
import sys
import threading
import time
import traceback
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import Any, TextIO

from wpilib import getDeployDirectory


class LogLevel(IntEnum):
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    FATAL = 5


class Logger:
    COLORS = {
        LogLevel.TRACE: "\033[36;1m",  # Cyan + Bold
        LogLevel.DEBUG: "\033[34;1m",  # Blue + Bold
        LogLevel.INFO: "\033[32;1m",  # Green + Bold
        LogLevel.WARNING: "\033[33;1m",  # Yellow + Bold
        LogLevel.ERROR: "\033[31;1m",  # Red + Bold
        LogLevel.FATAL: "\033[35;1m",  # Magenta + Bold
    }

    RESET = "\033[0m"

    def __init__(
        self,
        tag: str,
        level: LogLevel = LogLevel.FATAL,
        stream: TextIO = sys.stderr,
        use_color: bool = True,
        log_file: bool = False,
        json_output: bool = False,
    ) -> None:
        self.tag = tag
        self.level = level
        self.stream = stream
        self.start_time = time.monotonic()
        self.json_output = json_output
        self.use_color = use_color and stream.isatty()

        self.file = None
        if log_file:
            path = Path(getDeployDirectory() + "logs/" + tag + ".txt")
            path.parent.mkdir(parents=True, exist_ok=True)
            self.file = path.open("a", encoding="utf-8", buffering=1)

        self.lock = threading.Lock()

    def __exit__(self, *_: object) -> None:
        self.Close()

    def __enter__(self) -> Logger:
        return self

    def SetLevel(self, level: LogLevel) -> None:
        self.level = level

    def Log(self, level: LogLevel, msg: str, **fields: Any) -> None:
        if level < self.level:
            return

        timestamp = datetime.now().astimezone().isoformat(timespec="milliseconds")
        uptime = time.monotonic() - self.start_time

        color = self.COLORS[level] if self.use_color else ""
        reset = self.RESET if self.use_color else ""

        if self.json_output:
            record: dict[str, Any] = {
                "timestamp": timestamp,
                "uptime": uptime,
                "level": level.name,
                "tag": self.tag,
                "message": msg,
            }
            if fields:
                record["fields"] = fields

            line = json.dumps(record, default=str, separators=(",", ":"))
        else:
            color = self.COLORS[level] if self.use_color else ""
            reset = self.RESET if self.use_color else ""

            line = f"{color}[{timestamp}][{uptime:09.3f}][{self.tag}][{level.name}]:{reset} {msg}"
            if fields:
                formatted_fields = " ".join(f"{key}={value!r}" for key, value in fields.items())
                line += f" {formatted_fields}"

        with self.lock:
            print(line, file=self.stream, flush=True)
            if self.file is not None:
                print(line, file=self.file, flush=True)

    def Trace(self, msg: str, **fields: Any) -> None:
        self.Log(LogLevel.TRACE, msg, **fields)

    def Debug(self, msg: str, **fields: Any) -> None:
        self.Log(LogLevel.DEBUG, msg, **fields)

    def Info(self, msg: str, **fields: Any) -> None:
        self.Log(LogLevel.INFO, msg, **fields)

    def Warning(self, msg: str, **fields: Any) -> None:
        self.Log(LogLevel.WARNING, msg, **fields)

    def Error(self, msg: str, **fields: Any) -> None:
        self.Log(LogLevel.ERROR, msg, **fields)

    def Fatal(self, msg: str, **fields: Any) -> None:
        self.Log(LogLevel.FATAL, msg, **fields)

    def Except(self, msg: str, exception: BaseException | None = None, **fields: Any) -> None:
        if exception is None:
            exception = sys.exception()

        fields = {
            **fields,
            "exception": type(exception).__name__,
        }

        self.Log(LogLevel.ERROR, msg, **fields)

        formatted = "".join(traceback.format_exception(exception))
        with self.lock:
            print(formatted, file=self.stream, end="", flush=True)
            if self.file is not None:
                print(formatted, file=self.file, end="", flush=True)

    def Child(self, tag: str) -> Logger:
        child = Logger(
            level=self.level,
            stream=self.stream,
            use_color=self.use_color,
            json_output=self.json_output,
            tag=f"{self.tag}/{tag}",
        )

        child.start_time = self.start_time
        child.file = self.file
        child.lock = self.lock

        return child

    def Close(self) -> None:
        if self.file is not None:
            self.file.close()
            self.file = None
