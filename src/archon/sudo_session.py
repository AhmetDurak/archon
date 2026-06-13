import subprocess
from dataclasses import dataclass


@dataclass
class SudoSession:
    """Holds sudo credentials for the lifetime of the app session."""
    password: str | None  # None means NOPASSWD — no injection needed


def check_passwordless() -> bool:
    """Returns True if sudo works without a password right now."""
    result = subprocess.run(["sudo", "-n", "true"], capture_output=True)
    return result.returncode == 0


def validate_password(password: str) -> bool:
    """Validates a sudo password without running anything harmful."""
    try:
        result = subprocess.run(
            ["sudo", "-S", "-v"],
            input=f"{password}\n",
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
