# Linux Platform Guide

## System Requirements

- Linux kernel 3.x or higher
- libpcap development libraries
- gcc/g++ 7.0 or higher
- Make or CMake

## Installation

### Installing Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install build-essential libpcap-dev
```

#### Fedora/RHEL
```bash
sudo dnf install gcc gcc-c++ libpcap-devel
```

#### Arch Linux
```bash
sudo pacman -S base-devel libpcap
```

## Building from Source

```bash
cd NetworkzeroMonitor
# Build instructions will be added
```

## Running

```bash
# May require root privileges
sudo ./networkzero-monitor
```

## Configuration

Configuration options specific to Linux will be documented here.

## Troubleshooting

### Permission Denied

Network monitoring requires elevated privileges:
```bash
# Run with sudo
sudo ./networkzero-monitor

# Or set capabilities
sudo setcap cap_net_raw,cap_net_admin=eip ./networkzero-monitor
```

### libpcap Not Found

Ensure libpcap is installed:
```bash
# Ubuntu/Debian
sudo apt-get install libpcap-dev

# Fedora/RHEL
sudo dnf install libpcap-devel
```

## Platform-Specific Features

- Native packet capture using libpcap
- Integration with Linux networking stack
- Support for various network interfaces
