import platform
import math

# ===== Imports (Windows or MacOS) =====
_WINDOWS_IMPORTS_AVAILABLE = False
if platform.system() == 'Windows':
    try:
        import ctypes
        from ctypes import wintypes
        import win32con
        import win32gui
        import win32api
        _WINDOWS_IMPORTS_AVAILABLE = True
    except ImportError:
        pass

_MACOS_IMPORTS_AVAILABLE = False
if platform.system() == 'Darwin':
    try:
        from typing import Optional, Tuple
        from AppKit import NSScreen, NSWorkspace
        from Quartz import CGEventCreateKeyboardEvent, CGEventPost, kCGHIDEventTap
        from Quartz import kCGEventFlagMaskControl, kCGEventFlagMaskCommand
        import time
        
        # Accessibility APIs - Try ApplicationServices First Since Quartz.Accessibility May Not Exist
        try:
            from ApplicationServices import (
                AXUIElementCreateApplication,
                AXUIElementCopyAttributeValue,
                AXUIElementSetAttributeValue,
                AXValueCreate,
                AXValueGetValue,
                kAXValueCGPointType,
                kAXValueCGSizeType,
            )
            try:
                from ApplicationServices import AXUIElementPerformAction
            except ImportError:
                AXUIElementPerformAction = None
        except ImportError:
            # Fallback to Quartz If ApplicationServices Fails
            try:
                from Quartz import Accessibility as AX
                AXUIElementCreateApplication = AX.AXUIElementCreateApplication
                AXUIElementCopyAttributeValue = AX.AXUIElementCopyAttributeValue
                AXUIElementSetAttributeValue = AX.AXUIElementSetAttributeValue
                AXValueCreate = AX.AXValueCreate
                AXValueGetValue = AX.AXValueGetValue
                kAXValueCGPointType = AX.kAXValueCGPointType
                kAXValueCGSizeType = AX.kAXValueCGSizeType
                AXUIElementPerformAction = getattr(AX, "AXUIElementPerformAction", None)
            except ImportError:
                # If Both Fail, We Can't Use macOS Functionality
                raise ImportError("Neither ApplicationServices nor Quartz.Accessibility could be imported")

        # String Constants (Portable Across PyObjC Variants)
        AX_FOCUSED_WINDOW = "AXFocusedWindow"
        AX_WINDOWS       = "AXWindows"
        AX_ROLE          = "AXRole"
        AX_SUBROLE       = "AXSubrole"
        AX_POSITION      = "AXPosition"
        AX_SIZE          = "AXSize"
        AX_RESIZABLE     = "AXResizable"
        AX_FULLSCREEN    = "AXFullScreen"
        AX_MINIMIZED     = "AXMinimized"
        AX_RAISE         = "AXRaise"
        AX_MINIMIZE_BTN  = "AXMinimizeButton"
        AX_PRESS         = "AXPress"
        
        _MACOS_IMPORTS_AVAILABLE = True
    except ImportError as e:
        print(f"macOS imports failed: {e}")
        _MACOS_IMPORTS_AVAILABLE = False


# ===== DWM (via Visible Frame Bounds) =====
if _WINDOWS_IMPORTS_AVAILABLE:
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    _dwmapi = ctypes.windll.dwmapi

    class RECT(ctypes.Structure):
        _fields_ = [('left', ctypes.c_long),
                    ('top', ctypes.c_long),
                    ('right', ctypes.c_long),
                    ('bottom', ctypes.c_long)]


# ===== Determine & Execute OS =====
def execute_os(mac_command, win_command):

    os_name = platform.system()

    if os_name == 'Darwin':
        if _MACOS_IMPORTS_AVAILABLE:
            return mac_command
        else:
            def mac_error_handler():
                return "macOS Functionality Not Available - PyObjC Imports Failed"
            return mac_error_handler
    elif os_name == 'Windows': 
        if _WINDOWS_IMPORTS_AVAILABLE:
            return win_command
        else:
            def win_error_handler():
                return "Windows Functionality Not Available - pywin32 Imports Failed"
            return win_error_handler
    else:
        def unsupported_os_handler():
            return "Unsupported Operating System (Not MacOS or Windows)"
        return unsupported_os_handler


