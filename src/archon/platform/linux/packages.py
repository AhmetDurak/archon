import subprocess
from datetime import datetime
from pathlib import Path
from archon.core.interfaces import IPackageManager, PackageUpdate, InstalledApp

_PACMAN_LOCAL = Path("/var/lib/pacman/local")


def _install_date_map() -> dict[str, datetime]:
    """Read mtime of each package dir in the pacman local DB in one pass."""
    result: dict[str, datetime] = {}
    if not _PACMAN_LOCAL.exists():
        return result
    for entry in _PACMAN_LOCAL.iterdir():
        if entry.is_dir() and entry.name != "ALPM_DB_VERSION":
            result[entry.name] = datetime.fromtimestamp(entry.stat().st_mtime)
    return result


def _parse_pacman_size(s: str) -> int:
    """'1.23 MiB' → bytes."""
    units = {"B": 1, "KiB": 1024, "MiB": 1024**2, "GiB": 1024**3, "TiB": 1024**4}
    parts = s.split()
    if len(parts) != 2:
        return 0
    try:
        return int(float(parts[0]) * units.get(parts[1], 1))
    except ValueError:
        return 0


class PacmanPackageManager(IPackageManager):
    def get_outdated_packages(self) -> list[PackageUpdate]:
        try:
            result = subprocess.run(
                ["checkupdates"], capture_output=True, text=True, timeout=60
            )
        except FileNotFoundError:
            return []
        except subprocess.TimeoutExpired:
            return []

        packages = []
        for line in result.stdout.strip().splitlines():
            parts = line.split()
            # "name current -> available"
            if len(parts) == 4 and parts[2] == "->":
                packages.append(PackageUpdate(
                    name=parts[0], current=parts[1], available=parts[3]
                ))
        return packages

    def get_update_command(self) -> list[str]:
        return ["sudo", "pacman", "-Syu", "--noconfirm"]

    def get_installed_packages(self) -> list[InstalledApp]:
        try:
            result = subprocess.run(
                ["pacman", "-Qi"], capture_output=True, text=True, timeout=30
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

        dates = _install_date_map()

        apps: list[InstalledApp] = []
        current: dict[str, str] = {}

        def _flush(block: dict[str, str]) -> None:
            name = block.get("Name", "")
            version = block.get("Version", "")
            install_date = dates.get(f"{name}-{version}")
            apps.append(InstalledApp(
                name=name,
                version=version,
                size_bytes=_parse_pacman_size(block.get("Installed Size", "0 B")),
                description=block.get("Description", ""),
                install_date=install_date,
            ))

        for line in result.stdout.splitlines():
            if not line.strip():
                if current.get("Name"):
                    _flush(current)
                current = {}
            elif " : " in line and not line[0].isspace():
                key, _, val = line.partition(" : ")
                current[key.strip()] = val.strip()

        if current.get("Name"):
            _flush(current)

        apps.sort(key=lambda a: a.size_bytes, reverse=True)
        return apps
