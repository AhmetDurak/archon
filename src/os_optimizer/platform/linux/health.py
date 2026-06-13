import os
import stat
from pathlib import Path
from os_optimizer.core.interfaces import IHealthChecker, HealthIssue


class LinuxHealthChecker(IHealthChecker):
    def get_issues(self) -> list[HealthIssue]:
        issues = []
        issues.extend(self._check_tmp())
        issues.extend(self._check_ssh())
        issues.extend(self._check_home_perms())
        return issues

    def _check_tmp(self) -> list[HealthIssue]:
        issues = []
        for path in ["/tmp", "/var/tmp"]:
            try:
                mode = stat.S_IMODE(os.stat(path).st_mode)
                if mode != 0o1777:
                    issues.append(HealthIssue(
                        severity="warning",
                        category="permission",
                        path=path,
                        message=f"{path} permissions are {oct(mode)}, expected 1777",
                        fix=f"sudo chmod 1777 {path}",
                    ))
            except PermissionError:
                continue
        return issues

    def _check_ssh(self) -> list[HealthIssue]:
        issues = []
        ssh_dir = Path.home() / ".ssh"
        if not ssh_dir.exists():
            return []

        mode = stat.S_IMODE(ssh_dir.stat().st_mode)
        if mode != 0o700:
            issues.append(HealthIssue(
                severity="error",
                category="permission",
                path=str(ssh_dir),
                message=f"~/.ssh permissions are {oct(mode)}, must be 700",
                fix="chmod 700 ~/.ssh",
            ))

        for key_file in ssh_dir.iterdir():
            if key_file.suffix in (".pub", ".known_hosts", ".config"):
                continue
            if key_file.name.startswith("id_"):
                file_mode = stat.S_IMODE(key_file.stat().st_mode)
                if file_mode != 0o600:
                    issues.append(HealthIssue(
                        severity="error",
                        category="permission",
                        path=str(key_file),
                        message=f"SSH key permissions are {oct(file_mode)}, must be 600",
                        fix=f"chmod 600 {key_file}",
                    ))
        return issues

    def _check_home_perms(self) -> list[HealthIssue]:
        issues = []
        home = Path.home()
        mode = stat.S_IMODE(home.stat().st_mode)
        # Home dir should not be world-readable/executable
        if mode & 0o007:
            issues.append(HealthIssue(
                severity="warning",
                category="permission",
                path=str(home),
                message=f"Home directory is world-accessible ({oct(mode)})",
                fix=f"chmod 750 {home}",
            ))
        return issues
