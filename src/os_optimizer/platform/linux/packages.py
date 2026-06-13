import subprocess
from os_optimizer.core.interfaces import IPackageManager, PackageUpdate, InstalledApp


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

        apps: list[InstalledApp] = []
        current: dict[str, str] = {}

        for line in result.stdout.splitlines():
            if not line.strip():
                if current.get("Name"):
                    apps.append(InstalledApp(
                        name=current["Name"],
                        version=current.get("Version", ""),
                        size_bytes=_parse_pacman_size(current.get("Installed Size", "0 B")),
                        description=current.get("Description", ""),
                    ))
                current = {}
            elif " : " in line and not line[0].isspace():
                key, _, val = line.partition(" : ")
                current[key.strip()] = val.strip()

        # flush last block
        if current.get("Name"):
            apps.append(InstalledApp(
                name=current["Name"],
                version=current.get("Version", ""),
                size_bytes=_parse_pacman_size(current.get("Installed Size", "0 B")),
                description=current.get("Description", ""),
            ))

        apps.sort(key=lambda a: a.size_bytes, reverse=True)
        return apps
