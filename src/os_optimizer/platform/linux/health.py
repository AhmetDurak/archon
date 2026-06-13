import os
import shutil
import stat
import subprocess
from pathlib import Path

from os_optimizer.core.interfaces import IHealthChecker, HealthIssue


class LinuxHealthChecker(IHealthChecker):
    def get_issues(self) -> list[HealthIssue]:
        checks = [
            self._check_tmp,
            self._check_home_perms,
            self._check_ssh,
            self._check_gnupg,
            self._check_system_files,
            self._check_orphaned_packages,
            self._check_pacman_cache,
            self._check_broken_symlinks,
            self._check_autostart,
        ]
        issues = []
        for check in checks:
            issues.extend(check())
        return issues

    # ── Permissions ───────────────────────────────────────────────────────

    def _check_tmp(self) -> list[HealthIssue]:
        issues = []
        for path in ["/tmp", "/var/tmp"]:
            try:
                mode = stat.S_IMODE(os.stat(path).st_mode)
                if mode != 0o1777:
                    issues.append(HealthIssue(
                        severity="warning", category="permission", path=path,
                        message=f"Permissions are {oct(mode)}, expected 1777",
                        fix=f"sudo chmod 1777 {path}",
                    ))
            except PermissionError:
                continue
        return issues

    def _check_home_perms(self) -> list[HealthIssue]:
        home = Path.home()
        mode = stat.S_IMODE(home.stat().st_mode)
        if mode & 0o007:
            return [HealthIssue(
                severity="warning", category="permission", path=str(home),
                message=f"Home directory is world-accessible ({oct(mode)})",
                fix=f"chmod 750 {home}",
            )]
        return []

    def _check_ssh(self) -> list[HealthIssue]:
        ssh_dir = Path.home() / ".ssh"
        if not ssh_dir.exists():
            return []
        issues = []

        mode = stat.S_IMODE(ssh_dir.stat().st_mode)
        if mode != 0o700:
            issues.append(HealthIssue(
                severity="error", category="permission", path=str(ssh_dir),
                message=f"~/.ssh permissions are {oct(mode)}, must be 700",
                fix="chmod 700 ~/.ssh",
            ))

        for key_file in ssh_dir.iterdir():
            if key_file.name.startswith("id_") and key_file.suffix not in (".pub",):
                file_mode = stat.S_IMODE(key_file.stat().st_mode)
                if file_mode != 0o600:
                    issues.append(HealthIssue(
                        severity="error", category="permission", path=str(key_file),
                        message=f"SSH private key permissions are {oct(file_mode)}, must be 600",
                        fix=f"chmod 600 {key_file}",
                    ))

        auth_keys = ssh_dir / "authorized_keys"
        if auth_keys.exists():
            mode = stat.S_IMODE(auth_keys.stat().st_mode)
            if mode not in (0o600, 0o640):
                issues.append(HealthIssue(
                    severity="warning", category="permission", path=str(auth_keys),
                    message=f"authorized_keys permissions are {oct(mode)}, recommended 600",
                    fix="chmod 600 ~/.ssh/authorized_keys",
                ))
        return issues

    def _check_gnupg(self) -> list[HealthIssue]:
        gnupg = Path.home() / ".gnupg"
        if not gnupg.exists():
            return []
        mode = stat.S_IMODE(gnupg.stat().st_mode)
        if mode != 0o700:
            return [HealthIssue(
                severity="error", category="permission", path=str(gnupg),
                message=f"~/.gnupg permissions are {oct(mode)}, must be 700",
                fix="chmod 700 ~/.gnupg",
            )]
        return []

    def _check_system_files(self) -> list[HealthIssue]:
        checks = [
            ("/etc/passwd", 0o644),
            ("/etc/shadow", 0o640),
        ]
        issues = []
        for path_str, expected in checks:
            try:
                mode = stat.S_IMODE(os.stat(path_str).st_mode)
                if mode != expected:
                    issues.append(HealthIssue(
                        severity="warning", category="permission", path=path_str,
                        message=f"Permissions are {oct(mode)}, expected {oct(expected)}",
                        fix=f"sudo chmod {oct(expected)[2:]} {path_str}",
                    ))
            except PermissionError:
                continue
        return issues

    # ── Packages ──────────────────────────────────────────────────────────

    def _check_orphaned_packages(self) -> list[HealthIssue]:
        try:
            result = subprocess.run(
                ["pacman", "-Qtd"], capture_output=True, text=True, timeout=15
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

        if result.returncode != 0 or not result.stdout.strip():
            return []

        pkgs = [line.split()[0] for line in result.stdout.strip().splitlines() if line]
        preview = ", ".join(pkgs[:5]) + ("…" if len(pkgs) > 5 else "")
        return [HealthIssue(
            severity="info", category="package", path="pacman",
            message=f"{len(pkgs)} orphaned package(s) installed: {preview}",
            fix="sudo pacman -Rns $(pacman -Qtdq)",
        )]

    def _check_pacman_cache(self) -> list[HealthIssue]:
        cache = Path("/var/cache/pacman/pkg")
        if not cache.exists():
            return []
        try:
            result = subprocess.run(
                ["du", "-s", str(cache)], capture_output=True, text=True, timeout=10
            )
            size_gb = int(result.stdout.split()[0]) / 1024 / 1024
            if size_gb > 3:
                return [HealthIssue(
                    severity="info", category="config", path=str(cache),
                    message=f"Pacman cache is {size_gb:.1f} GB",
                    fix="paccache -rk2  # keeps last 2 versions per package",
                )]
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError, IndexError):
            pass
        return []

    # ── Config / files ────────────────────────────────────────────────────

    def _check_broken_symlinks(self) -> list[HealthIssue]:
        issues = []
        scan_dirs = [
            Path.home() / ".config",
            Path.home() / ".local" / "share",
        ]
        for base in scan_dirs:
            if not base.exists():
                continue
            try:
                for entry in base.iterdir():
                    if entry.is_symlink() and not entry.exists():
                        issues.append(HealthIssue(
                            severity="info", category="config", path=str(entry),
                            message="Broken symlink (target no longer exists)",
                            fix=f"rm {entry}",
                        ))
            except PermissionError:
                continue
        return issues

    def _check_autostart(self) -> list[HealthIssue]:
        autostart = Path.home() / ".config" / "autostart"
        if not autostart.exists():
            return []
        issues = []
        for desktop in autostart.glob("*.desktop"):
            exec_bin = self._desktop_exec(desktop)
            if exec_bin and not Path(exec_bin).is_absolute():
                exec_bin = shutil.which(exec_bin)
            if exec_bin is None:
                issues.append(HealthIssue(
                    severity="info", category="config", path=str(desktop),
                    message="Autostart entry points to a missing or unknown executable",
                    fix=f"rm {desktop}",
                ))
        return issues

    @staticmethod
    def _desktop_exec(desktop: Path) -> str | None:
        try:
            for line in desktop.read_text(errors="replace").splitlines():
                if line.startswith("Exec="):
                    # Strip field codes (%f, %u, …) and take the binary name
                    parts = line[5:].split()
                    if parts:
                        return parts[0]
        except OSError:
            pass
        return None
