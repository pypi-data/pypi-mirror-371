#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .functions import (
    move_active_window_left_half, move_active_window_right_half,
    move_active_window_top_half, move_active_window_bottom_half,
    move_active_window_left_third, move_active_window_middle_third, move_active_window_right_third,
    move_active_window_left_two_third, move_active_window_right_two_third,
    move_active_window_top_left_quarter, move_active_window_top_right_quarter,
    move_active_window_bottom_left_quarter, move_active_window_bottom_right_quarter,
    move_active_window_maximize, fullscreen_active_window, minimize_active_window
)

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent


mcp = FastMCP("split-screen-macOS-test-copy")


def ok(msg: str) -> TextContent:
    return TextContent(type="text", text=msg)


def error(msg: str) -> TextContent:
    return TextContent(type="text", text=f"Error: {msg}")


# ---------- Window Positioning Tools ----------

@mcp.tool("move-window-left-half", description="Move the active window to the left half of the screen")
def move_left_half() -> TextContent:
    try:
        result = move_active_window_left_half()
        if result:
            return ok("Window moved to left half successfully")
        else:
            return error("Failed to move window to left half")
    except Exception as e:
        return error(f"Error moving window to left half: {str(e)}")


@mcp.tool("move-window-right-half", description="Move the active window to the right half of the screen")
def move_right_half() -> TextContent:
    try:
        result = move_active_window_right_half()
        if result:
            return ok("Window moved to right half successfully")
        else:
            return error("Failed to move window to right half")
    except Exception as e:
        return error(f"Error moving window to right half: {str(e)}")


@mcp.tool("move-window-top-half", description="Move the active window to the top half of the screen")
def move_top_half() -> TextContent:
    try:
        result = move_active_window_top_half()
        if result:
            return ok("Window moved to top half successfully")
        else:
            return error("Failed to move window to top half")
    except Exception as e:
        return error(f"Error moving window to top half: {str(e)}")


@mcp.tool("move-window-bottom-half", description="Move the active window to the bottom half of the screen")
def move_bottom_half() -> TextContent:
    try:
        result = move_active_window_bottom_half()
        if result:
            return ok("Window moved to bottom half successfully")
        else:
            return error("Failed to move window to bottom half")
    except Exception as e:
        return error(f"Error moving window to bottom half: {str(e)}")


# ---------- Thirds Positioning Tools ----------

@mcp.tool("move-window-left-third", description="Move the active window to the left third of the screen")
def move_left_third() -> TextContent:
    try:
        result = move_active_window_left_third()
        if result:
            return ok("Window moved to left third successfully")
        else:
            return error("Failed to move window to left third")
    except Exception as e:
        return error(f"Error moving window to left third: {str(e)}")


@mcp.tool("move-window-middle-third", description="Move the active window to the middle third of the screen")
def move_middle_third() -> TextContent:
    try:
        result = move_active_window_middle_third()
        if result:
            return ok("Window moved to middle third successfully")
        else:
            return error("Failed to move window to middle third")
    except Exception as e:
        return error(f"Error moving window to middle third: {str(e)}")


@mcp.tool("move-window-right-third", description="Move the active window to the right third of the screen")
def move_right_third() -> TextContent:
    try:
        result = move_active_window_right_third()
        if result:
            return ok("Window moved to right third successfully")
        else:
            return error("Failed to move window to right third")
    except Exception as e:
        return error(f"Error moving window to right third: {str(e)}")


# ---------- Two-Thirds Positioning Tools ----------

@mcp.tool("move-window-left-two-thirds", description="Move the active window to the left two-thirds of the screen")
def move_left_two_thirds() -> TextContent:
    try:
        result = move_active_window_left_two_third()
        if result:
            return ok("Window moved to left two-thirds successfully")
        else:
            return error("Failed to move window to left two-thirds")
    except Exception as e:
        return error(f"Error moving window to left two-thirds: {str(e)}")


@mcp.tool("move-window-right-two-thirds", description="Move the active window to the right two-thirds of the screen")
def move_right_two_thirds() -> TextContent:
    try:
        result = move_active_window_right_two_third()
        if result:
            return ok("Window moved to right two-thirds successfully")
        else:
            return error("Failed to move window to right two-thirds")
    except Exception as e:
        return error(f"Error moving window to right two-thirds: {str(e)}")


# ---------- Quarter Positioning Tools ----------

@mcp.tool("move-window-top-left-quarter", description="Move the active window to the top-left quarter of the screen")
def move_top_left_quarter() -> TextContent:
    try:
        result = move_active_window_top_left_quarter()
        if result:
            return ok("Window moved to top-left quarter successfully")
        else:
            return error("Failed to move window to top-left quarter")
    except Exception as e:
        return error(f"Error moving window to top-left quarter: {str(e)}")


@mcp.tool("move-window-top-right-quarter", description="Move the active window to the top-right quarter of the screen")
def move_top_right_quarter() -> TextContent:
    try:
        result = move_active_window_top_right_quarter()
        if result:
            return ok("Window moved to top-right quarter successfully")
        else:
            return error("Failed to move window to top-right quarter")
    except Exception as e:
        return error(f"Error moving window to top-right quarter: {str(e)}")


@mcp.tool("move-window-bottom-left-quarter", description="Move the active window to the bottom-left quarter of the screen")
def move_bottom_left_quarter() -> TextContent:
    try:
        result = move_active_window_bottom_left_quarter()
        if result:
            return ok("Window moved to bottom-left quarter successfully")
        else:
            return error("Failed to move window to bottom-left quarter")
    except Exception as e:
        return error(f"Error moving window to bottom-left quarter: {str(e)}")


@mcp.tool("move-window-bottom-right-quarter", description="Move the active window to the bottom-right quarter of the screen")
def move_bottom_right_quarter() -> TextContent:
    try:
        result = move_active_window_bottom_right_quarter()
        if result:
            return ok("Window moved to bottom-right quarter successfully")
        else:
            return error("Failed to move window to bottom-right quarter")
    except Exception as e:
        return error(f"Error moving window to bottom-right quarter: {str(e)}")


# ---------- Special Window Management Tools ----------

@mcp.tool("move-window-maximize", description="Maximize the active window to fill the entire screen (excluding Dock and menu bar)")
def move_maximize() -> TextContent:
    try:
        result = move_active_window_maximize()
        if result:
            return ok("Window maximized successfully")
        else:
            return error("Failed to maximize window")
    except Exception as e:
        return error(f"Error maximizing window: {str(e)}")


@mcp.tool("window-fullscreen", description="Toggle fullscreen mode for the active window")
def window_fullscreen() -> TextContent:
    try:
        result = fullscreen_active_window()
        if result:
            return ok("Window fullscreen toggled successfully")
        else:
            return error("Failed to toggle window fullscreen")
    except Exception as e:
        return error(f"Error toggling window fullscreen: {str(e)}")


@mcp.tool("window-minimize", description="Minimize the active window")
def window_minimize() -> TextContent:
    try:
        result = minimize_active_window()
        if result:
            return ok("Window minimized successfully")
        else:
            return error("Failed to minimize window")
    except Exception as e:
        return error(f"Error minimizing window: {str(e)}")


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
