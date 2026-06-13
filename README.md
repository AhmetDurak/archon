# Archon

A native desktop app for monitoring and optimizing Linux systems.  
Built with Python + PySide6 (Qt6). Catppuccin Mocha dark theme.

---

## Features

| View | What it does |
|---|---|
| **Dashboard** | Live CPU / RAM / Disk gauges, refreshed every 2 s. Summary cards show pending updates and health issues. One-click "Apply All Updates" button when updates are available. |
| **Disk Usage** | Partition overview with a donut chart. On-demand scanner shows the largest files and directories under any path. Btrfs subvolumes appear immediately; their sizes fill in via background scan. Sortable/resizable columns with a `% of disk` column. |
| **Packages** | Calls `checkupdates` (pacman-contrib) to list outdated packages without touching the system. Applies updates with live terminal output. |
| **Health** | Scans for permission issues, orphaned packages, broken symlinks, stale autostart entries, oversized pacman cache, and more. Each issue has an inline "Fix" button that runs the fix with live terminal output. |
| **Installed Apps** | Lists all installed packages with version, size, install date, and description tooltip. Sortable by any column (size descending by default). Search by name. "Remove" button runs `pacman -Rns` with live output. Removing a package auto-refreshes the Packages and Health counts on the dashboard. |

### Health checks

| Check | Category | Severity |
|---|---|---|
| `/tmp`, `/var/tmp` permissions (must be 1777) | permission | warning |
| Home directory world-accessible | permission | warning |
| `~/.ssh` permissions (must be 700) | permission | error |
| SSH private key permissions (must be 600) | permission | error |
| `~/.ssh/authorized_keys` permissions | permission | warning |
| `~/.gnupg` permissions (must be 700) | permission | error |
| `/etc/passwd` permissions (must be 644) | permission | warning |
| `/etc/shadow` permissions (must be 640) | permission | warning |
| Orphaned packages (`pacman -Qtd`) | package | info |
| Pacman cache > 3 GB | config | info |
| Broken symlinks in `~/.config`, `~/.local/share` | config | info |
| Stale autostart `.desktop` entries | config | info |

---

## Requirements

- **OS**: Arch Linux (Linux support only; Windows is on the roadmap)
- **Python**: 3.11+
- **Qt**: PySide6 ≥ 6.6 (installed via pip)
- **pacman-contrib**: for `checkupdates` (update checking without root)

```bash
sudo pacman -S pacman-contrib
```

### Sudo for updates and fixes

Applying updates, removing packages, and running health fixes all use `sudo`. The app prompts for your sudo password at startup and holds it in memory for the session (never written to disk). If you have `NOPASSWD` configured for pacman, the prompt is skipped automatically.

Example sudoers line (optional):
```
yourusername ALL=(ALL) NOPASSWD: /usr/bin/pacman
```

---

## Installation

```bash
git clone <repo>
cd archon

python -m venv .venv
.venv/bin/pip install -e .
```

## Running

```bash
# X11
QT_QPA_PLATFORM=xcb .venv/bin/python -m archon

# Wayland
.venv/bin/python -m archon

# Via installed script
.venv/bin/archon
```

---

## Architecture

```
src/archon/
  core/interfaces.py        ABCs + data classes — no platform or UI imports
  platform/__init__.py      Factory: returns Linux implementations
  platform/linux/
    disk.py                 psutil + du (btrfs-aware: subvolume deduplication,
                            background size scans for same-pool mounts)
    packages.py             checkupdates + pacman -Qi for installed package list
                            (install date from /var/lib/pacman/local mtime)
    health.py               permission, package, and config checks
  assets/
    icon.svg                App icon (CPU chip with health pulse line)
  sudo_session.py           Holds sudo credentials for the session
  ui/
    strings.py              All user-visible text — EN / DE / TR
    theme.py                Catppuccin Mocha QSS stylesheet
    main_window.py          QMainWindow, sidebar, QStackedWidget
    auth_dialog.py          Sudo password dialog (shown at startup)
    fix_dialog.py           Live fix/remove output (QProcess + bash -c)
    update_dialog.py        Live update output (QProcess)
    views/
      dashboard_view.py     Live metrics + summary cards
      disk_view.py          Partition donut chart + directory scanner
      packages_view.py      Outdated package list + apply updates
      health_view.py        Issue table + per-row fix button
      apps_view.py          Installed packages list + remove action
```

**DI approach**: constructor injection throughout — no DI framework, no globals.  
`main()` creates platform services and `SudoSession`, passes them to `MainWindow`, which passes them to the views that need them.

**Threading**: slow operations (checkupdates, health scan, du, pacman -Qi) run in `QThread` workers. The UI never blocks. Btrfs subvolume sizes are filled in by per-subvolume background workers after the main scan completes (2-minute timeout per subvolume).

**Signal flow**: `PackagesView.summary_ready` and `HealthView.summary_ready` update dashboard counts. `AppsView.package_removed` triggers a background refresh of both views so dashboard counts stay in sync after a removal.

---

## Multi-language support

All user-visible strings live in `src/archon/ui/strings.py`.  
Three languages are implemented: **EN** (default), **DE**, **TR**.

To switch language before launch:
```python
from archon.ui import strings
strings.set_language("de")   # or "tr"
```

To add a new language, create a new `AppStrings(...)` instance in `strings.py` and register it in `LANGUAGES`.

---

## Roadmap

- [ ] Windows support (`winreg` + `winget` platform implementations)
- [ ] Language selector in the UI (no restart required)
- [ ] System tray icon with background health monitoring
- [ ] Scheduled health scan with desktop notifications
- [ ] Dark/light theme toggle
- [ ] Export health report as PDF / JSON
