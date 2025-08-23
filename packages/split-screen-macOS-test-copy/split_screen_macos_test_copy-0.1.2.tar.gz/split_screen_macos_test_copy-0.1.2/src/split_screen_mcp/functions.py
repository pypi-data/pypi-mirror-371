#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, Tuple
from AppKit import NSScreen, NSWorkspace

# Use CoreGraphics symbols from the CG submodule
from Quartz.CoreGraphics import (
    CGEventCreateKeyboardEvent,
    CGEventPost,
    kCGHIDEventTap,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskCommand,
)

# Accessibility APIs - import the package, then reference attributes via Quartz.<name>
import Quartz

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

# ---------- Minimal helpers ----------

def _focused_window_for_actions():
    ax_app = _frontmost_ax_app()
    if not ax_app:
        return None
    return _focused_or_standard_window(ax_app)

# 1) Fix _ax_copy to use Quartz.<symbol>
def _ax_copy(el, attr):
    res = Quartz.AXUIElementCopyAttributeValue(el, attr, None)
    if isinstance(res, tuple) and len(res) == 2:
        val, err = res
        return None if err else val
    return res

# 2) (Optional) Add and call this at the start of actions
def _ensure_accessibility_or_raise():
    opts = {Quartz.kAXTrustedCheckOptionPrompt: True}
    if not Quartz.AXIsProcessTrustedWithOptions(opts):
        raise PermissionError(
            "Accessibility permission not granted. "
            "Enable it in System Settings → Privacy & Security → Accessibility "
            "for your terminal/IDE and try again."
        )

# Example: call once on action entry
def _do_region(region: str) -> bool:
    _ensure_accessibility_or_raise()  # <-- add this
    ax_app = _frontmost_ax_app()
    if not ax_app:
        return False
    win = _focused_or_standard_window(ax_app)
    if not _prep_window(win):
        return False
    screen = _pick_screen_for(win)
    x, y, w, h = _target_frame_for_screen_region(screen, region)
    return _tile(win, x, y, w, h)

# 3) Simplify keystroke fallback
def _send_keystroke_control_command_f():
    KEY_F = 0x03
    ev_down = CGEventCreateKeyboardEvent(None, KEY_F, True)
    ev_up   = CGEventCreateKeyboardEvent(None, KEY_F, False)
    for ev in (ev_down, ev_up):
        ev.setFlags_(kCGEventFlagMaskControl | kCGEventFlagMaskCommand)
        CGEventPost(kCGHIDEventTap, ev)

def _ax_point(x: float, y: float):
    return Quartz.AXValueCreate(Quartz.kAXValueCGPointType, (float(x), float(y)))

def _ax_size(w: float, h: float):
    return Quartz.AXValueCreate(Quartz.kAXValueCGSizeType, (float(w), float(h)))

def _ax_get_point(el, attr) -> Optional[Tuple[float, float]]:
    v = _ax_copy(el, attr)
    if v is None: return None
    out = Quartz.AXValueGetValue(v, Quartz.kAXValueCGPointType, None)
    if isinstance(out, tuple) and len(out) == 2:
        ok, pt = out
        return tuple(pt) if ok else None
    return tuple(out) if out is not None else None

def _ax_get_size(el, attr) -> Optional[Tuple[float, float]]:
    v = _ax_copy(el, attr)
    if v is None: return None
    out = Quartz.AXValueGetValue(v, Quartz.kAXValueCGSizeType, None)
    if isinstance(out, tuple) and len(out) == 2:
        ok, sz = out
        return tuple(sz) if ok else None
    return tuple(out) if out is not None else None

def _ax_bool(el, attr, default=False) -> bool:
    v = _ax_copy(el, attr)
    return bool(v) if isinstance(v, bool) else default

def _union_max_y() -> float:
    # Now called only when needed, not at module import
    return max((s.frame().origin.y + s.frame().size.height) for s in NSScreen.screens())

