from __future__ import annotations

import os
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

try:
    import fcntl
except ImportError:  # pragma: no cover - the supported runtime is Unix-like.
    fcntl = None  # type: ignore[assignment]


class LockTimeoutError(TimeoutError):
    """Raised when a project-local lock cannot be acquired in time."""


def _fsync_directory(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)

def atomic_write_bytes(path: Path, content: bytes, *, mode: int | None = None) -> None:
    """Replace *path* atomically with bytes written and synced in the same directory."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing_mode: int | None = None
    if path.exists():
        existing_mode = path.stat().st_mode & 0o777

    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        final_mode = mode if mode is not None else existing_mode
        if final_mode is not None:
            os.chmod(temporary_path, final_mode)
        os.replace(temporary_path, path)
        _fsync_directory(path.parent)
    except BaseException:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass
        raise


def atomic_write_text(
    path: Path,
    content: str,
    *,
    encoding: str = "utf-8",
    mode: int | None = None,
) -> None:
    atomic_write_bytes(Path(path), content.encode(encoding), mode=mode)


def exclusive_create_text(
    path: Path,
    content: str,
    *,
    encoding: str = "utf-8",
    mode: int = 0o644,
) -> None:
    """Create a new file and fail if the target already exists."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(descriptor, "w", encoding=encoding, newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        _fsync_directory(path.parent)
    except BaseException:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise


@contextmanager
def file_lock(lock_path: Path, *, timeout: float = 10.0, poll_interval: float = 0.05) -> Iterator[None]:
    """Hold an advisory, project-local exclusive lock for the duration of the context."""

    if fcntl is None:  # pragma: no cover - fail closed on unsupported platforms.
        raise RuntimeError("project-state locking requires the standard-library fcntl module")

    lock_path = Path(lock_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
    deadline = time.monotonic() + max(timeout, 0.0)
    acquired = False
    try:
        while True:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise LockTimeoutError(f"timed out waiting for lock: {lock_path}")
                time.sleep(poll_interval)

        os.ftruncate(descriptor, 0)
        os.write(descriptor, f"pid={os.getpid()}\n".encode("ascii"))
        os.fsync(descriptor)
        yield
    finally:
        if acquired:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)
