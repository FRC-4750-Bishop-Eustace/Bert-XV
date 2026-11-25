import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import core
import service

ROOT = Path(__file__).resolve().parents[1]


class ConfigFixture:
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.path = self.directory / "launcher.json"
        self.config = json.loads((ROOT / "launcher.json").read_text())
        self.path.write_text(json.dumps(self.config))
        self.store = core.ConfigStore(self.path, self.directory / "state")


class ConfigTests(ConfigFixture, unittest.TestCase):
    def test_real_config_and_persisted_controls(self):
        core.validate_config(self.config)
        self.store.update_settings({"rev_fullscreen": False, "rev_scale": .75})
        restored = core.ConfigStore(self.path, self.directory / "state")
        self.assertFalse(restored.settings["rev_fullscreen"])
        self.assertEqual(restored.settings["rev_scale"], .75)

    def test_reject_bad_settings_without_overwriting_good_values(self):
        for changes in [{"rev_fullscreen": "false"}, {"rev_scale": 50}, {"rev_scale": float("nan")}, {"unknown": True}]:
            with self.assertRaises(core.LauncherError):
                self.store.update_settings(changes)
        self.assertEqual(self.store.settings, self.config["settings"])

    def test_bad_layout_is_not_saved_and_good_layout_keeps_backup(self):
        before = self.path.read_bytes()
        bad = copy.deepcopy(self.config)
        bad["buttons"][0]["action"] = "missing"
        with self.assertRaises(core.LauncherError):
            self.store.save(bad)
        self.assertEqual(self.path.read_bytes(), before)
        good = copy.deepcopy(self.config)
        good["title"] = "Oscar's Trash Can"
        self.store.save(good)
        self.assertEqual(self.path.with_suffix(".json.bak").read_bytes(), before)
        self.assertEqual(self.store.config["title"], "Oscar's Trash Can")

    def test_future_select_control_and_apply_action(self):
        config = copy.deepcopy(self.config)
        config["settings"]["mode"] = "a"
        config["controls"].append({"id": "mode", "label": "Mode", "type": "select", "options": [{"label": "A", "value": "a"}, {"label": "B", "value": "b"}], "action": "apply"})
        config["actions"]["apply"] = {"type": "command", "argv": ["/bin/echo", "{value}", "{setting:mode}"]}
        self.store.save(config)
        self.store.update_settings({"mode": "b"})
        self.assertEqual(core.expand("mode={setting:mode}", self.store.settings), "mode=b")
        with self.assertRaises(core.LauncherError):
            self.store.update_settings({"mode": "unknown"})

    def test_reject_invalid_readiness_and_control_references(self):
        bad = copy.deepcopy(self.config)
        bad["backends"]["rev"]["ready_url"] = "http://0.0.0.0:{port}/"
        with self.assertRaises(core.LauncherError):
            core.validate_config(bad)
        bad = copy.deepcopy(self.config)
        bad["actions"]["launch_rev"]["steps"][1]["scale_setting"] = "missing"
        with self.assertRaises(core.LauncherError):
            core.validate_config(bad)


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.marker = str(self.directory / "fake-rev.jar")
        self.script = self.directory / "fake_backend.py"
        self.script.write_text('''import http.server
server=http.server.HTTPServer(("127.0.0.1",0),http.server.SimpleHTTPRequestHandler)
print(f"INFO Listening on: http://127.0.0.1:{server.server_port}", flush=True)
server.serve_forever()
''')
        self.backend = {"label":"Test backend", "command":[sys.executable,str(self.script),"-jar",self.marker],
                        "state_directory":str(self.directory/"backend"), "ready_pattern":r"Listening on: http://[0-9.]+:([0-9]+)",
                        "ready_url":"http://127.0.0.1:{port}/", "timeout_seconds":5}
        self.processes = []

    def tearDown(self):
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
            process.wait(timeout=5)

    def start_process(self, command, **kwargs):
        process = subprocess.Popen(command, **kwargs)
        self.processes.append(process)
        return process

    def process_args(self, pid):
        return next((p.args for p in self.processes if p.pid == pid and p.poll() is None), [])

    def test_real_http_readiness_then_reuse_without_second_backend(self):
        messages = []
        with patch("core.process_args", side_effect=self.process_args), patch("core.find_matching_process", return_value=None):
            url = core.ensure_backend(self.backend, lambda *m: messages.append(m), popen=self.start_process)
            self.assertTrue(core.local_ready(url))
            again = core.ensure_backend(self.backend, lambda *m: messages.append(m), popen=self.start_process)
        self.assertEqual(url, again)
        self.assertEqual(len(self.processes), 1)
        self.assertTrue(any("running backend" in m[0] for m in messages))

    def test_unmanaged_backend_is_not_duplicated(self):
        with patch("core.find_matching_process", return_value=123), patch("core.subprocess.Popen") as popen:
            with self.assertRaisesRegex(core.LauncherError,"outside this launcher"):
                core.ensure_backend(self.backend, lambda *m: None, popen=popen)
            popen.assert_not_called()

    def test_failed_backend_never_returns_an_old_log_url(self):
        self.script.write_text('raise SystemExit("deliberate test failure")\n')
        directory = self.directory / "backend"
        directory.mkdir()
        (directory / "server.log").write_text("Listening on: http://127.0.0.1:12345\n")
        with patch("core.find_matching_process", return_value=None):
            with self.assertRaisesRegex(core.LauncherError,"stopped during startup"):
                core.ensure_backend(self.backend, lambda *m: None, popen=self.start_process)
        self.assertNotIn("12345",(directory/"server.log").read_text())

    def test_port_parsing_rejects_bad_ports_and_handles_noise(self):
        self.assertEqual(core.ready_url(self.backend,"timeout\nINFO Listening on: http://0.0.0.0:52714\n"),"http://127.0.0.1:52714/")
        self.assertIsNone(core.ready_url(self.backend,"Listening on: http://127.0.0.1:99999"))
        self.assertIsNone(core.ready_url(self.backend,"HTTP connect timed out"))


