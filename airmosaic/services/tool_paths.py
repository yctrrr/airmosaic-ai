"""Conservative local-path preflight for read-only discovery probes."""

from __future__ import annotations

import os
from pathlib import Path
import stat


def _network_drive(path: Path) -> bool:
    if os.name == "nt":
        import ctypes

        # GetDriveType queries the volume category without opening a remote file.
        get_drive_type = ctypes.windll.kernel32.GetDriveTypeW
        get_drive_type.argtypes = [ctypes.c_wchar_p]
        get_drive_type.restype = ctypes.c_uint
        drive_type = get_drive_type(path.anchor)
        return drive_type in {0, 1, 4}
    mount_table = Path("/proc/self/mountinfo")
    if mount_table.is_file():
        # Linux's kernel-provided mount table; no mount-point traversal.
        for line in mount_table.read_text(encoding="utf-8").splitlines():
            left, separator, right = line.partition(" - ")
            fields = left.split()
            if not separator or len(fields) < 5:
                continue
            mount = Path(fields[4].replace("\\040", " ").replace("\\134", "\\"))
            filesystem = right.split()[0]
            if path.is_relative_to(mount) and (
                filesystem in {"nfs", "nfs4", "cifs", "smb3", "9p", "afs", "ceph"}
                or filesystem.startswith("fuse")
            ):
                return True
    return False


def local_path(value: str) -> Path:
    """Reject remote drives and all link/reparse ancestors before following them.

    This deliberately treats linked locations as unverified, even if they might
    resolve locally. It is a discovery preflight, not a filesystem sandbox.
    """
    if value.startswith(("\\\\", "//")) or not Path(value).is_absolute() or ".." in Path(value).parts:
        raise ValueError("A local absolute path is required.")
    path = Path(os.path.abspath(value))
    if _network_drive(path):
        raise ValueError("Remote or unknown drive type.")
    for ancestor in reversed((path, *path.parents)):
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            break
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Linked or reparse locations require manual verification.")
    return path


def executable_available(name: str) -> bool:
    """Search local PATH entries only, without implicit current-directory search."""
    suffixes = (".exe", ".com", ".bat", ".cmd") if os.name == "nt" else ("",)
    for raw in os.environ.get("PATH", "").split(os.pathsep):
        if not raw.strip():
            continue
        try:
            directory = local_path(raw.strip('"'))
            for suffix in suffixes:
                candidate = local_path(str(directory / (name + suffix)))
                if candidate.is_file() and os.access(candidate, os.X_OK):
                    return True
        except (OSError, ValueError, RuntimeError):
            continue
    return False
