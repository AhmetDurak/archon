import subprocess
from os_optimizer.core.interfaces import IPackageManager, PackageUpdate


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
