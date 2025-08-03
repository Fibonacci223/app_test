import ctypes

def toggle_desktop_icons(show: bool):
    progman = ctypes.windll.user32.FindWindowW("Progman", None)
    desktop = ctypes.windll.user32.FindWindowExW(progman, 0, "SHELLDLL_DefView", None)
    syslistview32 = ctypes.windll.user32.FindWindowExW(desktop, 0, "SysListView32", None)
    SW_HIDE = 0
    SW_SHOW = 5
    if show:
        ctypes.windll.user32.ShowWindow(syslistview32, SW_SHOW)
    else:
        ctypes.windll.user32.ShowWindow(syslistview32, SW_HIDE)

def toggle_taskbar(show: bool):
    hwnd = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
    SW_HIDE = 0
    SW_SHOW = 5
    if show:
        ctypes.windll.user32.ShowWindow(hwnd, SW_SHOW)
    else:
        ctypes.windll.user32.ShowWindow(hwnd, SW_HIDE)

if __name__ == "__main__":
    toggle_desktop_icons(True)  # Nasconde le icone del desktop
    toggle_taskbar(True)        # Nasconde la barra delle applicazioni
