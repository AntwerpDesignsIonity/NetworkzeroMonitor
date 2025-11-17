# Windows Platform Guide

## System Requirements

- Windows 10 or higher (64-bit)
- Visual Studio 2019 or higher
- WinPcap or Npcap

## Installation

### Installing Prerequisites

1. **Install Visual Studio**
   - Download from [Visual Studio website](https://visualstudio.microsoft.com/)
   - Select "Desktop development with C++" workload

2. **Install Npcap**
   - Download from [Npcap website](https://npcap.com/)
   - Install with "WinPcap Compatible Mode" enabled

## Building from Source

```batch
# Using Visual Studio
# Open NetworkzeroMonitor.sln
# Build -> Build Solution

# Or using MSBuild from command line
msbuild NetworkzeroMonitor.sln /p:Configuration=Release
```

## Running

```batch
# Run the executable
networkzero-monitor.exe
```

## Configuration

Configuration options specific to Windows will be documented here.

## Troubleshooting

### WinPcap/Npcap Not Found

Ensure Npcap is installed:
1. Download Npcap from the official website
2. Install with administrator privileges
3. Enable "WinPcap Compatible Mode" during installation

### Permission Issues

Run as Administrator:
1. Right-click on the executable
2. Select "Run as administrator"

### Firewall Warnings

Windows Firewall may prompt for network access:
1. Allow access for the application
2. Configure firewall rules if needed

## Platform-Specific Features

- Native Windows packet capture using Npcap
- Windows-native GUI
- Integration with Windows networking
- Support for Windows network adapters
