# Oscar's Tinker Can

A local, offline touchscreen launchpad for the Raspberry Pi bench. A large **Launch REV** button starts the working headless REV Hardware Client backend, waits for local HTTP readiness, then opens Chromium fullscreen. The green street-sign theme, metal trash can, and workshop mascot are configurable starting points for BErt 4750.

## Requirements

- Raspberry Pi OS 64-bit Desktop, with its existing Python 3 and Chromium. No pip packages, Tkinter, CDN, web fonts, or internet service are required.
- The already-working REV 1.4.7 ARM64 installation under `/usr/lib/rev-robotics/rev-hardware-client/`.
- The already-installed Java runtime at `~/.local/share/frc-java25/bin/java`.
- Run the UI from the Pi desktop, where a graphical session exists. SSH is suitable for installing and editing files.

## Install

The launcher lives in `oscars-tinker-can/` in the Bert-XV preseason repository. After cloning the repository, use that folder as the source for the copy command below. It is a standalone Pi application and has no RobotPy dependency.

1. Stop any motor run in REV. If an older manually launched backend is running, press Ctrl+C in its terminal once. The new launcher can reuse a backend managed by the earlier `rev-bench` shortcut.
2. From the root of the cloned repository, copy this folder to the Pi. Replace `pi-user` and `pi-hostname.local` with the Pi desktop account and hostname.

   ```sh
   scp -r ./oscars-tinker-can pi-user@pi-hostname.local:~/
   ssh pi-user@pi-hostname.local 'bash ~/oscars-tinker-can/install.sh'
   ```

3. On the Pi desktop, double-click **Oscar's Tinker Can**. Accept **Execute** or **Trust and Launch** if asked.
4. Tap **Launch REV**. Allow up to two minutes on the first start. It does not command a motor; use the REV controls for motor tests.

The installer downloads nothing and does not change the original REV installation. It installs the application in `~/.local/share/oscars-tinker-can/`, configuration in `~/.config/oscars-tinker-can/launcher.json`, and the desktop command in `~/.local/bin/oscar-launcher`. Reinstalling preserves your custom configuration.

To open only the launchpad automatically after desktop login, explicitly install with:

```sh
bash ~/oscars-tinker-can/install.sh --autostart
```

Disable that later by removing only `~/.config/autostart/oscars-tinker-can.desktop`. The launchpad opening never automatically runs the configured actions.

## Touchscreen use

The layout is optimized for a **1024 × 600 landscape display**. Navigation and workshop status stay visible while longer pages scroll within the content area. The configuration editor fills the available space, keeping its save button accessible. Smaller screens continue to use the responsive layout.

- **Launchpad:** large configurable tool buttons, startup progress, and a backend-log viewer.
- **Controls:** saved REV fullscreen and display-scale options. The default REV display scale is 100%, matching the working Pi setup. Existing installations retain their saved setting; select 100% here if REV appears reduced, then close and reopen the REV window.
- **Activity:** recent launcher messages.
- **Configuration:** edit the JSON, then **Save & reload layout**. Invalid configurations are rejected and the previous file is backed up as `launcher.json.bak`. **Reload file** reads changes made over SSH.
- **Desktop:** closes only the launchpad's Chromium window. It does not stop REV or other applications.
- To leave the REV fullscreen window, use **F11**, then close that window to return to the launchpad beneath it. **Alt+F4** closes the current window. Standard Raspberry Pi touchscreen/window-manager gestures also remain available.
- Fullscreen and scale apply when opening a REV browser window. Close an existing REV browser window before reopening if you changed display options, so Chromium applies its new startup settings. The backend can remain running.

## Add a button

In **Configuration**, append this to `buttons`:

```json
{
  "id": "files",
  "label": "Project files",
  "description": "Open your saved bench projects.",
  "icon": "tool",
  "action": "open_files"
}
```

Add its matching entry inside `actions`:

```json
"open_files": {
  "type": "command",
  "argv": ["/usr/bin/pcmanfm", "{home}/Documents"]
}
```

Save and reload. Use `enabled: false` on a button or control to hide it temporarily. Supported icons are `play`, `log`, and `tool`; unknown icons use `tool`. Set a primary button's `accent` to `orange`, `green`, or `blue` to change its color.

## Add controls and action sequences

The supported controls are `toggle`, `slider`, and `select`. Each control's `id` must have a default in `settings`. Current choices are saved separately and survive restarts. Bounds and types are validated. If new bounds make a saved choice invalid, its configured default is used.

A control normally only saves a setting. Add an `action` ID to display an explicit **Apply** button. Moving a slider or flipping a toggle never runs a command automatically. `examples.json` includes ready-to-copy control examples.

Action types:

| Type | Purpose |
| --- | --- |
| `pipeline` | Execute `steps` in order; a failed step prevents later steps. |
| `ensure_backend` | Start or reuse a configured local backend and wait for HTTP readiness. |
| `open_browser` | Open an HTTP(S) URL or a backend's discovered URL in Chromium. |
| `show_log` | View a configured backend's startup log. Use directly on a button. |
| `command` | Start an installed program with an argument list. No shell evaluation. |

Templates in command arguments and URLs: `{home}`, `{value}` (an explicit Apply value), `{setting:ID}`, and `{backend:ID}`. Backend `ready_url` additionally supports `{port}`. Environment variables for a backend are set in its `environment` object. Environment variable and shell substitution such as `$HOME` or `$(...)` are deliberately not evaluated; use `{home}` instead.

Future local web tools can define another `backends` entry with a command list, readiness-log regex containing one port capture, local `ready_url`, and state directory. Build a pipeline of `ensure_backend` then `open_browser` as in the included REV configuration. Executables must already be installed. No motor-control API or hardware command is included by default.

Change `title`, `subtitle`, and `theme.accent` / `theme.street_sign` in Configuration to rename or recolor the station. Theme colors are six-digit hex values.

## Offline behavior and troubleshooting

The launchpad binds only `127.0.0.1:8787`; its scripts, styling, icons, and images are all local. REV also binds only local HTTP. Normal USB/CAN bench use needs no internet. Prepare firmware-update packs in REV while online if you want offline firmware updates.

- The FTC Control Hub ping timeout can still appear in REV logs without an FTC hub present; this does not itself indicate a failed SPARK connection.
- The roboRIO must remain disconnected from CAN for REV USB motor control, and the SPARKs must be fully power-cycled after removing it. Keep appropriate CAN termination on the bench.
- If REV was updated, change the JAR path in the backend command and `required_files` to its installed version. The default is the version already proven on this Pi, 1.4.7.
- The launchpad logs to `~/.local/state/oscars-tinker-can/launcher.log`. Browser diagnostics are in `browser.log`; configured commands log to `tools.log`.
- REV uses `~/.local/state/rev-bench/server.log` and `server.pid`, compatible with the previous offline shortcut. It will not terminate or replace an unrecognized manually started REV instance.
- To see startup errors, run `~/.local/bin/oscar-launcher` **in a Pi desktop terminal**.
- To validate configuration over SSH: `python3 ~/.local/share/oscars-tinker-can/service.py --check`.
- Closing the launchpad does not shut down its service or the REV backend. Shut down the Pi normally before removing its power.

To test the application source without installed hardware:

```sh
python3 -m unittest discover -s tests -v
python3 service.py --config launcher.json --state /tmp/tinker-can-preview --serve
```

Visit `http://127.0.0.1:8787/`. Launching REV requires the real Pi installation. There is no automatic motor output on page load, service start, or launcher login autostart.
