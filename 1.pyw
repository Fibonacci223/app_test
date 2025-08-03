import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

def toggle_desktop_icons(show: bool):
    progman = user32.FindWindowW("Progman", None)
    desktop = user32.FindWindowExW(progman, 0, "SHELLDLL_DefView", None)
    syslistview32 = user32.FindWindowExW(desktop, 0, "SysListView32", None)
    SW_HIDE = 0
    SW_SHOW = 5
    if syslistview32:
        user32.ShowWindow(syslistview32, SW_SHOW if show else SW_HIDE)

def toggle_taskbar(show: bool):
    hwnd = user32.FindWindowW("Shell_TrayWnd", None)
    SW_HIDE = 0
    SW_SHOW = 5
    if hwnd:
        user32.ShowWindow(hwnd, SW_SHOW if show else SW_HIDE)

def close_all_windows():
    def enum_callback(hwnd, lParam):
        # Filtra solo finestre visibili, non di sistema, con titolo
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                title = buffer.value
                if title and "Program Manager" not in title:
                    user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(EnumWindowsProc(enum_callback), 0)

if __name__ == "__main__":
    toggle_desktop_icons(False)  # Nasconde icone
    toggle_taskbar(False)        # Nasconde taskbar
    close_all_windows()          # Chiude tutte le finestre aperte
