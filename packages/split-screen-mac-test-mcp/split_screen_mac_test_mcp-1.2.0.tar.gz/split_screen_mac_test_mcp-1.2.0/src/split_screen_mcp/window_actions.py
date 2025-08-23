#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, Tuple
import platform
import sys

# Conditional imports for macOS-specific functionality
_IS_MACOS = platform.system() == 'Darwin'
_IMPORTS_AVAILABLE = False

if _IS_MACOS:
    try:
        from AppKit import NSScreen, NSWorkspace
        from Quartz import CGEventCreateKeyboardEvent, CGEventPost, kCGHIDEventTap
        from Quartz import kCGEventFlagMaskControl, kCGEventFlagMaskCommand
        import time
        _IMPORTS_AVAILABLE = True
    except ImportError:
        pass

# Accessibility APIs (prefer Quartz.Accessibility; else ApplicationServices)
if _IMPORTS_AVAILABLE:
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
    except Exception:
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
        except Exception:
            AXUIElementPerformAction = None

# String constants (portable across PyObjC variants)
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

def _check_macos_available():
    """Check if macOS functionality is available"""
    if not _IS_MACOS:
        raise RuntimeError("This functionality is only available on macOS")
    if not _IMPORTS_AVAILABLE:
        raise RuntimeError("PyObjC frameworks not available. Install with: pip install 'split-screen-mac-test-mcp[macos]' or ensure PyObjC is installed")

# ---------- Minimal helpers ----------

def _focused_window_for_actions():
    _check_macos_available()
    ax_app = _frontmost_ax_app()
    if not ax_app:
        return None
    return _focused_or_standard_window(ax_app)

def _send_keystroke_control_command_f():
    _check_macos_available()
    # 'f' virtual keycode is 0x03 on ANSI (10.9+ consistent)
    KEY_F = 0x03
    ev_down = CGEventCreateKeyboardEvent(None, KEY_F, True)
    ev_up   = CGEventCreateKeyboardEvent(None, KEY_F, False)
    for ev in (ev_down, ev_up):
        # add ⌃⌘ modifiers
        current = 0
        try:
            # On some PyObjC builds, flags must be set directly:
            ev.setIntegerValueField_(0x12, kCGEventFlagMaskControl | kCGEventFlagMaskCommand)  # kCGEventSourceStateID?
        except Exception:
            pass
        # Standard API:
        ev.setFlags_(kCGEventFlagMaskControl | kCGEventFlagMaskCommand)
        CGEventPost(kCGHIDEventTap, ev)

def _ax_copy(el, attr):
    _check_macos_available()
    res = AXUIElementCopyAttributeValue(el, attr, None)
    if isinstance(res, tuple) and len(res) == 2:  # (err, value)
        return None if res[0] else res[1]
    return res

def _ax_point(x: float, y: float):
    _check_macos_available()
    return AXValueCreate(kAXValueCGPointType, (float(x), float(y)))

def _ax_size(w: float, h: float):
    _check_macos_available()
    return AXValueCreate(kAXValueCGSizeType, (float(w), float(h)))

def _ax_get_point(el, attr) -> Optional[Tuple[float, float]]:
    _check_macos_available()
    v = _ax_copy(el, attr)
    if v is None: return None
    out = AXValueGetValue(v, kAXValueCGPointType, None)
    if isinstance(out, tuple) and len(out) == 2:
        ok, pt = out
        return tuple(pt) if ok else None
    return tuple(out) if out is not None else None

def _ax_get_size(el, attr) -> Optional[Tuple[float, float]]:
    _check_macos_available()
    v = _ax_copy(el, attr)
    if v is None: return None
    out = AXValueGetValue(v, kAXValueCGSizeType, None)
    if isinstance(out, tuple) and len(out) == 2:
        ok, sz = out
        return tuple(sz) if ok else None
    return tuple(out) if out is not None else None

def _ax_bool(el, attr, default=False) -> bool:
    _check_macos_available()
    v = _ax_copy(el, attr)
    return bool(v) if isinstance(v, bool) else default

def _union_max_y() -> float:
    _check_macos_available()
    return max((s.frame().origin.y + s.frame().size.height) for s in NSScreen.screens())

def _screen_for_point(px: float, py: float):
    _check_macos_available()
    for s in NSScreen.screens():
        f = s.frame()
        if (px >= f.origin.x and px <= f.origin.x + f.size.width and
            py >= f.origin.y and py <= f.origin.y + f.size.height):
            return s
    return NSScreen.mainScreen()

def _frontmost_pid() -> Optional[int]:
    _check_macos_available()
    app = NSWorkspace.sharedWorkspace().frontmostApplication()
    return int(app.processIdentifier()) if app else None

