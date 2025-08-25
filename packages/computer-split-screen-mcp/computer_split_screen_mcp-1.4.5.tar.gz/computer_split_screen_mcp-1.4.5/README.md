# Computer Split Screen MCP

A high-performance, cross-platform Model Context Protocol (MCP) server that provides reliable split-screen window management for both Windows and macOS. This server exposes 16 window manipulation tools through the MCP protocol, enabling AI assistants and other MCP clients to control desktop window layouts with precision.

## 🚀 Features

- **Cross-platform support**: Windows and macOS with native optimizations
- **16 window management tools**: Comprehensive split-screen layouts and controls
- **High performance**: Windows: 15-60ms, macOS: 50-150ms per operation
- **Reliability first**: Robust fallback mechanisms and error handling
- **MCP integration**: Full Model Context Protocol server support via stdio transport
- **Smart focus detection**: Advanced window focus detection with platform-specific optimizations

## 🛠️ Installation

### Prerequisites

- **Python**: 3.9 or higher
- **Package Manager**: `uvx` (recommended) or `pip`

### Install via uvx (Recommended)

```bash
uvx install computer-split-screen-mcp
```

### Install via pip

```bash
pip install computer-split-screen-mcp
```

## 🔧 MCP Client Configuration

Configure your MCP client with the following settings:

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

### Alternative Configuration (if not using uvx)

```json
{
  "mcpServers": {
    "computer-split-screen": {
      "command": "python",
      "args": ["-m", "computer-split-screen-mcp"],
      "env": {}
    }
  }
}
```

## 🎯 Available Tools

### Split-Screen Layouts

#### Halves (2-way splits)
- `left-half-screen` - Snap current window to left half
- `right-half-screen` - Snap current window to right half
- `top-half-screen` - Snap current window to top half
- `bottom-half-screen` - Snap current window to bottom half

#### Quadrants (4-way splits)
- `top-left-screen` - Top-left quadrant (1/4 screen)
- `top-right-screen` - Top-right quadrant (1/4 screen)
- `bottom-left-screen` - Bottom-left quadrant (1/4 screen)
- `bottom-right-screen` - Bottom-right quadrant (1/4 screen)

#### Thirds (3-way splits)
- `left-one-third-screen` - Left third (1/3 screen)
- `middle-one-third-screen` - Middle third (1/3 screen)
- `right-one-third-screen` - Right third (1/3 screen)

#### Two-Thirds (2/3 splits)
- `left-two-thirds-screen` - Left two-thirds (2/3 screen)
- `right-two-thirds-screen` - Right two-thirds (2/3 screen)

### Window Controls
- `maximize-screen` - OS maximize (bordered, taskbar visible)
- `fullscreen-screen` - Fullscreen mode (platform-specific behavior)
- `minimize-screen` - Minimize window to taskbar/dock

## ⚡ Performance Characteristics

### Windows Performance
- **Total time**: 15-60ms per operation
- **Detection**: 2-5ms (direct Win32 API)
- **Manipulation**: 10-47ms (SetWindowPos with corrections)
- **Best case**: 15-25ms for simple splits
- **Typical case**: 20-35ms for most operations

### macOS Performance
- **Total time**: 50-150ms per operation
- **Detection**: 20-50ms (AppleScript + Accessibility API)
- **Manipulation**: 15-55ms (AXUIElement operations)
- **Best case**: 50-80ms for simple splits
- **Typical case**: 80-120ms for most operations

## 🔍 Technical Architecture

### Windows Implementation
- **Direct Win32 API calls** via `pywin32`
- **DWM integration** for accurate frame bounds
- **DPI-aware positioning** for high-resolution displays
- **Two-pass positioning** for precise window placement

### macOS Implementation
- **AppleScript focus detection** for reliability
- **Accessibility API** for window manipulation
- **Fallback mechanisms** for edge cases
- **Screen-aware positioning** respecting menu bar and Dock

### Cross-Platform Features
- **Automatic platform detection**
- **Conditional dependency loading**
- **Unified API interface**
- **Error handling and recovery**

## 📋 Platform Dependencies

### Windows
- **Required**: `pywin32>=306`
- **Purpose**: Win32 API access, DWM integration, window manipulation

### macOS
- **Required**: `pyobjc-core>=10.1,<11`, `pyobjc-framework-Cocoa>=10.1,<11`, `pyobjc-framework-Quartz>=10.1,<11`, `pyobjc-framework-ApplicationServices>=10.1,<11`
- **Purpose**: Accessibility API, AppleScript integration, window management

## 🚨 Troubleshooting

### Common Issues

#### macOS Focus Detection Problems
- **Symptom**: Windows don't move or wrong windows are selected
- **Solution**: Ensure Terminal has Accessibility permissions in System Preferences > Security & Privacy > Privacy > Accessibility

#### Windows DPI Issues
- **Symptom**: Windows positioned incorrectly on high-DPI displays
- **Solution**: The server automatically handles DPI awareness, but ensure `pywin32>=306` is installed

#### MCP Client Connection Issues
- **Symptom**: Functions work when called directly but fail via MCP
- **Solution**: Check MCP client logs, ensure proper configuration, restart MCP client

### Performance Optimization
- **First run**: May be slower due to system warm-up
- **Subsequent runs**: Should be consistently fast
- **Complex apps**: Safari, Chrome may take longer due to window structure

## 🔧 Development

### Project Structure
```
computer-split-screen/
├── src/splitscreen_mcp/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # MCP server entry point
│   └── window_actions.py    # Core window management logic
├── pyproject.toml           # Project configuration
├── README.md               # This file
└── LICENSE                 # MIT License
```

### Building from Source
```bash
git clone https://github.com/Beta0415/computer-split-screen-mcp.git
cd computer-split-screen-mcp
uvx install -e .
```

### Running Tests
```bash
# Test window detection
python3 -c "from src.splitscreen_mcp.window_actions import left_half_window; left_half_window()"

# Test MCP server
uvx run computer-split-screen-mcp
```

### Contributing
- **Repository**: [https://github.com/Beta0415/computer-split-screen-mcp](https://github.com/Beta0415/computer-split-screen-mcp)
- **Issues**: [https://github.com/Beta0415/computer-split-screen-mcp/issues](https://github.com/Beta0415/computer-split-screen-mcp/issues)
- **Pull Requests**: Welcome! Please open an issue first for major changes.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📊 Version History

- **v1.4.4** - Current stable release
  - Cross-platform window management
  - 16 comprehensive tools
  - High-performance implementation
  - Full MCP protocol support

## 🆘 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review MCP client logs for errors
3. Test functions directly to isolate issues
4. Open an issue on the project repository

---

**Built with ❤️ for the MCP community**
