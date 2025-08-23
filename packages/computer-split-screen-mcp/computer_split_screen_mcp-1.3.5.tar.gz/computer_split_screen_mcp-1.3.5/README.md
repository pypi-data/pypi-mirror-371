# Computer Split Screen MCP

Cross-platform MCP server that exposes split-screen tools (halves, quadrants, thirds) plus maximize/minimize for both Windows and macOS.  
Works with MCP clients via `uvx`.

## Features

- **Cross-platform support**: Windows and macOS
- **Split-screen layouts**: Halves, quadrants, thirds, and two-thirds variations
- **Window controls**: Maximize and minimize
- **MCP integration**: Full Model Context Protocol server support
- **Native performance**: Uses PyObjC on macOS and pywin32 on Windows for optimal performance
- **No external scripts**: Pure Python implementation with native OS APIs

## Install / Run via MCP client

Configure your MCP client:

```json
{
  "mcpServers": {
    "computer-split-screen": {
      "command": "uvx",
      "args": ["computer-split-screen-mcp"],
      "env": {}
    }
  }
}
```

## Available Tools

- `left-half` - Snap current window to left half
- `right-half` - Snap current window to right half
- `top-half` - Snap current window to top half
- `bottom-half` - Snap current window to bottom half
- `top-left` - Top-left quadrant
- `top-right` - Top-right quadrant
- `bottom-left` - Bottom-left quadrant
- `bottom-right` - Bottom-right quadrant
- `left-third` - Left third (1/3)
- `middle-third` - Middle third (1/3)
- `right-third` - Right third (1/3)
- `left-two-thirds` - Left two-thirds (2/3)
- `right-two-thirds` - Right two-thirds (2/3)
- `maximize` - OS maximize (bordered)
- `fullscreen` - Fullscreen (no borders via macOS)(bordered via Windows)
- `minimize` - Minimize window

## Platform Dependencies

- **Windows**: Requires `pywin32>=306`
- **macOS**: Requires `pyobjc-framework-Cocoa>=10.0`, `pyobjc-framework-Quartz>=10.0`, and `pyobjc-framework-ApplicationServices>=10.0`

## What's New in v1.3.0

- **Complete macOS rewrite**: Replaced AppleScript with native PyObjC implementation
- **Improved performance**: Faster window operations on macOS using Accessibility APIs
- **Better reliability**: More robust window detection and positioning
- **Enhanced error handling**: Graceful fallbacks when platform-specific features are unavailable
- **Multi-monitor support**: Improved handling of complex display configurations

## Technical Details

### macOS Implementation
- Uses PyObjC frameworks for native macOS integration
- Leverages Accessibility APIs (AX) for precise window manipulation
- Handles coordinate system conversion between macOS and AX coordinate systems
- Respects macOS-specific features like Dock and menu bar positioning
- Supports both standard windows and document windows

### Windows Implementation
- Uses pywin32 for Windows API access
- Implements DPI awareness for high-DPI displays
- Uses DWM (Desktop Window Manager) for accurate frame bounds
- Handles window insets and shadows properly
- Calculates positions as fractions of monitor work area