def _frontmost_ax_app():
    _check_macos_available()
    pid = _frontmost_pid()
    return AXUIElementCreateApplication(pid) if pid else None

def _focused_or_standard_window(ax_app):
    _check_macos_available()
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
    _check_macos_available()
    # raise (best effort)
    if AXUIElementPerformAction is not None:
        try: AXUIElementPerformAction(win, AX_RAISE)
        except Exception: pass
    # position → size, then reverse if needed
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
    _check_macos_available()
    """
    Return (x, y_topLeftAX, w, h) for a given region of the screen's visibleFrame.
    Regions: 'left', 'right', 'top', 'bottom',
             'left_third', 'middle_third', 'right_third'.
    """
    v = screen.visibleFrame()  # respects menu bar & Dock
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

# ---------- Actions ----------

def _prep_window(win) -> bool:
    _check_macos_available()
    if not win or not _ax_bool(win, AX_RESIZABLE, True):
        return False
    if _ax_bool(win, AX_FULLSCREEN, False):
        try: AXUIElementSetAttributeValue(win, AX_FULLSCREEN, False)
        except Exception: pass
    return True

def _pick_screen_for(win):
    _check_macos_available()
    pos = _ax_get_point(win, AX_POSITION) or (0.0, 0.0)
    size = _ax_get_size(win, AX_SIZE) or (0.0, 0.0)
    cx, cy = pos[0] + size[0]/2.0, pos[1] + size[1]/2.0
    return _screen_for_point(cx, cy)

def _do_region(region: str) -> bool:
    _check_macos_available()
    ax_app = _frontmost_ax_app()
    if not ax_app:
        return False
    win = _focused_or_standard_window(ax_app)
    if not _prep_window(win):
        return False
    screen = _pick_screen_for(win)
    x, y, w, h = _target_frame_for_screen_region(screen, region)
    return _tile(win, x, y, w, h)

def fullscreen_active_window() -> bool:
    """
    Enter native macOS fullscreen for the focused window.
    Falls back to sending ⌃⌘F if AXFullScreen isn't available.
    """
    try:
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
    except RuntimeError as e:
        print(f"Error: {e}")
        return False

def minimize_active_window() -> bool:
    """
    Minimize the focused window. Uses AXMinimized; falls back to pressing the
    minimize button (AXPress) if available.
    """
    try:
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
    except RuntimeError as e:
        print(f"Error: {e}")
        return False

def move_active_window_left_half() -> bool:   
    try:
        return _do_region("left")
    except RuntimeError as e:
        print(f"Error: {e}")
        return False

def move_active_window_right_half() -> bool:  
    try:
        return _do_region("right")
    except RuntimeError as e:
        print(f"Error: {e}")
        return False

def move_active_window_top_half() -> bool:    
    try:
        return _do_region("top")
    except RuntimeError as e:
        print(f"Error: {e}")
        return False

def move_active_window_bottom_half() -> bool: 
    try:
        return _do_region("bottom")
    except RuntimeError as e:
        print(f"Error: {e}")
        return False

def move_active_window_left_third() -> bool:   
    try:
        return _do_region("left_third")
    except RuntimeError as e:
        print(f"Error: {e}")
        return False

def move_active_window_middle_third() -> bool: 
    try:
        return _do_region("middle_third")
    except RuntimeError as e:
        print(f"Error: {e}")
        return False

def move_active_window_right_third() -> bool:  
    try:
        return _do_region("right_third")
    except RuntimeError as e:
        print(f"Error: {e}")
        return False

def move_active_window_left_two_third() -> bool: 
    try:
        return _do_region("left_two_third")
    except RuntimeError as e:
        print(f"Error: {e}")
        return False

def move_active_window_right_two_third() -> bool: 
    try:
        return _do_region("right_two_third")
    except RuntimeError as e:
        print(f"Error: {e}")
        return False

def move_active_window_top_left_quarter() -> bool:
    try:
        return _do_region("top_left_quarter")   
    except RuntimeError as e:
        print(f"Error: {e}")
        return False

def move_active_window_top_right_quarter() -> bool:
    try:
        return _do_region("top_right_quarter")
    except RuntimeError as e:
        print(f"Error: {e}")
        return False

def move_active_window_bottom_left_quarter() -> bool:
    try:
        return _do_region("bottom_left_quarter")
    except RuntimeError as e:
        print(f"Error: {e}")
        return False

def move_active_window_bottom_right_quarter() -> bool:
    try:
        return _do_region("bottom_right_quarter")
    except RuntimeError as e:
        print(f"Error: {e}")
        return False

def move_active_window_maximize() -> bool:
    try:
        return _do_region("maximize")
    except RuntimeError as e:
        print(f"Error: {e}")
        return False
