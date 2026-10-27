"""Windows Job Object ownership, assigned before a suspended child starts."""

import ctypes
from ctypes import wintypes


class _BasicLimit(ctypes.Structure):
    _fields_ = [("ProcessTime", ctypes.c_longlong), ("JobTime", ctypes.c_longlong),
                ("Flags", wintypes.DWORD), ("MinWorkingSet", ctypes.c_size_t),
                ("MaxWorkingSet", ctypes.c_size_t), ("ActiveProcesses", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t), ("Priority", wintypes.DWORD), ("Scheduling", wintypes.DWORD)]


class _ExtendedLimit(ctypes.Structure):
    _fields_ = [("Basic", _BasicLimit), ("IOCounters", ctypes.c_ulonglong * 6),
                ("ProcessMemory", ctypes.c_size_t), ("JobMemory", ctypes.c_size_t),
                ("PeakProcessMemory", ctypes.c_size_t), ("PeakJobMemory", ctypes.c_size_t)]


class _ThreadEntry(ctypes.Structure):
    _fields_ = [("Size", wintypes.DWORD), ("Usage", wintypes.DWORD), ("ID", wintypes.DWORD),
                ("Owner", wintypes.DWORD), ("BasePriority", wintypes.LONG),
                ("DeltaPriority", wintypes.LONG), ("Flags", wintypes.DWORD)]


class WindowsJob:
    def __init__(self):
        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "CreateJobObjectW": ([ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
            "SetInformationJobObject": ([wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD], wintypes.BOOL),
            "AssignProcessToJobObject": ([wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
            "TerminateJobObject": ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
            "CloseHandle": ([wintypes.HANDLE], wintypes.BOOL),
            "CreateToolhelp32Snapshot": ([wintypes.DWORD, wintypes.DWORD], wintypes.HANDLE),
            "Thread32First": ([wintypes.HANDLE, ctypes.POINTER(_ThreadEntry)], wintypes.BOOL),
            "Thread32Next": ([wintypes.HANDLE, ctypes.POINTER(_ThreadEntry)], wintypes.BOOL),
            "OpenThread": ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
            "ResumeThread": ([wintypes.HANDLE], wintypes.DWORD),
        }
        for name, (args, result) in signatures.items():
            function = getattr(self.api, name)
            function.argtypes, function.restype = args, result
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise OSError("job_creation_failed")
        limits = _ExtendedLimit()
        limits.Basic.Flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.api.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            self.close()
            raise OSError("job_configuration_failed")

    def assign_and_resume(self, process):
        if not self.api.AssignProcessToJobObject(self.handle, int(process._handle)):
            raise OSError("job_assignment_failed")
        # Popen closes the primary thread handle. Find that still-suspended
        # thread using documented Toolhelp APIs, then resume only our PID.
        snapshot = self.api.CreateToolhelp32Snapshot(4, 0)
        if snapshot in (None, ctypes.c_void_p(-1).value):
            raise OSError("thread_snapshot_failed")
        try:
            entry = _ThreadEntry()
            entry.Size = ctypes.sizeof(entry)
            found = self.api.Thread32First(snapshot, ctypes.byref(entry))
            while found:
                if entry.Owner == process.pid:
                    thread = self.api.OpenThread(2, False, entry.ID)
                    if not thread:
                        raise OSError("thread_open_failed")
                    try:
                        if self.api.ResumeThread(thread) == 0xFFFFFFFF:
                            raise OSError("thread_resume_failed")
                    finally:
                        self.api.CloseHandle(thread)
                    return
                found = self.api.Thread32Next(snapshot, ctypes.byref(entry))
            raise OSError("owned_thread_missing")
        finally:
            self.api.CloseHandle(snapshot)

    def terminate(self) -> bool:
        return bool(self.api.TerminateJobObject(self.handle, 1))

    def close(self):
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None
