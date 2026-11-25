"""Local configuration, process management, and action execution. No third-party modules."""
from __future__ import annotations

import copy
import fcntl
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request


class LauncherError(Exception):
    pass


IDENTIFIER = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
TOKEN = re.compile(r"\{(home|port|value|setting:[A-Za-z0-9_-]+|backend:[A-Za-z0-9_-]+)\}")


def read_json(path, fallback=None):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return copy.deepcopy(fallback)


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n")
    temporary.chmod(0o600)
    temporary.replace(path)


def setting_value(control, value):
    kind = control["type"]
    if kind == "toggle":
        if type(value) is not bool:
            raise LauncherError(f"{control['label']} needs an on/off value.")
    elif kind == "slider":
        if type(value) not in (int, float) or not math.isfinite(value):
            raise LauncherError(f"{control['label']} needs a finite number.")
        low, high, step = control["min"], control["max"], control.get("step", 1)
        if not low <= value <= high:
            raise LauncherError(f"{control['label']} must be between {low} and {high}.")
        value = round(low + round((value - low) / step) * step, 8)
        value = min(high, max(low, value))
    elif kind == "select":
        if value not in [option["value"] for option in control["options"]]:
            raise LauncherError(f"Choose a valid value for {control['label']}.")
    return value


def validate_config(config):
    """Reject broken references before saving or executing a configuration."""
    try:
        if config.get("schema_version") != 1:
            raise LauncherError("This launcher needs schema_version 1.")
        if not isinstance(config["title"], str) or not config["title"].strip():
            raise LauncherError("Give the launcher a title.")
        if not isinstance(config["actions"], dict) or not isinstance(config["backends"], dict):
            raise LauncherError("Actions and backends must be JSON objects.")
        if not isinstance(config["browser_command"], str) or not config["browser_command"]:
            raise LauncherError("Set browser_command to your Chromium executable.")
        for group in (config["actions"], config["backends"], config["settings"]):
            if not isinstance(group, dict) or any(not IDENTIFIER.fullmatch(k) for k in group):
                raise LauncherError("Use letters, digits, hyphens, or underscores for IDs.")
        controls = {}
        for control in config["controls"]:
            key, kind = control["id"], control["type"]
            if not IDENTIFIER.fullmatch(key) or key in controls or key not in config["settings"]:
                raise LauncherError("Each control needs a unique ID and a matching setting.")
            if kind not in ("toggle", "slider", "select"):
                raise LauncherError("Controls support toggle, slider, or select.")
            if not isinstance(control["label"], str):
                raise LauncherError("Each control needs a label.")
            if kind == "slider":
                values = [control["min"], control["max"], control.get("step", 1)]
                if any(type(v) not in (int, float) or not math.isfinite(v) for v in values):
                    raise LauncherError("Slider bounds and step must be finite numbers.")
                if values[0] >= values[1] or values[2] <= 0:
                    raise LauncherError("Slider minimum must be below maximum, with a positive step.")
            if kind == "select":
                if not control["options"] or any(not isinstance(o["label"], str) for o in control["options"]):
                    raise LauncherError("A select control needs labeled options.")
            setting_value(control, config["settings"][key])
            if control.get("action") and control["action"] not in config["actions"]:
                raise LauncherError(f"Unknown action for control {key}.")
            controls[key] = control
        button_ids = set()
        for button in config["buttons"]:
            key = button["id"]
            if not IDENTIFIER.fullmatch(key) or key in button_ids:
                raise LauncherError("Buttons need unique IDs.")
            if not isinstance(button["label"], str) or button["action"] not in config["actions"]:
                raise LauncherError(f"Button {key} needs a label and a valid action.")
            button_ids.add(key)

        def step_check(step, depth=0):
            if depth > 8:
                raise LauncherError("Action pipelines are nested too deeply.")
            kind = step["type"]
            if kind == "pipeline":
                if not step["steps"]:
                    raise LauncherError("A pipeline needs at least one step.")
                for child in step["steps"]:
                    step_check(child, depth + 1)
            elif kind in ("ensure_backend", "show_log"):
                if step["backend"] not in config["backends"]:
                    raise LauncherError("An action refers to an unknown backend.")
            elif kind == "open_browser":
                if "backend" in step and step["backend"] not in config["backends"]:
                    raise LauncherError("Browser action refers to an unknown backend.")
                if "backend" not in step and not step.get("url"):
                    raise LauncherError("A browser action needs a backend or URL.")
                if not IDENTIFIER.fullmatch(step.get("profile", "tool")):
                    raise LauncherError("Browser profile names must be simple IDs.")
                for key, expected in (("fullscreen_setting", "toggle"), ("scale_setting", "slider")):
                    if key in step and (step[key] not in controls or controls[step[key]]["type"] != expected):
                        raise LauncherError(f"{key} must refer to a matching control.")
            elif kind == "command":
                if not isinstance(step["argv"], list) or not step["argv"] or any(not isinstance(a, str) for a in step["argv"]):
                    raise LauncherError("A command needs a non-empty argv list of strings.")
            else:
                raise LauncherError(f"Unknown action type: {kind}")

        for action in config["actions"].values():
            step_check(action)
        for key, backend in config["backends"].items():
            command = backend["command"]
            if not isinstance(command, list) or not command or any(not isinstance(a, str) for a in command):
                raise LauncherError(f"Backend {key} needs a command list.")
            pattern = re.compile(backend["ready_pattern"])
            if pattern.groups != 1:
                raise LauncherError("A ready_pattern must have exactly one capturing group for the port.")
            url = urllib.parse.urlsplit(backend["ready_url"].replace("{port}", "12345"))
            if url.scheme != "http" or url.hostname not in ("127.0.0.1", "localhost"):
                raise LauncherError("Backend readiness must use local HTTP.")
            timeout = backend.get("timeout_seconds", 120)
            if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 1 <= timeout <= 600:
                raise LauncherError("Backend timeout must be between 1 and 600 seconds.")
            if not isinstance(backend.get("environment", {}), dict) or any(not isinstance(v, str) for v in backend.get("environment", {}).values()):
                raise LauncherError("Backend environment values must be strings.")
    except (KeyError, TypeError, ValueError, AttributeError, re.error) as exc:
        raise LauncherError(f"Invalid launcher configuration: {exc}") from exc
    return config


