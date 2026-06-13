from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DiskPartition:
    device: str
    mountpoint: str
    total: int
    used: int
    free: int
    percent: float


@dataclass
class DirSize:
    path: str
    size: int


@dataclass
class PackageUpdate:
    name: str
    current: str
    available: str


@dataclass
class InstalledApp:
    name: str
    version: str
    size_bytes: int
    description: str


@dataclass
class HealthIssue:
    severity: str       # "error" | "warning" | "info"
    category: str       # "permission" | "config" | "package"
    path: str
    message: str
    fix: str | None     # human-readable fix suggestion


class IDiskAnalyzer(ABC):
    @abstractmethod
    def get_partitions(self) -> list[DiskPartition]: ...

    @abstractmethod
    def get_large_dirs(self, path: str, limit: int = 10) -> list[DirSize]: ...


class IPackageManager(ABC):
    @abstractmethod
    def get_outdated_packages(self) -> list[PackageUpdate]: ...

    @abstractmethod
    def get_update_command(self) -> list[str]:
        """Returns the shell command to run a full system update."""
        ...

    @abstractmethod
    def get_installed_packages(self) -> list[InstalledApp]: ...


class IHealthChecker(ABC):
    @abstractmethod
    def get_issues(self) -> list[HealthIssue]: ...