class ActionTests(ConfigFixture, unittest.TestCase):
    def test_browser_flags_use_fullscreen_and_preserve_security(self):
        args = core.browser_arguments("chromium","/tmp/profile","http://127.0.0.1:52714/",True,.8)
        self.assertIn("--start-fullscreen",args)
        self.assertIn("--force-device-scale-factor=0.8",args)
        self.assertNotIn("--no-sandbox",args)
        self.assertNotIn("--disable-web-security",args)
        self.assertNotIn("--start-fullscreen",core.browser_arguments("chromium","/tmp/profile","http://127.0.0.1:52714/",False))
        with self.assertRaises(core.LauncherError):
            core.browser_arguments("chromium","p","javascript:alert(1)")

    def test_browser_only_opens_after_backend_is_ready(self):
        runner = core.ActionRunner(self.store)
        order = []
        with patch("core.ensure_backend",side_effect=lambda *a: order.append("ready") or "http://127.0.0.1:40000/"), patch("core.open_browser",side_effect=lambda *a: order.append("browser")):
            runner.execute(self.config["actions"]["launch_rev"],self.config,self.store.settings)
        self.assertEqual(order,["ready","browser"])
        with patch("core.ensure_backend",side_effect=core.LauncherError("failed")), patch("core.open_browser") as browser:
            with self.assertRaises(core.LauncherError):
                runner.execute(self.config["actions"]["launch_rev"],self.config,self.store.settings)
            browser.assert_not_called()

    def test_busy_action_prevents_duplicate_clicks(self):
        runner = core.ActionRunner(self.store)
        gate = threading.Event()
        with patch.object(runner,"execute",side_effect=lambda *args: gate.wait(3)):
            runner.start("launch_rev")
            try:
                with self.assertRaisesRegex(core.LauncherError,"wait"):
                    runner.start("launch_rev")
            finally:
                gate.set()
            deadline = time.monotonic()+3
            while runner.snapshot()["job"]["busy"] and time.monotonic()<deadline:
                time.sleep(.01)
        self.assertFalse(runner.snapshot()["job"]["busy"])

    def test_configured_commands_are_argument_lists_not_shell_code(self):
        runner = core.ActionRunner(self.store)
        self.store.state_directory.mkdir(exist_ok=True)
        with patch("core.subprocess.Popen") as popen:
            runner.execute({"type":"command","argv":["/bin/echo","{value}"]},self.config,self.store.settings,"$(touch /tmp/should-not-run)")
        self.assertEqual(popen.call_args.args[0],["/bin/echo","$(touch /tmp/should-not-run)"])
        self.assertNotIn("shell",popen.call_args.kwargs)


class HttpTests(ConfigFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.runner = core.ActionRunner(self.store)
        self.server = service.ThreadingHTTPServer(("127.0.0.1",0),service.BaseHTTPRequestHandler)
        self.port = self.server.server_port
        self.server.RequestHandlerClass = service.make_handler(self.store,self.runner,"test-token",self.port)
        self.thread = threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def request(self,path,body=None,token="test-token",origin=True,host=None):
        url=f"http://127.0.0.1:{self.port}{path}"
        headers={}
        if host: headers["Host"]=host
        if body is not None:
            headers.update({"Content-Type":"application/json","X-Bench-Token":token})
            if origin: headers["Origin"]=f"http://127.0.0.1:{self.port}"
        request=urllib.request.Request(url,data=None if body is None else json.dumps(body).encode(),headers=headers)
        try:
            with self.opener.open(request,timeout=3) as response:
                return response.status,response.read(),response.headers
        except urllib.error.HTTPError as error:
            try:
                return error.code,error.read(),error.headers
            finally:
                error.close()

    def test_assets_bootstrap_and_no_external_dependencies(self):
        for path in ["/","/app.js","/styles.css","/api/bootstrap","/api/state"]:
            status,data,headers=self.request(path)
            self.assertEqual(status,200,path)
            self.assertEqual(headers["Cache-Control"],"no-store")
        status,data,_=self.request("/api/bootstrap")
        self.assertEqual(json.loads(data)["token"],"test-token")
        html=(ROOT/"web/index.html").read_text()
        self.assertNotIn("src=\"https://",html)
        self.assertNotIn("href=\"https://",html)

    def test_mutations_require_both_local_origin_and_token(self):
        for token,origin in [("wrong",True),("test-token",False)]:
            status,_,_=self.request("/api/settings",{"values":{"rev_scale":.75}},token,origin)
            self.assertEqual(status,403)
        status,_,_=self.request("/api/settings",{"values":{"rev_scale":.75}})
        self.assertEqual(status,200)
        self.assertEqual(self.store.settings["rev_scale"],.75)

    def test_dns_rebinding_and_path_traversal_are_rejected(self):
        self.assertEqual(self.request("/api/bootstrap",host="evil.example")[0],403)
        self.assertEqual(self.request("/../launcher.json")[0],404)

    def test_bad_config_does_not_replace_working_configuration(self):
        invalid=copy.deepcopy(self.config)
        invalid["controls"][1]["step"]=0
        status,_,_=self.request("/api/config",{"config":invalid})
        self.assertEqual(status,400)
        self.assertEqual(json.loads(self.path.read_text()),self.config)


if __name__ == "__main__":
    unittest.main()