def _screen_for_point(px: float, py: float):
    # Now called only when needed, not at module import
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
    return Quartz.AXUIElementCreateApplication(pid) if pid else None

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
    # raise (best effort)
    if getattr(Quartz, "AXUIElementPerformAction", None) is not None:
        try:
            Quartz.AXUIElementPerformAction(win, AX_RAISE)
        except Exception:
            pass
    # position → size, then reverse if needed
    try:
        Quartz.AXUIElementSetAttributeValue(win, AX_POSITION, _ax_point(x, y))
        Quartz.AXUIElementSetAttributeValue(win, AX_SIZE, _ax_size(w, h))
        return True
    except Exception:
        try:
            Quartz.AXUIElementSetAttributeValue(win, AX_SIZE, _ax_size(w, h))
            Quartz.AXUIElementSetAttributeValue(win, AX_POSITION, _ax_point(x, y))
            return True
        except Exception:
            return False

def _target_frame_for_screen_region(screen, region: str) -> Tuple[float, float, float, float]:
    """
    Return (x, y_topLeftAX, w, h) for a given region of the screen's visibleFrame.
    Regions: 'left', 'right', 'top', 'bottom',
             'left_third', 'middle_third', 'right_third',
             'left_two_third', 'right_two_third',
             'top_left_quarter', 'top_right_quarter',
             'bottom_left_quarter', 'bottom_right_quarter',
             'maximize'.
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
    if not win or not _ax_bool(win, AX_RESIZABLE, True):
        return False
    if _ax_bool(win, AX_FULLSCREEN, False):
        try:
            Quartz.AXUIElementSetAttributeValue(win, AX_FULLSCREEN, False)
        except Exception:
            pass
    return True

def _pick_screen_for(win):
    pos = _ax_get_point(win, AX_POSITION) or (0.0, 0.0)
    size = _ax_get_size(win, AX_SIZE) or (0.0, 0.0)
    cx, cy = pos[0] + size[0]/2.0, pos[1] + size[1]/2.0
    return _screen_for_point(cx, cy)

def fullscreen_active_window() -> bool:
    """
    Enter native macOS fullscreen for the focused window.
    Falls back to sending ⌃⌘F if AXFullScreen isn't available.
    """
    _ensure_accessibility_or_raise()
    win = _focused_window_for_actions()
    if not win:
        return False
    # Try AX attribute first
    try:
        cur = _ax_copy(win, AX_FULLSCREEN)
        if isinstance(cur, bool) and cur is False:
            Quartz.AXUIElementSetAttributeValue(win, AX_FULLSCREEN, True)
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

def minimize_active_window() -> bool:
    """
    Minimize the focused window. Uses AXMinimized; falls back to pressing the
    minimize button (AXPress) if available.
    """
    _ensure_accessibility_or_raise()
    win = _focused_window_for_actions()
    if not win:
        return False
    # Prefer attribute
    try:
        Quartz.AXUIElementSetAttributeValue(win, AX_MINIMIZED, True)
        return True
    except Exception:
        pass
    # Fallback: press the minimize button
    try:
        btn = _ax_copy(win, AX_MINIMIZE_BTN)
        if btn and getattr(Quartz, "AXUIElementPerformAction", None) is not None:
            Quartz.AXUIElementPerformAction(btn, AX_PRESS)
            return True
    except Exception:
        pass
    return False

def move_active_window_left_half() -> bool:   
    return _do_region("left")

def move_active_window_right_half() -> bool:  
    return _do_region("right")

def move_active_window_top_half() -> bool:    
    return _do_region("top")

def move_active_window_bottom_half() -> bool: 
    return _do_region("bottom")

def move_active_window_left_third() -> bool:   
    return _do_region("left_third")

def move_active_window_middle_third() -> bool: 
    return _do_region("middle_third")

def move_active_window_right_third() -> bool:  
    return _do_region("right_third")

def move_active_window_left_two_third() -> bool: 
    return _do_region("left_two_third")

def move_active_window_right_two_third() -> bool: 
    return _do_region("right_two_third")

def move_active_window_top_left_quarter() -> bool:
    return _do_region("top_left_quarter")   

def move_active_window_top_right_quarter() -> bool:
    return _do_region("top_right_quarter")

def move_active_window_bottom_left_quarter() -> bool:
    return _do_region("bottom_left_quarter")

def move_active_window_bottom_right_quarter() -> bool:
    return _do_region("bottom_right_quarter")

def move_active_window_maximize() -> bool:
    return _do_region("maximize")
