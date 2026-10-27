"""Launch owned subprocesses with bounded capture and a minimal environment."""

from __future__ import annotations

import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time

from .tool_execution_paths import ExecutionPaths, checked_path


CAPTURE_LIMIT = 1024 * 1024


def child_environment(paths: ExecutionPaths, model_root: Path | None) -> dict[str, str]:
    env = {key: os.environ[key] for key in ("SystemRoot", "WINDIR", "SYSTEMROOT") if key in os.environ}
    directories = []
    for value in [str(Path(sys.executable).parent), *os.environ.get("PATH", "").split(os.pathsep)]:
        try:
            directory = checked_path(value.strip('"'))
            if directory.is_dir() and str(directory) not in directories:
                directories.append(str(directory))
        except ValueError:
            continue
    env.update({"PATH": os.pathsep.join(directories), "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
                "PYTHONDONTWRITEBYTECODE": "1", "AIRMOSAIC_LOCAL_WORKSPACE": str(paths.workspace),
                "UNIT_PRICE_OUT_DIR": str(paths.output)})
    for name in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "TMPDIR"):
        env[name] = str(paths.temp)
    if model_root is not None:
        env["GCAM_RELEASE_DIR"] = str(model_root)
        env["JAVA_TOOL_OPTIONS"] = f'-Duser.home="{paths.temp}" -Djava.io.tmpdir="{paths.temp}"'
    return env


def stop_tree(process: subprocess.Popen, job=None) -> bool:
    try:
        if job is not None:
            success = job.terminate()
        elif os.name == "nt":
            system = os.environ.get("SystemRoot", os.environ.get("SYSTEMROOT", ""))
            taskkill = checked_path(str(Path(system) / "System32" / "taskkill.exe"))
            result = subprocess.run([str(taskkill), "/PID", str(process.pid), "/T", "/F"],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                    timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
            success = result.returncode == 0
        else:
            os.killpg(process.pid, signal.SIGKILL)
            success = True
        process.wait(timeout=10)
        return success
    except (OSError, ValueError, subprocess.SubprocessError):
        try:
            process.kill()
            process.wait(timeout=5)
        except (OSError, subprocess.SubprocessError):
            pass
        return False


def execute(argv: list[str], cwd: Path, env: dict[str, str], timeout: int, capture: bool) -> tuple:
    options = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW | 4}
               if os.name == "nt" else {"start_new_session": True})
    job, process = None, None
    if os.name == "nt":
        from .tool_windows_job import WindowsJob
        job = WindowsJob()
    try:
        process = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, shell=False, **options)
        if job is not None:
            job.assign_and_resume(process)
        return _monitor(process, timeout, capture, job)
    except BaseException:
        if process is not None:
            stop_tree(process, job)
        raise
    finally:
        if job is not None:
            job.close()
        elif process is not None:
            # POSIX session ownership survives the direct parent's exit.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def _monitor(process, timeout, capture, job):
    chunks: list[bytes] = []
    exceeded = threading.Event()
    def read():
        count = 0
        try:
            while True:
                chunk = process.stdout.read(4096)
                if not chunk:
                    break
                count += len(chunk)
                if count > CAPTURE_LIMIT:
                    exceeded.set()
                    break
                chunks.append(chunk)
        except (OSError, ValueError):
            exceeded.set()
    reader = threading.Thread(target=read, daemon=True) if capture else None
    if reader:
        reader.start()
    deadline = time.monotonic() + timeout
    reason, cleanup = None, None
    while process.poll() is None:
        if exceeded.is_set() or time.monotonic() >= deadline:
            reason = "output_limit" if exceeded.is_set() else "timeout"
            cleanup = stop_tree(process, job)
            break
        time.sleep(0.02)
    if reader:
        reader.join(timeout=1)
        if reader.is_alive():
            reason, cleanup = "output_stream_open", stop_tree(process, job)
            reader.join(timeout=2)
        elif exceeded.is_set():
            reason = "output_limit"
    if process.stdout and not (reader and reader.is_alive()):
        process.stdout.close()
    return process.returncode, reason, cleanup, b"".join(chunks) if reason is None else b""