# ===== Helper Functions (MacOS) =====
def _focused_window_for_actions():
    ax_app = _frontmost_ax_app()
    if not ax_app:
        return None
    return _focused_or_standard_window(ax_app)

def _send_keystroke_control_command_f():
    # 'f' Virtual Keycode is 0x03 on ANSI (10.9+ Consistent)
    KEY_F = 0x03
    ev_down = CGEventCreateKeyboardEvent(None, KEY_F, True)
    ev_up   = CGEventCreateKeyboardEvent(None, KEY_F, False)
    for ev in (ev_down, ev_up):
        # Add ⌃⌘ Modifiers
        current = 0
        try:
            # On Some PyObjC Builds, Flags Must Be Set Directly
            ev.setIntegerValueField_(0x12, kCGEventFlagMaskControl | kCGEventFlagMaskCommand)  # kCGEventSourceStateID?
        except Exception:
            pass
        # Standard API
        ev.setFlags_(kCGEventFlagMaskControl | kCGEventFlagMaskCommand)
        CGEventPost(kCGHIDEventTap, ev)

def _ax_copy(el, attr):
    res = AXUIElementCopyAttributeValue(el, attr, None)
    if isinstance(res, tuple) and len(res) == 2:  # (err, value)
        return None if res[0] else res[1]
    return res

def _ax_point(x: float, y: float):
    return AXValueCreate(kAXValueCGPointType, (float(x), float(y)))

def _ax_size(w: float, h: float):
    return AXValueCreate(kAXValueCGSizeType, (float(w), float(h)))

def _ax_get_point(el, attr) -> Optional[Tuple[float, float]]:
    v = _ax_copy(el, attr)
    if v is None: return None
    out = AXValueGetValue(v, kAXValueCGPointType, None)
    if isinstance(out, tuple) and len(out) == 2:
        ok, pt = out
        return tuple(pt) if ok else None
    return tuple(out) if out is not None else None

def _ax_get_size(el, attr) -> Optional[Tuple[float, float]]:
    v = _ax_copy(el, attr)
    if v is None: return None
    out = AXValueGetValue(v, kAXValueCGSizeType, None)
    if isinstance(out, tuple) and len(out) == 2:
        ok, sz = out
        return tuple(sz) if ok else None
    return tuple(out) if out is not None else None

def _ax_bool(el, attr, default=False) -> bool:
    v = _ax_copy(el, attr)
    return bool(v) if isinstance(v, bool) else default

def _union_max_y() -> float:
    return max((s.frame().origin.y + s.frame().size.height) for s in NSScreen.screens())

def _screen_for_point(px: float, py: float):
    for s in NSScreen.screens():
        f = s.frame()
        if (px >= f.origin.x and px <= f.origin.x + f.size.width and
            py >= f.origin.y and py <= f.origin.y + f.size.height):
            return s
    return NSScreen.mainScreen()

def _frontmost_pid() -> Optional[int]:
    app = NSWorkspace.sharedWorkspace().frontmostApplication()
    return int(app.processIdentifier()) if app else None

def _frontmost_ax_app():
    pid = _frontmost_pid()
    return AXUIElementCreateApplication(pid) if pid else None

def _focused_or_standard_window(ax_app):
    win = _ax_copy(ax_app, AX_FOCUSED_WINDOW)
    if win:
        return win
    for w in (_ax_copy(ax_app, AX_WINDOWS) or []):
        if _ax_bool(w, AX_MINIMIZED, False):
            continue
        role = _ax_copy(w, AX_ROLE) or ""
        sub  = _ax_copy(w, AX_SUBROLE) or ""
        if role == "AXWindow" and sub in ("AXStandardWindow", "AXDocumentWindow", ""):
            return w
    ws = _ax_copy(ax_app, AX_WINDOWS) or []
    return ws[0] if ws else None

