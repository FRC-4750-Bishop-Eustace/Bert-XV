# Validation — 2026-11-24

- 17 automated checks passed on the development Mac.
- A real local HTTP stub verified backend startup, readiness, and reuse without launching a second backend.
- A failed backend prevented the browser step; stale log URLs were rejected.
- Control persistence, configuration validation and backup, explicit Apply actions, single launch concurrency, and shell-free command arguments passed.
- Local-only host checks and action origin/token checks passed.
- Python compilation, JavaScript syntax, and installer shell syntax passed.
- The actual UI was inspected at 800×480 and the normal browser size.
- Browser interaction verified a saved toggle survives reload, an added JSON-defined button appears, and the backend log viewer opens. Preview defaults were restored afterward.

The Pi's live Java/backend/Chromium sequence has not been verified by this session because SSH to the bench Pi was blocked before authentication. The REV command and JNA paths are taken from the working command previously run on the Pi. No motor commands were issued.

## 1024 × 600 layout update

- Added landscape spacing for 551–700 pixel tall displays, including the target 1024 × 600 touchscreen.
- Navigation and status remain outside the scrollable main area. The configuration editor uses the available height, with its toolbar and save controls kept in the layout.
- Switching tabs resets the content scroll position.
- The 5 existing configuration tests and 4 existing action tests passed. JavaScript syntax, CSS parsing, and installer shell syntax passed.
- A new visual check could not run: this environment blocks the local HTTP listener and headless browser startup, and the connected browser runtime is unavailable. The earlier visual validation above predates this update. A live 1024 × 600 check on the Pi is still needed.

## User verification on the Raspberry Pi

- The user tested launching REV on the Pi and confirmed it works after setting REV display scale to 100% and keeping fullscreen enabled.
- The packaged default is now 100%. Previously saved settings are preserved during installation.
- This confirms the reported REV display issue is resolved. A complete visual inspection of every launchpad tab has not been independently verified.