class ConfigStore:
    def __init__(self, path, state_directory):
        self.path, self.state_directory = Path(path), Path(state_directory)
        self.lock = threading.RLock()
        self.load()

    def load(self):
        with self.lock:
            try:
                config = validate_config(json.loads(self.path.read_text()))
            except (OSError, ValueError) as exc:
                raise LauncherError(f"Cannot read {self.path}: {exc}") from exc
            saved = read_json(self.state_directory / "settings.json", {})
            settings = copy.deepcopy(config["settings"])
            for control in config["controls"]:
                key = control["id"]
                if key in saved:
                    try:
                        settings[key] = setting_value(control, saved[key])
                    except LauncherError:
                        pass
            self.config, self.settings = config, settings

    def snapshot(self):
        with self.lock:
            return copy.deepcopy(self.config), copy.deepcopy(self.settings)

    def update_settings(self, values):
        with self.lock:
            if not isinstance(values, dict):
                raise LauncherError("Settings must be a JSON object.")
            controls = {c["id"]: c for c in self.config["controls"]}
            updated = dict(self.settings)
            for key, value in values.items():
                if key not in controls:
                    raise LauncherError(f"Unknown control: {key}")
                updated[key] = setting_value(controls[key], value)
            atomic_json(self.state_directory / "settings.json", updated)
            self.settings = updated

    def save(self, config):
        with self.lock:
            validate_config(config)
            backup = self.path.with_suffix(".json.bak")
            if self.path.exists():
                shutil.copy2(self.path, backup)
            atomic_json(self.path, config)
            self.load()


def expand(text, settings=None, urls=None, **values):
    values = {"home": str(Path.home()), **values}
    settings, urls = settings or {}, urls or {}

    def replace(match):
        key = match.group(1)
        if key.startswith("setting:"):
            value = settings[key.split(":", 1)[1]]
        elif key.startswith("backend:"):
            value = urls[key.split(":", 1)[1]]
        else:
            value = values[key]
        return str(value).lower() if type(value) is bool else str(value)

    return TOKEN.sub(replace, text)


def tail_text(path, limit=65536):
    try:
        with Path(path).open("rb") as stream:
            stream.seek(0, 2)
            stream.seek(max(0, stream.tell() - limit))
            return stream.read().decode("utf-8", errors="replace")
    except OSError:
        return ""


