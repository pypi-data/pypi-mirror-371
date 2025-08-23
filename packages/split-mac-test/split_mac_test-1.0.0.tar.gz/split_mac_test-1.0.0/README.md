# Split Mac Test MCP Server

MCP server that exposes macOS split-screen tools via native PyObjC/Quartz APIs for maximum performance and reliability.

## Features

- **Native macOS implementation**: Uses PyObjC, Quartz, and AppKit for direct system access
- **Split-screen layouts**: Halves, quadrants, thirds, and two-thirds variations
- **Window controls**: Maximize, minimize, and fullscreen
- **MCP integration**: Full Model Context Protocol server support
- **No startup issues**: Screen detection only happens when tools are called

## Install / Run via MCP client

Configure your MCP client:

```json
{
  "mcpServers": {
    "split-mac-test": {
      "command": "uvx",
      "args": ["split-mac-test-mcp"],
      "env": {}
    }
  }
}
```

## Available Tools

- `left-half-screen` - Snap current window to left half
- `right-half-screen` - Snap current window to right half
- `top-half-screen` - Snap current window to top half
- `bottom-half-screen` - Snap current window to bottom half
- `top-left-screen` - Top-left quadrant
- `top-right-screen` - Top-right quadrant
- `bottom-left-screen` - Bottom-left quadrant
- `bottom-right-screen` - Bottom-right quadrant
- `left-one-third-screen` - Left third (1/3)
- `middle-one-third-screen` - Middle third (1/3)
- `right-one-third-screen` - Right third (1/3)
- `left-two-thirds-screen` - Left two-thirds (2/3)
- `right-two-thirds-screen` - Right two-thirds (2/3)
- `maximize-screen` - OS maximize (bordered)
- `fullscreen-screen` - Fullscreen (no borders)
- `minimize-screen` - Minimize window

## Technical Details

- **Platform**: macOS only (uses native PyObjC APIs)
- **Dependencies**: `mcp>=0.1.0`, PyObjC (built into most macOS Python installs)
- **Architecture**: Direct system calls via Quartz/AppKit for maximum performance
- **Startup**: Safe MCP initialization with lazy screen detection

## Advantages over AppleScript-based solutions

- **Faster execution**: Direct API calls vs. AppleScript interpretation
- **Better error handling**: Native exception handling and fallbacks
- **More reliable**: No AppleScript parsing or execution issues
- **Lower latency**: Direct system access without intermediate layers
