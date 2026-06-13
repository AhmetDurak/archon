import subprocess
from pathlib import Path
import psutil
from archon.core.interfaces import IDiskAnalyzer, DiskPartition, DirSize


def _block_device_of(path: str) -> str | None:
    """Return the block device (e.g. /dev/nvme0n1p2) for the mount that best covers path."""
    best_mnt, best_dev = "", None
    for part in psutil.disk_partitions(all=False):
        if path.startswith(part.mountpoint) and len(part.mountpoint) > len(best_mnt):
            best_mnt = part.mountpoint
            best_dev = part.device
    return best_dev


class LinuxDiskAnalyzer(IDiskAnalyzer):
    def get_partitions(self) -> list[DiskPartition]:
        # Deduplicate by device: btrfs subvolumes share a block device but report
        # identical pool usage — keep the shortest (most canonical) mountpoint.
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

    def get_large_dirs(self, path: str, limit: int = 20) -> list[DirSize]:
        # du -x stays on one filesystem.  For btrfs setups this means separately-
        # mounted subvolumes (e.g. /home) are silently omitted from the output.
        #
        # Strategy:
        #   A) Run du -ax for items on the same filesystem (fast, correct sizes).
        #   B) For every real mount point directly under `path` on a DIFFERENT block
        #      device (e.g. /boot on vfat, /mnt/LocalD on NTFS): supplement with
        #      psutil.disk_usage().used which is accurate for those.
        #   C) For same-block-device subvolumes (btrfs /home, /var/log, …): inject a
        #      0-byte placeholder so they appear in the list.  psutil would return
        #      the pool total for these, inflating sums — so we skip it.
        #      The user can double-click the 0-byte entry to scan the subvolume.
        try:
            proc = subprocess.run(
                ["du", "-ax", "--max-depth=1", path],
                capture_output=True, text=True, timeout=60,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []

        entries: dict[str, int] = {}
        for line in proc.stdout.strip().splitlines():
            parts = line.split("\t", 1)
            if len(parts) == 2:
                try:
                    entries[parts[1]] = int(parts[0]) * 1024
                except ValueError:
                    continue

        # Drop the totals line (the scanned directory itself)
        entries.pop(path, None)
        entries.pop(path.rstrip("/"), None)

        path_norm = path.rstrip("/") or "/"
        scan_block = _block_device_of(path)

        for part in psutil.disk_partitions(all=False):
            mnt = part.mountpoint
            if str(Path(mnt).parent) != path_norm or mnt == path_norm:
                continue
            if scan_block is not None and part.device == scan_block:
                # Same btrfs pool — psutil gives pool total, not subvolume content.
                # Inject a 0-byte placeholder so the entry is at least visible.
                entries.setdefault(mnt, 0)
            else:
                # Genuinely separate partition: psutil gives the correct used bytes.
                try:
                    entries[mnt] = psutil.disk_usage(mnt).used
                except (PermissionError, OSError):
                    pass

        result = sorted(
            [DirSize(path=p, size=s) for p, s in entries.items()],
            key=lambda d: d.size,
            reverse=True,
        )
        return result[:limit]
