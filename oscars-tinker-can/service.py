#!/usr/bin/env python3
"""Offline touchscreen launchpad. HTTP is restricted to this computer's loopback."""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

from core import ActionRunner, ConfigStore, LauncherError, backend_state, close_dashboard, open_browser, tail_text

APP_ID = "oscars-tinker-can-v1"
ROOT = Path(__file__).resolve().parent


def make_handler(store, runner, token, port):
    origins = {f"http://127.0.0.1:{port}", f"http://localhost:{port}"}
    hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            # Polling is intentionally quiet; errors still appear in the launcher log.
            if len(args) > 1 and str(args[1]).startswith("2"):
                return
            super().log_message(fmt, *args)

        def reply(self, status, value, content_type="application/json"):
            body = json.dumps(value).encode() if content_type == "application/json" else value
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(body)

        def valid_host(self):
            if self.headers.get("Host") not in hosts:
                self.reply(403, {"error": "This launcher accepts local requests only."})
                return False
            return True

        def do_GET(self):
            if not self.valid_host():
                return
            route = self.path.split("?", 1)[0]
            if route == "/api/identity":
                self.reply(200, {"app_id": APP_ID, "config_path": str(store.path)})
            elif route == "/api/bootstrap":
                config, settings = store.snapshot()
                self.reply(200, {"config": config, "settings": settings, "token": token, "config_path": str(store.path)})
            elif route == "/api/state":
                self.reply(200, runner.snapshot())
            elif route.startswith("/api/log/"):
                config, _ = store.snapshot()
                name = route.rsplit("/", 1)[-1]
                if name not in config["backends"]:
                    self.reply(404, {"error": "Unknown backend."})
                    return
                _, _, log = backend_state(config["backends"][name])
                self.reply(200, {"text": tail_text(log) or "No backend log yet. Launch REV to create it."})
            elif route in ("/", "/app.js", "/styles.css"):
                file_name, kind = {"/": ("index.html", "text/html; charset=utf-8"),
                                   "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                                   "/styles.css": ("styles.css", "text/css; charset=utf-8")}[route]
                self.reply(200, (ROOT / "web" / file_name).read_bytes(), kind)
            else:
                self.reply(404, {"error": "Not found."})

        def do_POST(self):
            if not self.valid_host():
                return
            if self.headers.get("Origin") not in origins or not secrets.compare_digest(self.headers.get("X-Bench-Token", ""), token):
                self.reply(403, {"error": "Open this action from the launchpad."})
                return
            if self.headers.get_content_type() != "application/json":
                self.reply(415, {"error": "Use JSON for launcher actions."})
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 262144:
                    raise LauncherError("The request is empty or too large.")
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict):
                    raise LauncherError("The request must be an object.")
                route = self.path
                if route == "/api/action":
                    runner.start(body.get("action"), body.get("value"))
                    self.reply(202, {"ok": True})
                elif route == "/api/settings":
                    store.update_settings(body.get("values"))
                    self.reply(200, {"ok": True, "settings": store.snapshot()[1]})
                elif route == "/api/config":
                    if runner.snapshot()["job"]["busy"]:
                        raise LauncherError("Wait until the current launch finishes before changing the layout.")
                    store.save(body["config"])
                    self.reply(200, {"ok": True})
                elif route == "/api/reload":
                    if runner.snapshot()["job"]["busy"]:
                        raise LauncherError("Wait until the current launch finishes before reloading.")
                    store.load()
                    self.reply(200, {"ok": True})
                elif route == "/api/desktop":
                    self.reply(200, {"ok": True})
                    threading.Timer(0.3, close_dashboard, args=(store.state_directory,)).start()
                else:
                    self.reply(404, {"error": "Unknown action endpoint."})
            except (LauncherError, ValueError, TypeError, KeyError) as exc:
                self.reply(400, {"error": str(exc)})
            except OSError as exc:
                self.reply(500, {"error": f"Could not save the change: {exc}"})

    return Handler


def identity(port):
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(f"http://127.0.0.1:{port}/api/identity", timeout=0.5) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        error.close()
        return None
    except (OSError, ValueError, urllib.error.URLError):
        return None


def main():
    parser = argparse.ArgumentParser(description="Oscar's Tinker Can touchscreen launcher")
    parser.add_argument("--config", type=Path, default=Path.home() / ".config/oscars-tinker-can/launcher.json")
    parser.add_argument("--state", type=Path, default=Path.home() / ".local/state/oscars-tinker-can")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Choose a port between 1024 and 65535.")
    args.config = args.config.expanduser().resolve()
    args.state = args.state.expanduser().resolve()
    args.state.mkdir(parents=True, exist_ok=True)
    store = ConfigStore(args.config, args.state)
    if args.check:
        print(f"Configuration is valid: {args.config}")
        return
    if args.serve:
        runner = ActionRunner(store)
        handler = make_handler(store, runner, secrets.token_urlsafe(32), args.port)
        server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
        print(f"Oscar's Tinker Can is ready at http://127.0.0.1:{args.port}/", flush=True)
        server.serve_forever()
        return
    if sys.platform.startswith("linux") and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        raise LauncherError("Open the shortcut from the Pi desktop. SSH can install it, but does not provide a display.")
    existing = identity(args.port)
    if existing and (existing.get("app_id") != APP_ID or existing.get("config_path") != str(args.config)):
        raise LauncherError("Another launchpad is using this port with a different configuration.")
    if not existing:
        with (args.state / "launcher.log").open("a") as output:
            process = subprocess.Popen([sys.executable, "-u", str(ROOT / "service.py"), "--serve", "--config", str(args.config),
                                        "--state", str(args.state), "--port", str(args.port)],
                                       stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT,
                                       start_new_session=True, close_fds=True)
        for _ in range(100):
            existing = identity(args.port)
            if existing and existing.get("app_id") == APP_ID and existing.get("config_path") == str(args.config):
                break
            if process.poll() is not None:
                raise LauncherError("The launchpad could not start. Check ~/.local/state/oscars-tinker-can/launcher.log.")
            time.sleep(0.1)
        else:
            raise LauncherError("The launchpad took too long to start. Check launcher.log.")
    config, _ = store.snapshot()
    open_browser(config, args.state, "launchpad", f"http://127.0.0.1:{args.port}/", fullscreen=True)


if __name__ == "__main__":
    try:
        main()
    except (LauncherError, OSError) as error:
        print(f"Launcher: {error}", file=sys.stderr)
        sys.exit(1)
