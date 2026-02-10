# NetworkzeroMonitor

**Network Monitoring and Diagnostics Tool**  
*Ionity (Pty) Ltd - [www.ionity.today](https://www.ionity.today)*

---

## Overview

NetworkzeroMonitor is a comprehensive network monitoring application that provides real-time network status, connectivity checks, DNS diagnostics, and Pi-hole integration. The application features both a graphical user interface (GUI) and a command-line interface (CLI) for flexibility in different environments.

## Features

### Core Network Monitoring
- **Ping Monitoring**: Test connectivity to any host with detailed statistics
- **DNS Resolution**: Check DNS lookup performance and results
- **Network Status**: Monitor overall internet connectivity and quality
- **Network Information**: Display local and public IP addresses, hostname, and platform details

### Pi-hole Integration
- **Status Monitoring**: Check Pi-hole service status
- **Statistics Dashboard**: View DNS queries, blocked ads, and blocking percentage
- **Top Blocked Domains**: See the most frequently blocked domains

### Dual Interface
- **Graphical User Interface (GUI)**: Full-featured desktop application with tabbed interface
- **Command-Line Interface (CLI)**: Scriptable commands for automation and remote use

### Continuous Monitoring
- Real-time monitoring with configurable intervals
- Live activity display
- Quality indicators and status symbols

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Setup

#### Windows
1. Clone or download the repository
2. Run the setup script:
   ```batch
   setup.bat
   ```

#### Linux/macOS
1. Clone or download the repository
2. Make the setup script executable and run it:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

### Manual Installation
If you prefer to install manually:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate.bat
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Starting the Application

#### GUI Mode
```bash
# Activate virtual environment first
# Windows: venv\Scripts\activate.bat
# Linux/macOS: source venv/bin/activate

# Launch GUI
python networkzero_gui.py
```

#### CLI Mode
```bash
# Activate virtual environment first
# Windows: venv\Scripts\activate.bat
# Linux/macOS: source venv/bin/activate

# Run CLI commands
python networkzero_cli.py --help
```

### CLI Commands

#### Ping a Host
```bash
python networkzero_cli.py ping google.com
python networkzero_cli.py ping 8.8.8.8 -c 10 -t 5
```

#### DNS Lookup
```bash
python networkzero_cli.py dns github.com
python networkzero_cli.py dns example.com -s 1.1.1.1
```

#### Check Network Status
```bash
python networkzero_cli.py status
python networkzero_cli.py status -v  # verbose mode
```

#### Pi-hole Monitoring
```bash
# Check Pi-hole status
python networkzero_cli.py pihole status --url http://192.168.1.1

# Get summary statistics
python networkzero_cli.py pihole summary --url http://192.168.1.1

# View top blocked domains
python networkzero_cli.py pihole blocked --url http://192.168.1.1 --count 20
```

#### Continuous Monitoring
```bash
python networkzero_cli.py monitor --host 8.8.8.8 --interval 5
```

### GUI Features

The GUI application provides a tabbed interface with the following sections:

1. **Dashboard**: Overview of network information and connectivity status
2. **Ping**: Interactive ping tool with customizable parameters
3. **DNS Lookup**: DNS resolution testing with custom DNS server support
4. **Pi-hole**: Pi-hole monitoring and statistics (requires Pi-hole instance)
5. **Live Monitor**: Continuous real-time network monitoring

## Configuration

Edit `config.ini` to customize default settings:

- Default hosts and domains to monitor
- DNS servers
- Monitoring intervals
- Pi-hole connection details
- UI preferences

## Pi-hole Integration

To use Pi-hole features:

1. Ensure you have a Pi-hole instance running on your network
2. Configure the Pi-hole URL in the GUI or provide it via CLI
3. (Optional) Generate an API key in Pi-hole settings for authenticated access
4. Use the Pi-hole tab in GUI or `pihole` commands in CLI

## Project Structure

```
NetworkzeroMonitor/
├── network_monitor.py      # Core monitoring module
├── networkzero_cli.py      # Command-line interface
├── networkzero_gui.py      # Graphical user interface
├── requirements.txt        # Python dependencies
├── config.ini             # Configuration file
├── setup.bat              # Windows setup script
├── setup.sh               # Linux/macOS setup script
└── README.md              # This file
```

## Dependencies

- `ping3`: ICMP ping functionality
- `dnspython`: DNS resolution
- `psutil`: System and network utilities
- `requests`: HTTP requests for Pi-hole API
- `matplotlib`: Data visualization (optional)
- `tkinter`: GUI framework (included with Python)

## Requirements

- Operating System: Windows, Linux, or macOS
- Python: 3.8 or higher
- Network: Active internet connection for full functionality
- (Optional) Pi-hole instance for Pi-hole monitoring features

## Troubleshooting

### Ping Issues
- On Linux/macOS, you may need root privileges for ICMP ping
- Use `sudo` when running commands if you get permission errors

### DNS Resolution
- Ensure your system has working DNS configuration
- Try using a public DNS server like 8.8.8.8 or 1.1.1.1

### Pi-hole Connection
- Verify Pi-hole URL is correct and accessible
- Check if Pi-hole's web interface is enabled
- Ensure API access is not blocked by firewall

### GUI Issues
- Ensure tkinter is installed (usually comes with Python)
- On Linux, you may need: `sudo apt-get install python3-tk`

## Development

### Running Tests
```bash
# Test core monitoring module
python network_monitor.py
```

### Contributing
This project is developed and maintained by Ionity (Pty) Ltd.

## License

Copyright © 2026 Ionity (Pty) Ltd  
All rights reserved.

## Support

For support, please visit [www.ionity.today](https://www.ionity.today)

## About Ionity

Ionity (Pty) Ltd is dedicated to providing innovative network monitoring and management solutions. Visit us at [www.ionity.today](https://www.ionity.today) for more information about our products and services.
