# OS Optimizer

System health monitor and optimizer with a native desktop GUI.

## Stack
- **Language**: Python 3.11+
- **UI**: PySide6 (Qt6) with Catppuccin Mocha dark theme
- **Platform (now)**: Linux (Arch). Windows support is future work.
- **DI**: Constructor injection — no DI framework. ABCs in `core/interfaces.py`, factory in `platform/__init__.py`.

## Project structure
```
src/os_optimizer/
  core/interfaces.py       ABCs + data classes (no imports from platform or ui)
  platform/__init__.py     Factory: get_disk_analyzer(), get_package_manager(), get_health_checker()
  platform/linux/          Concrete Linux implementations
  ui/main_window.py        QMainWindow, sidebar, QStackedWidget
  ui/views/                One view per feature (dashboard, disk, packages, health)
  ui/theme.py              QSS stylesheet
```

## Feature status
| Feature | Status |
|---|---|
| Main window + sidebar navigation | ✅ |
| Dashboard (live CPU/RAM/Disk gauges) | ✅ |
| Disk view (partition usage + large dirs) | ✅ |
| Packages view (checkupdates + apply) | ✅ |
| Health view (permissions, config checks) | ✅ |

## Running
```bash
python -m pip install -e .
python -m os_optimizer
```
Requires `pacman-contrib` for update checking (`sudo pacman -S pacman-contrib`).

## Auto-commit workflow
After completing a feature, write a one-line summary to `.claude/pending_commit.txt`.
The Stop hook at `.claude/scripts/auto-commit.sh` picks it up and commits.
The file is gitignored so it never gets committed itself.

## Coding rules
1. **Think before coding** — state assumptions, surface tradeoffs, ask when uncertain.
2. **Simplicity first** — minimum code that solves the problem. No speculative features.
3. **Surgical changes** — touch only what the task requires. Match existing style.
4. **Goal-driven** — define verifiable success criteria before implementing.
5. SOLID + constructor injection. No over-abstraction.

## Linux privilege for updates
`sudo pacman -Syu --noconfirm` is run via QProcess. The user needs password-less sudo for pacman,
or the update button will fail with a permission error shown in the output dialog.

Example sudoers line:
```
username ALL=(ALL) NOPASSWD: /usr/bin/pacman
```
