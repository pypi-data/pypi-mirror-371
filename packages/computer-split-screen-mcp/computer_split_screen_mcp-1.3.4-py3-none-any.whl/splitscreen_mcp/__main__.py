from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from .window_actions import (
    left_half_window, right_half_window,
    top_half_window, bottom_half_window,
    top_left_quadrant_window, top_right_quadrant_window,
    bottom_left_quadrant_window, bottom_right_quadrant_window,
    left_third_window, middle_third_window, right_third_window,
    left_two_thirds_window, right_two_thirds_window,
    maximise_window, minimise_window, fullscreen_window,
)

mcp = FastMCP("computer-split-screen")

def ok(msg: str) -> TextContent:
    return TextContent(type="text", text=msg)

@mcp.tool("left-half-screen", description="Relocates the currently focused (active) window to exactly fill the left half of the display it is currently on")
def left_half() -> TextContent:
    left_half_window()
    return ok("")

@mcp.tool("right-half-screen", description="Relocates the currently focused (active) window to exactly fill the right half of the display it is currently on")
def right_half() -> TextContent:
    right_half_window()
    return ok("")

@mcp.tool("top-half-screen", description="Relocates the currently focused (active) window to exactly fill the top half of the display it is currently on")
def top_half() -> TextContent:
    top_half_window()
    return ok("")

@mcp.tool("bottom-half-screen", description="Relocates the currently focused (active) window to exactly fill the bottom half of the display it is currently on")
def bottom_half() -> TextContent:
    bottom_half_window()
    return ok("")

@mcp.tool("top-left-screen", description="Relocates the currently focused (active) window to exactly fill the top-left quadrant of the display it is currently on")
def top_left() -> TextContent:
    top_left_quadrant_window()
    return ok("")

@mcp.tool("top-right-screen", description="Relocates the currently focused (active) window to exactly fill the top-right quadrant of the display it is currently on")
def top_right() -> TextContent:
    top_right_quadrant_window()
    return ok("")

@mcp.tool("bottom-left-screen", description="Relocates the currently focused (active) window to exactly fill the bottom-left quadrant of the display it is currently on")
def bottom_left() -> TextContent:
    bottom_left_quadrant_window()
    return ok("")

@mcp.tool("bottom-right-screen", description="Relocates the currently focused (active) window to exactly fill the bottom-right quadrant of the display it is currently on")
def bottom_right() -> TextContent:
    bottom_right_quadrant_window()
    return ok("")

@mcp.tool("left-one-third-screen", description="Relocates the currently focused (active) window to exactly fill the left one third of the display it is currently on")
def left_third() -> TextContent:
    left_third_window()
    return ok("")

@mcp.tool("middle-one-third-screen", description="Relocates the currently focused (active) window to exactly fill the middle one third of the display it is currently on")
def middle_third() -> TextContent:
    middle_third_window()
    return ok("")

@mcp.tool("right-one-third-screen", description="Relocates the currently focused (active) window to exactly fill the right one third of the display it is currently on")
def right_third() -> TextContent:
    right_third_window()
    return ok("")

@mcp.tool("left-two-thirds-screen", description="Relocates the currently focused (active) window to exactly fill the left two thirds of the display it is currently on")
def left_two_thirds() -> TextContent:
    left_two_thirds_window()
    return ok("")

@mcp.tool("right-two-thirds-screen", description="Relocates the currently focused (active) window to exactly fill the right two thirds of the display it is currently on")
def right_two_thirds() -> TextContent:
    right_two_thirds_window()
    return ok("")

@mcp.tool("maximize-screen", description="Maximizes the currently focused (active) window to fill the entire display it is currently on, while keeping its borders and title bar visible")
def maximize() -> TextContent:
    maximise_window()
    return ok("")

@mcp.tool("fullscreen-screen", description="Fullscreen the currently focused (active) window. On macOS, this uses fullscreen mode (borderless, no title bar). On Windows, this uses standard maximize mode (with borders and title bar visible)")
def fullscreen() -> TextContent:
    fullscreen_window()
    return ok("")

@mcp.tool("minimize-screen", description="Minimizes the currently focused (active) window, sending it to the Windows taskbar (on Windows) or the Dock (on macOS)")
def minimize() -> TextContent:
    minimise_window()
    return ok("")

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
