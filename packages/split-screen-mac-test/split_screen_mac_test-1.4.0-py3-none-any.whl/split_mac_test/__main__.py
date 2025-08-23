from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from .window_actions import (
    move_active_window_left_half, move_active_window_right_half,
    move_active_window_top_half, move_active_window_bottom_half,
    move_active_window_left_third, move_active_window_middle_third, move_active_window_right_third,
    move_active_window_left_two_third, move_active_window_right_two_third,
    move_active_window_top_left_quarter, move_active_window_top_right_quarter,
    move_active_window_bottom_left_quarter, move_active_window_bottom_right_quarter,
    move_active_window_maximize, fullscreen_active_window, minimize_active_window,
)

mcp = FastMCP("split-screen-mac-test")

def ok(msg: str) -> TextContent:
    return TextContent(type="text", text=msg)

@mcp.tool("left-half-screen", description="Relocates the currently focused (active) window to exactly fill the left half of the display it is currently on")
def left_half() -> TextContent:
    success = move_active_window_left_half()
    return ok("left-half: done" if success else "left-half: failed")

@mcp.tool("right-half-screen", description="Relocates the currently focused (active) window to exactly fill the right half of the display it is currently on")
def right_half() -> TextContent:
    success = move_active_window_right_half()
    return ok("right-half: done" if success else "right-half: failed")

@mcp.tool("top-half-screen", description="Relocates the currently focused (active) window to exactly fill the top half of the display it is currently on")
def top_half() -> TextContent:
    success = move_active_window_top_half()
    return ok("top-half: done" if success else "top-half: failed")

@mcp.tool("bottom-half-screen", description="Relocates the currently focused (active) window to exactly fill the bottom half of the display it is currently on")
def bottom_half() -> TextContent:
    success = move_active_window_bottom_half()
    return ok("bottom-half: done" if success else "bottom-half: failed")

@mcp.tool("top-left-screen", description="Relocates the currently focused (active) window to exactly fill the top-left quadrant of the display it is currently on")
def top_left() -> TextContent:
    success = move_active_window_top_left_quarter()
    return ok("top-left: done" if success else "top-left: failed")

@mcp.tool("top-right-screen", description="Relocates the currently focused (active) window to exactly fill the top-right quadrant of the display it is currently on")
def top_right() -> TextContent:
    success = move_active_window_top_right_quarter()
    return ok("top-right: done" if success else "top-right: failed")

@mcp.tool("bottom-left-screen", description="Relocates the currently focused (active) window to exactly fill the bottom-left quadrant of the display it is currently on")
def bottom_left() -> TextContent:
    success = move_active_window_bottom_left_quarter()
    return ok("bottom-left: done" if success else "bottom-left: failed")

@mcp.tool("bottom-right-screen", description="Relocates the currently focused (active) window to exactly fill the bottom-right quadrant of the display it is currently on")
def bottom_right() -> TextContent:
    success = move_active_window_bottom_right_quarter()
    return ok("bottom-right: done" if success else "bottom-right: failed")

@mcp.tool("left-one-third-screen", description="Relocates the currently focused (active) window to exactly fill the left one third of the display it is currently on")
def left_third() -> TextContent:
    success = move_active_window_left_third()
    return ok("left-third: done" if success else "left-third: failed")

@mcp.tool("middle-one-third-screen", description="Relocates the currently focused (active) window to exactly fill the middle one third of the display it is currently on")
def middle_third() -> TextContent:
    success = move_active_window_middle_third()
    return ok("middle-third: done" if success else "middle-third: failed")

@mcp.tool("right-one-third-screen", description="Relocates the currently focused (active) window to exactly fill the right one third of the display it is currently on")
def right_third() -> TextContent:
    success = move_active_window_right_third()
    return ok("right-third: done" if success else "right-third: failed")

@mcp.tool("left-two-thirds-screen", description="Relocates the currently focused (active) window to exactly fill the left two thirds of the display it is currently on")
def left_two_thirds() -> TextContent:
    success = move_active_window_left_two_third()
    return ok("left-two-thirds: done" if success else "left-two-thirds: failed")

@mcp.tool("right-two-thirds-screen", description="Relocates the currently focused (active) window to exactly fill the right two thirds of the display it is currently on")
def right_two_thirds() -> TextContent:
    success = move_active_window_right_two_third()
    return ok("right-two-thirds: done" if success else "right-two-thirds: failed")

@mcp.tool("maximize-screen", description="Maximizes the currently focused (active) window to fill the entire display it is currently on, while keeping its borders and title bar visible")
def maximize() -> TextContent:
    success = move_active_window_maximize()
    return ok("maximize: done" if success else "maximize: failed")

@mcp.tool("fullscreen-screen", description="Fullscreen the currently focused (active) window using native macOS fullscreen mode (borderless, no title bar)")
def fullscreen() -> TextContent:
    success = fullscreen_active_window()
    return ok("fullscreen: done" if success else "fullscreen: failed")

@mcp.tool("minimize-screen", description="Minimizes the currently focused (active) window, sending it to the Dock")
def minimize() -> TextContent:
    success = minimize_active_window()
    return ok("minimize: done" if success else "minimize: failed")

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