def _tile(win, x: float, y: float, w: float, h: float) -> bool:
    # Raise (Best Effort)
    if AXUIElementPerformAction is not None:
        try: AXUIElementPerformAction(win, AX_RAISE)
        except Exception: pass
    # Position → Size, Then Reverse If Needed
    try:
        AXUIElementSetAttributeValue(win, AX_POSITION, _ax_point(x, y))
        AXUIElementSetAttributeValue(win, AX_SIZE, _ax_size(w, h))
        return True
    except Exception:
        try:
            AXUIElementSetAttributeValue(win, AX_SIZE, _ax_size(w, h))
            AXUIElementSetAttributeValue(win, AX_POSITION, _ax_point(x, y))
            return True
        except Exception:
            return False

def _target_frame_for_screen_region(screen, region: str) -> Tuple[float, float, float, float]:
    """
    Return (x, y_topLeftAX, w, h) for a given region of the screen's visibleFrame.
    Regions: 'left', 'right', 'top', 'bottom',
             'left_third', 'middle_third', 'right_third'.
    """
    v = screen.visibleFrame()  # Respects Menu Bar & Dock
    vX, vY, vW, vH = float(v.origin.x), float(v.origin.y), float(v.size.width), float(v.size.height)
    axTopLeftY = _union_max_y() - (vY + vH)

    if region in ("left", "right"):
        halfW = float(int(vW // 2))
        if region == "left":
            return (vX, axTopLeftY, halfW, vH)
        else:
            return (vX + halfW, axTopLeftY, vW - halfW, vH)

    elif region in ("top", "bottom"):
        halfH = float(int(vH // 2))
        if region == "top":
            return (vX, axTopLeftY, vW, halfH)
        else:
            return (vX, axTopLeftY + halfH, vW, vH - halfH)

    elif region in ("left_third", "middle_third", "right_third"):
        thirdW = float(int(vW // 3))
        if region == "left_third":
            return (vX, axTopLeftY, thirdW, vH)
        elif region == "middle_third":
            return (vX + thirdW, axTopLeftY, thirdW, vH)
        else:  # right_third
            return (vX + 2*thirdW, axTopLeftY, vW - 2*thirdW, vH)
    
    elif region in ("left_two_third", "right_two_third"):
        thirdW = float(int(vW // 3))
        if region == "left_two_third":
            # start at left edge, take two-thirds
            return (vX, axTopLeftY, 2*thirdW, vH)
        else:  # right_two_third
            # start one-third in, take the rest
            return (vX + thirdW, axTopLeftY, vW - thirdW, vH)

    elif region in (
        "top_left_quarter", "top_right_quarter",
        "bottom_left_quarter", "bottom_right_quarter"
    ):
        halfW = vW // 2
        halfH = vH // 2

        if region == "top_left_quarter":
            return (vX, axTopLeftY, halfW, halfH)

        elif region == "top_right_quarter":
            return (vX + halfW, axTopLeftY, vW - halfW, halfH)

        elif region == "bottom_left_quarter":
            return (vX, axTopLeftY + halfH, halfW, vH - halfH)

        elif region == "bottom_right_quarter":
            return (vX + halfW, axTopLeftY + halfH, vW - halfW, vH - halfH)
            
    elif region == "maximize":
        # Fill entire visible working area (Dock + Menu bar excluded)
        return (vX, axTopLeftY, vW, vH)
    
    else:
        raise ValueError(f"Unknown region: {region}")

def _prep_window(win) -> bool:
    if not win or not _ax_bool(win, AX_RESIZABLE, True):
        return False
    if _ax_bool(win, AX_FULLSCREEN, False):
        try: AXUIElementSetAttributeValue(win, AX_FULLSCREEN, False)
        except Exception: pass
    return True

def _pick_screen_for(win):
    pos = _ax_get_point(win, AX_POSITION) or (0.0, 0.0)
    size = _ax_get_size(win, AX_SIZE) or (0.0, 0.0)
    cx, cy = pos[0] + size[0]/2.0, pos[1] + size[1]/2.0
    return _screen_for_point(cx, cy)

def _do_region(region: str) -> bool:
    ax_app = _frontmost_ax_app()
    if not ax_app:
        return False
    win = _focused_or_standard_window(ax_app)
    if not _prep_window(win):
        return False
    screen = _pick_screen_for(win)
    x, y, w, h = _target_frame_for_screen_region(screen, region)
    return _tile(win, x, y, w, h)


# ===== Helper Functions (Windows) =====
def check_exit_fullscreen_win(hwnd):
    """Restore if Window is Maximized so it can be Resized/Moved."""
    placement = win32gui.GetWindowPlacement(hwnd)
    if placement[1] == win32con.SW_SHOWMAXIMIZED:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

def set_dpi_aware_win():
    """Ensure Coordinates Match Physical Pixels on High-DPI Displays."""
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

def get_effective_dimension_win(hwnd):
    """(L, T, R, B) for the Monitor Containing hwnd, Excluding Taskbar."""
    monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    mi = win32api.GetMonitorInfo(monitor)  # Keys: "Monitor" & "Work"
    return mi['Work']

def get_visible_frame_win(hwnd):
    """
    (L, T, R, B) of the Visible Window Frame (Excludes Drop Shadow).
    Falls back to GetWindowRect if DWM Call Fails.
    """
    rect = RECT()
    hr = _dwmapi.DwmGetWindowAttribute(
        wintypes.HWND(hwnd),
        ctypes.c_uint(DWMWA_EXTENDED_FRAME_BOUNDS),
        ctypes.byref(rect),
        ctypes.sizeof(rect),
    )
    if hr == 0:
        return rect.left, rect.top, rect.right, rect.bottom
    return win32gui.GetWindowRect(hwnd)

def apply_effective_bounds_win(hwnd, target_ltrb):
    """
    Move/Resize so the Visible Frame Aligns with the Target Rect.
    1) Set Outer Bounds Roughly, 2) Measure Insets, 3) Correct.
    """
    L, T, R, B = target_ltrb
    W = max(1, R - L)
    H = max(1, B - T)

    win32gui.SetWindowPos(
        hwnd, 0, L, T, W, H,
        win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
    )

    visL, visT, visR, visB = get_visible_frame_win(hwnd)
    outL, outT, outR, outB = win32gui.GetWindowRect(hwnd)

    inset_left   = visL - outL
    inset_top    = visT - outT
    inset_right  = outR - visR
    inset_bottom = outB - visB

    corrL = L - inset_left
    corrT = T - inset_top
    corrW = W + inset_left + inset_right
    corrH = H + inset_top + inset_bottom

    corrL = int(round(corrL))
    corrT = int(round(corrT))
    corrW = max(1, int(round(corrW)))
    corrH = max(1, int(round(corrH)))

    win32gui.SetWindowPos(
        hwnd, 0, corrL, corrT, corrW, corrH,
        win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
    )

def apply_window_fraction_win(rx, ry, rw, rh):
    """
    Snap the Foreground Window to a Rectangle Expressed as Fractions
    of the Monitor Work Area: (rx, ry, rw, rh) in [0..1].
    """
    set_dpi_aware_win()
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd or not win32gui.IsWindowVisible(hwnd):
        raise RuntimeError("No visible foreground window found.")

    check_exit_fullscreen_win(hwnd)

    waL, waT, waR, waB = get_effective_dimension_win(hwnd)
    waW = waR - waL
    waH = waB - waT

    L = waL + int(math.floor(waW * rx))
    T = waT + int(math.floor(waH * ry))
    R = waL + int(math.floor(waW * (rx + rw)))
    B = waT + int(math.floor(waH * (ry + rh)))

    R = max(R, L + 1)
    B = max(B, T + 1)

    apply_effective_bounds_win(hwnd, (L, T, R, B))


# ===== (Tool 01) Minimise Window =====
def minimise_window():
    run = execute_os(minimise_window_mac, minimise_window_win)
    return run()

def minimise_window_mac():
    """
    Minimize the focused window. Uses AXMinimized; falls back to pressing the
    minimize button (AXPress) if available.
    """
    win = _focused_window_for_actions()
    if not win:
        return False
    # Prefer attribute
    try:
        AXUIElementSetAttributeValue(win, AX_MINIMIZED, True)
        return True
    except Exception:
        pass
    # Fallback: press the minimize button
    try:
        btn = _ax_copy(win, AX_MINIMIZE_BTN)
        if btn and AXUIElementPerformAction is not None:
            AXUIElementPerformAction(btn, AX_PRESS)
            return True
    except Exception:
        pass
    return False

def minimise_window_win():

    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        result = ctypes.windll.user32.ShowWindow(hwnd, 6)

        if result:
            return True
        else:
            print("Failed to Minimise Window")
            return False
 
    except Exception as e:
        print(f"Error Minimising Window: {e}")
        return False


# ===== (Tool 02) Maximise Window =====
def maximise_window():
    run = execute_os(maximise_window_mac, maximise_window_win)
    return run()

def maximise_window_mac():
    return _do_region("maximize")

def maximise_window_win():
    """Put the Foreground Window into the OS 'Maximize/Bordered Fullscreen' State (Bordered, Taskbar Visible)."""
    set_dpi_aware_win()
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd or not win32gui.IsWindowVisible(hwnd):
        raise RuntimeError("No visible foreground window found.")
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)


# ===== (Tool 03) Fullscreen Window =====
def fullscreen_window():
    run = execute_os(fullscreen_window_mac, fullscreen_window_win)
    return run()

def fullscreen_window_mac():
    """
    Enter native macOS fullscreen for the focused window.
    Falls back to sending ⌃⌘F if AXFullScreen isn't available.
    """
    win = _focused_window_for_actions()
    if not win:
        return False
    # Try AX attribute first
    try:
        cur = _ax_copy(win, AX_FULLSCREEN)
        if isinstance(cur, bool) and cur is False:
            AXUIElementSetAttributeValue(win, AX_FULLSCREEN, True)
            return True
        if isinstance(cur, bool) and cur is True:
            return True  # already fullscreen
    except Exception:
        pass
    # Fallback: send the keyboard shortcut
    try:
        _send_keystroke_control_command_f()
        return True
    except Exception:
        return False

def fullscreen_window_win():
    """Put the Foreground Window into the OS 'Maximize/Bordered Fullscreen' State (Bordered, Taskbar Visible)."""
    set_dpi_aware_win()
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd or not win32gui.IsWindowVisible(hwnd):
        raise RuntimeError("No visible foreground window found.")
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)


# ===== (Tool 04) Left 1/2 Screen =====
def left_half_window():
    run = execute_os(left_half_window_mac, left_half_window_win)
    return run()

def left_half_window_mac():   
    return _do_region("left")

def left_half_window_win():
    apply_window_fraction_win(0.0, 0.0, 0.5, 1.0)


# ===== (Tool 05) Right 1/2 Screen =====
def right_half_window():
    run = execute_os(right_half_window_mac, right_half_window_win)
    return run()

def right_half_window_mac():  
    return _do_region("right")

def right_half_window_win():
    apply_window_fraction_win(0.5, 0.0, 0.5, 1.0)


# ===== (Tool 06) Left 1/3 Screen =====
def left_third_window():
    run = execute_os(left_third_window_mac, left_third_window_win)
    return run()

def left_third_window_mac():   
    return _do_region("left_third")

def left_third_window_win():
    apply_window_fraction_win(0.0, 0.0, 1.0/3.0, 1.0)


# ===== (Tool 07) Middle 1/3 Screen =====
def middle_third_window():
    run = execute_os(middle_third_window_mac, middle_third_window_win)
    return run()

def middle_third_window_mac(): 
    return _do_region("middle_third")

def middle_third_window_win():
    apply_window_fraction_win(1.0/3.0, 0.0, 1.0/3.0, 1.0)


# ===== (Tool 08) Right 1/3 Screen =====
def right_third_window():
    run = execute_os(right_third_window_mac, right_third_window_win)
    return run()

def right_third_window_mac():  
    return _do_region("right_third")

def right_third_window_win():
    apply_window_fraction_win(2.0/3.0, 0.0, 1.0/3.0, 1.0)


# ===== (Tool 09) Top 1/2 Screen =====
def top_half_window():
    run = execute_os(top_half_window_mac, top_half_window_win)
    return run()

def top_half_window_mac():    
    return _do_region("top")

def top_half_window_win():
    apply_window_fraction_win(0.0, 0.0, 1.0, 0.5)


# ===== (Tool 10) Bottom 1/2 Screen =====
def bottom_half_window():
    run = execute_os(bottom_half_window_mac, bottom_half_window_win)
    return run()

def bottom_half_window_mac(): 
    return _do_region("bottom")

def bottom_half_window_win():
    apply_window_fraction_win(0.0, 0.5, 1.0, 0.5)


# ===== (Tool 11) Top Left 1/4 Screen =====
def top_left_quadrant_window():
    run = execute_os(top_left_quadrant_window_mac, top_left_quadrant_window_win)
    return run()

def top_left_quadrant_window_mac():
    return _do_region("top_left_quarter")  

def top_left_quadrant_window_win():
    apply_window_fraction_win(0.0, 0.0, 0.5, 0.5)


# ===== (Tool 12) Top Right 1/4 Screen =====
def top_right_quadrant_window():
    run = execute_os(top_right_quadrant_window_mac, top_right_quadrant_window_win)
    return run()

def top_right_quadrant_window_mac():
    return _do_region("top_right_quarter")

def top_right_quadrant_window_win():
    apply_window_fraction_win(0.5, 0.0, 0.5, 0.5)


# ===== (Tool 13) Bottom Left 1/4 Screen =====
def bottom_left_quadrant_window():
    run = execute_os(bottom_left_quadrant_window_mac, bottom_left_quadrant_window_win)
    return run()

def bottom_left_quadrant_window_mac():
    return _do_region("bottom_left_quarter")

def bottom_left_quadrant_window_win():
    apply_window_fraction_win(0.0, 0.5, 0.5, 0.5)


# ===== (Tool 14) Bottom Right 1/4 Screen =====
def bottom_right_quadrant_window():
    run = execute_os(bottom_right_quadrant_window_mac, bottom_right_quadrant_window_win)
    return run()

def bottom_right_quadrant_window_mac():
    return _do_region("bottom_right_quarter")

def bottom_right_quadrant_window_win():
    apply_window_fraction_win(0.5, 0.5, 0.5, 0.5)


# ===== (Tool 15) Left 2/3 Screen =====
def left_two_thirds_window():
    run = execute_os(left_two_thirds_window_mac, left_two_thirds_window_win)
    return run()

def left_two_thirds_window_mac(): 
    return _do_region("left_two_third")

def left_two_thirds_window_win():
    apply_window_fraction_win(0.0, 0.0, 2.0/3.0, 1.0)


# ===== (Tool 16) Right 2/3 Screen =====
def right_two_thirds_window():
    run = execute_os(right_two_thirds_window_mac, right_two_thirds_window_win)
    return run()

def right_two_thirds_window_mac(): 
    return _do_region("right_two_third")

def right_two_thirds_window_win():
    apply_window_fraction_win(1.0/3.0, 0.0, 2.0/3.0, 1.0)
