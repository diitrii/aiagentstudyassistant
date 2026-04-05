import ctypes
from ctypes import wintypes


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("dwTime", wintypes.DWORD),
    ]


def get_idle_time_seconds() -> float:
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    last_input_info = LASTINPUTINFO()
    last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)

    if not user32.GetLastInputInfo(ctypes.byref(last_input_info)):
        return 0.0

    current_tick = kernel32.GetTickCount()
    elapsed_ms = current_tick - last_input_info.dwTime
    return elapsed_ms / 1000.0