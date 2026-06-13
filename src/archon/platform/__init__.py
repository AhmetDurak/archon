import sys
from archon.core.interfaces import IDiskAnalyzer, IPackageManager, IHealthChecker


def get_disk_analyzer() -> IDiskAnalyzer:
    if sys.platform.startswith("linux"):
        from archon.platform.linux.disk import LinuxDiskAnalyzer
        return LinuxDiskAnalyzer()
    raise NotImplementedError(f"Platform not supported: {sys.platform}")


def get_package_manager() -> IPackageManager:
    if sys.platform.startswith("linux"):
        from archon.platform.linux.packages import PacmanPackageManager
        return PacmanPackageManager()
    raise NotImplementedError(f"Platform not supported: {sys.platform}")


def get_health_checker() -> IHealthChecker:
    if sys.platform.startswith("linux"):
        from archon.platform.linux.health import LinuxHealthChecker
        return LinuxHealthChecker()
    raise NotImplementedError(f"Platform not supported: {sys.platform}")
