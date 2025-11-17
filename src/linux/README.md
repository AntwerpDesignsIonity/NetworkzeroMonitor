# Linux Module

Linux-specific implementation of NetworkZero Monitor.

## Requirements

- Linux kernel 3.x or higher
- libpcap
- gcc/g++ compiler

## Features

- Native packet capture using libpcap
- Interface selection and management
- System integration
- Command-line interface

## Building

```bash
# Build instructions will be added
cd src/linux
make
```

## Supported Distributions

- Ubuntu 18.04+
- Debian 10+
- Fedora 30+
- Arch Linux
- Other distributions with modern kernels

## Permissions

Network monitoring requires appropriate permissions:
```bash
# May require root or CAP_NET_RAW capability
sudo ./networkzero-monitor
```
