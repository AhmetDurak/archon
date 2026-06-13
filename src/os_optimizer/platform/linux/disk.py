import subprocess
import psutil
from os_optimizer.core.interfaces import IDiskAnalyzer, DiskPartition, DirSize


class LinuxDiskAnalyzer(IDiskAnalyzer):
    def get_partitions(self) -> list[DiskPartition]:
        # Deduplicate by device: btrfs subvolumes share a device but report
        # identical usage — keep the shortest (most canonical) mountpoint.
        seen: dict[str, DiskPartition] = {}
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
            except PermissionError:
                continue
            entry = DiskPartition(
                device=part.device,
                mountpoint=part.mountpoint,
                total=usage.total,
                used=usage.used,
                free=usage.free,
                percent=usage.percent,
            )
            existing = seen.get(part.device)
            if existing is None or len(part.mountpoint) < len(existing.mountpoint):
                seen[part.device] = entry
        return list(seen.values())

    def get_large_dirs(self, path: str, limit: int = 10) -> list[DirSize]:
        try:
            proc = subprocess.run(
                ["du", "-x", "--max-depth=1", path],
                capture_output=True, text=True, timeout=30
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

        entries = []
        for line in proc.stdout.strip().splitlines():
            parts = line.split("\t", 1)
            if len(parts) == 2:
                try:
                    size_kb = int(parts[0])
                    dir_path = parts[1]
                    if dir_path != path:
                        entries.append(DirSize(path=dir_path, size=size_kb * 1024))
                except ValueError:
                    continue

        entries.sort(key=lambda d: d.size, reverse=True)
        return entries[:limit]
