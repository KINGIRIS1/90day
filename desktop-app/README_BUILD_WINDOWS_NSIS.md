Windows Build Guide (NSIS, system Python)
App: 90dayChonThanh | Company: Nguyen Thin Trung | Version: 1.1.0 | Arch: x64



Summary
- Target: 90dayChonThanh v1.1.0 (x64)
- Installer: NSIS all-in-one via electron-builder
- Python: Use system Python 3.10–3.12. No vendored packages.
- Gemini Flash: Reads GOOGLE_API_KEY from your machine (store inside app Settings or set env var). Placeholder used in build.

Prerequisites
1) Node.js + Yarn
2) NSIS (latest) in PATH: https://nsis.sourceforge.io/Download
3) Python 3.10/3.11/3.12 installed (py launcher recommended)
4) Clean local python folder (run scripts/clean-local-python.ps1)

Build steps
1) Install deps
   - yarn
2) Clean local python vendor remnants (avoid PIL/_imaging, requests errors)
   - powershell -ExecutionPolicy Bypass -File .\\scripts\\clean-local-python.ps1
3) Set optional env for Gemini Flash (or set inside app Settings)
   - setx GOOGLE_API_KEY your_key_here
4) Build installer
   - yarn build
   - yarn dist:win

First run after install (enable logs)
- set ELECTRON_ENABLE_LOGGING=1
- "%LocalAppData%\\Programs\\90dayChonThanh\\90dayChonThanh.exe" --enable-logging

Troubleshooting
- Missing library: requests / ImportError: _imaging from PIL
  -> Ensure step (2) was executed, and system Python has Pillow/requests installed
  -> Electron sets PYTHONPATH to include system site-packages automatically
- Python not found
  -> Install Python 3.10–3.12 and ensure 'py' or 'python' is in PATH

Uninstall
- Use Windows Control Panel or Uninstall shortcut.
