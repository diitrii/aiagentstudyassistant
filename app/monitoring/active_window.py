import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from typing import Optional

import psutil


user32 = ctypes.WinDLL("user32", use_last_error=True)


@dataclass
class ActiveWindowInfo:
    hwnd: int
    title: str
    process_id: Optional[int]
    process_name: Optional[str]


def get_foreground_window_handle() -> int:
    return user32.GetForegroundWindow()


def get_window_title(hwnd: int) -> str:
    if not hwnd:
        return ""

    length = user32.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value.strip()


def get_window_process_id(hwnd: int) -> Optional[int]:
    if not hwnd:
        return None

    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return int(pid.value) if pid.value else None


def get_process_name(pid: Optional[int]) -> Optional[str]:
    if pid is None:
        return None

    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def get_active_window_info() -> ActiveWindowInfo:
    hwnd = get_foreground_window_handle()
    title = get_window_title(hwnd)
    process_id = get_window_process_id(hwnd)
    process_name = get_process_name(process_id)

    return ActiveWindowInfo(
        hwnd=hwnd,
        title=title,
        process_id=process_id,
        process_name=process_name,
    )