def process_args(pid):
    try:
        if Path(f"/proc/{pid}").stat().st_uid != os.getuid():
            return []
        return [arg.decode(errors="replace") for arg in Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0") if arg]
    except OSError:
        return []


def find_matching_process(marker):
    if not marker or not Path("/proc").is_dir():
        return None
    for path in Path("/proc").iterdir():
        if path.name.isdigit() and marker in process_args(int(path.name)):
            return int(path.name)
    return None


def local_ready(url):
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(url, timeout=1) as response:
            return response.status == 200
    except urllib.error.HTTPError as error:
        error.close()
        return False
    except (OSError, ValueError, urllib.error.URLError):
        return False


def ready_url(backend, log):
    matches = list(re.finditer(backend["ready_pattern"], log))
    if not matches:
        return None
    port = matches[-1].group(1)
    if not port.isdigit() or not 1 <= int(port) <= 65535:
        return None
    return expand(backend["ready_url"], port=port)


def backend_state(backend):
    directory = Path(expand(backend["state_directory"]))
    return directory, directory / "server.pid", directory / "server.log"


def backend_marker(command):
    if "-jar" in command:
        return command[command.index("-jar") + 1]
    return command[0]


def ensure_backend(backend, notify, probe=local_ready, popen=subprocess.Popen):
    command = [expand(arg) for arg in backend["command"]]
    for name in backend.get("required_files", []):
        if not Path(expand(name)).is_file():
            raise LauncherError(f"A required REV file is missing: {expand(name)}")
    if not (Path(command[0]).is_file() or shutil.which(command[0])):
        raise LauncherError(f"Cannot find the backend executable: {command[0]}")
    directory, pid_path, log_path = backend_state(backend)
    directory.mkdir(parents=True, exist_ok=True)
    marker = backend_marker(command)
    with (directory / "launch.lock").open("w") as lock:
        deadline = time.monotonic() + backend.get("timeout_seconds", 120)
        while True:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                notify("Waiting for the current backend launch…", "backend")
                if time.monotonic() > deadline:
                    raise LauncherError("Another backend launch is still in progress.")
                time.sleep(0.2)
        try:
            pid = int(pid_path.read_text().strip())
        except (OSError, ValueError):
            pid = 0
        process = None
        if not pid or marker not in process_args(pid):
            unmanaged = find_matching_process(marker)
            if unmanaged:
                raise LauncherError("REV is already running outside this launcher. Stop that older REV terminal with Ctrl+C once, then try again.")
            notify("Starting the REV backend…", "backend")
            with log_path.open("w") as output:
                process = popen(command, env={**os.environ, **backend.get("environment", {})},
                                stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT,
                                start_new_session=True, close_fds=True)
            pid = process.pid
            pid_path.write_text(str(pid) + "\n")
        else:
            notify("Connecting to the running backend…", "backend")
        deadline = time.monotonic() + backend.get("timeout_seconds", 120)
        while time.monotonic() < deadline:
            url = ready_url(backend, tail_text(log_path, 1024 * 1024))
            if url and probe(url):
                notify("REV backend is ready", "ready")
                return url
            if process is not None and process.poll() is not None:
                raise LauncherError("REV stopped during startup. Open Backend log for the error.")
            if process is None and marker not in process_args(pid):
                raise LauncherError("The REV backend stopped. Launch REV again.")
            time.sleep(0.5)
        raise LauncherError("REV did not become ready within the startup timeout. Open Backend log for details.")


def browser_arguments(executable, profile, url, fullscreen=True, scale=1.0):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise LauncherError("Browser URLs must begin with http:// or https://.")
    if type(scale) not in (int, float) or not math.isfinite(scale) or not 0.5 <= scale <= 2:
        raise LauncherError("Browser display scale must be between 0.5 and 2.")
    args = [executable, f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check",
            "--new-window", f"--force-device-scale-factor={scale:g}", f"--app={url}"]
    if fullscreen:
        args.append("--start-fullscreen")
    return args


def open_browser(config, state_directory, profile, url, fullscreen=True, scale=1.0):
    executable = shutil.which(config["browser_command"])
    if not executable:
        raise LauncherError("Chromium was not found. Check browser_command in Configuration.")
    # Distinct profiles prevent a normal Chromium session from swallowing fullscreen flags.
    directory = Path(state_directory) / "browsers" / profile
    directory.mkdir(parents=True, exist_ok=True)
    args = browser_arguments(executable, directory, url, fullscreen, scale)
    log_path = Path(state_directory) / "browser.log"
    with log_path.open("a") as output:
        process = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=output,
                                   stderr=subprocess.STDOUT, close_fds=True, start_new_session=True)
    if profile == "launchpad":
        atomic_json(Path(state_directory) / "dashboard-browser.json", {"pid": process.pid, "marker": args[1]})
    time.sleep(0.4)
    if process.poll() not in (None, 0):
        raise LauncherError("Chromium could not open. Launch from the Pi desktop and check browser.log.")


