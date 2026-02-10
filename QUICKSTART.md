# NetworkzeroMonitor - Quick Start Guide
**Ionity (Pty) Ltd - www.ionity.today**

## Quick Installation

### Windows
1. Double-click `setup.bat`
2. Wait for installation to complete

### Linux/macOS
1. Open terminal in the NetworkzeroMonitor directory
2. Run: `./setup.sh`

## Running the Application

### GUI (Graphical Interface)
**Windows:**
- Double-click `run_gui.bat`

**Linux/macOS:**
- Run: `./run_gui.sh`

### CLI (Command Line)
**Windows:**
- Run: `run_cli.bat status` (or any other command)

**Linux/macOS:**
- Run: `./run_cli.sh status` (or any other command)

## Common Commands

### Check Network Status
```bash
./run_cli.sh status
```

### DNS Lookup
```bash
./run_cli.sh dns google.com
./run_cli.sh dns github.com -s 8.8.8.8
```

### Ping Test
```bash
./run_cli.sh ping 8.8.8.8
./run_cli.sh ping google.com -c 10
```

### Monitor Network (Continuous)
```bash
./run_cli.sh monitor --host 8.8.8.8 --interval 5
```

### Pi-hole Monitoring
```bash
./run_cli.sh pihole status --url http://192.168.1.1
./run_cli.sh pihole summary --url http://192.168.1.1
./run_cli.sh pihole blocked --url http://192.168.1.1 --count 20
```

## GUI Features

### Dashboard Tab
- View network information (hostname, IP addresses)
- Check internet connectivity status
- See quality indicators

### Ping Tab
- Enter hostname or IP address
- Set number of ping requests
- View detailed ping results

### DNS Lookup Tab
- Enter domain name to resolve
- Optionally specify DNS server
- See IP addresses and query time

### Pi-hole Tab
- Configure Pi-hole URL and API key
- Check Pi-hole status
- View summary statistics
- See top blocked domains

### Live Monitor Tab
- Set host to monitor
- Configure check interval
- Start/stop continuous monitoring
- View real-time activity log

## Configuration

Edit `config.ini` to customize:
- Default hosts and domains
- DNS servers
- Monitoring intervals
- Pi-hole connection details
- UI preferences

## Troubleshooting

### "Python not found" Error
- Install Python 3.8 or higher from python.org
- Ensure Python is in your system PATH

### Ping Permission Issues (Linux/macOS)
- Run with sudo: `sudo ./run_cli.sh ping google.com`
- Or use alternative connectivity checks

### Pi-hole Connection Failed
- Verify Pi-hole URL is correct
- Check Pi-hole web interface is accessible
- Ensure no firewall is blocking connection

## Support

For issues and support, visit: **www.ionity.today**

---
*Copyright © 2026 Ionity (Pty) Ltd - All rights reserved*
