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

import importlib
from typing import Final

from .logger import Logger, LogLevel

VENDOR_LIBRARIES: Final[dict[str, str]] = {
    "rev": "REV",
    "phoenix6": "Phoenix 6",
    "navx": "NavX",
    "ntcore": "NetworkTables",
    "photonlibpy": "PhotonLib",
    "robotpy_apriltag": "AprilTag",
    "urcl": "URCL",
}

_results: dict[str, BaseException | None] = {}


def CheckImport(module: str) -> BaseException | None:
    """
    Attempt to import `module`, caching the outcome.

    Returns `None` if the import succeeded, otherwise the exception that was raised.
    """
    if module not in _results:
        try:
            importlib.import_module(module)
            _results[module] = None

        except Exception as e:
            _results[module] = e

    return _results[module]


def RequireImport(*modules: str) -> None:
    """
    Raise a `RuntimeError` if any of `modules` cannot be imported, after logging a warning.
    """
    for module in modules:
        error = CheckImport(module)
        if error is None:
            continue

        name = VENDOR_LIBRARIES.get(module, module)
        Logger("vendor", LogLevel.WARNING).Warning(f"{name} could not be found")
        raise RuntimeError(f"{name} could not be found") from error