class ActionRunner:
    def __init__(self, store):
        self.store = store
        self.lock, self.job_lock = threading.RLock(), threading.Lock()
        self.job = {"busy": False, "phase": "idle", "message": "Ready to launch", "error": False}
        self.events, self.urls = [], {}

    def notify(self, message, phase="working"):
        with self.lock:
            self.job.update(message=message, phase=phase)
            self.events.append({"time": time.strftime("%H:%M:%S"), "message": message})
            self.events = self.events[-80:]

    def snapshot(self):
        with self.lock:
            return {"job": dict(self.job), "events": list(self.events), "urls": dict(self.urls)}

    def start(self, action_id, value=None):
        config, settings = self.store.snapshot()
        if action_id not in config["actions"]:
            raise LauncherError("Unknown action.")
        if not self.job_lock.acquire(blocking=False):
            raise LauncherError("Please wait for the current action to finish.")
        with self.lock:
            self.job.update(busy=True, error=False, phase="working", message="Preparing…")
        threading.Thread(target=self._run, args=(config, settings, action_id, value), daemon=True).start()

    def _run(self, config, settings, action_id, value):
        try:
            self.execute(config["actions"][action_id], config, settings, value)
            with self.lock:
                if self.job["phase"] != "log":
                    self.job.update(phase="complete", message="Ready — REV is open" if action_id == "launch_rev" else "Action complete")
        except Exception as exc:
            self.notify(str(exc), "error")
            with self.lock:
                self.job["error"] = True
        finally:
            with self.lock:
                self.job["busy"] = False
            self.job_lock.release()

    def execute(self, step, config, settings, value=None):
        kind = step["type"]
        if kind == "pipeline":
            for child in step["steps"]:
                self.execute(child, config, settings, value)
        elif kind == "ensure_backend":
            url = ensure_backend(config["backends"][step["backend"]], self.notify)
            with self.lock:
                self.urls[step["backend"]] = url
        elif kind == "open_browser":
            with self.lock:
                urls = dict(self.urls)
            url = urls.get(step.get("backend")) if "backend" in step else expand(step["url"], settings, urls, value=value)
            if not url:
                raise LauncherError("Start the backend before opening its browser window.")
            fullscreen = settings[step["fullscreen_setting"]] if "fullscreen_setting" in step else step.get("fullscreen", True)
            scale = settings[step["scale_setting"]] if "scale_setting" in step else step.get("scale", 1.0)
            self.notify("Opening the browser…", "browser")
            open_browser(config, self.store.state_directory, step.get("profile", "tool"), url, fullscreen, scale)
            self.notify("Browser launch complete", "complete")
        elif kind == "show_log":
            self.notify("Backend log opened", "log")
        elif kind == "command":
            with self.lock:
                urls = dict(self.urls)
            args = [expand(arg, settings, urls, value=value) for arg in step["argv"]]
            if not (Path(args[0]).is_file() or shutil.which(args[0])):
                raise LauncherError(f"Application not found: {args[0]}")
            with (self.store.state_directory / "tools.log").open("a") as output:
                subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT,
                                 start_new_session=True, close_fds=True)
            self.notify("Application launched", "complete")


def close_dashboard(state_directory):
    record = read_json(Path(state_directory) / "dashboard-browser.json", {})
    pid, marker = record.get("pid"), record.get("marker")
    if marker and (not pid or marker not in process_args(pid)):
        pid = find_matching_process(marker)
    if pid and marker and marker in process_args(pid):
        os.kill(pid, signal.SIGTERM)
