# NetworkzeroMonitor - Project Structure

**Ionity (Pty) Ltd - www.ionity.today**

---

## Directory Structure

```
NetworkzeroMonitor/
├── .git/                      # Git version control
├── .gitignore                 # Git ignore rules
├── venv/                      # Python virtual environment (created after setup)
│
├── CHANGELOG.md               # Version history and changes
├── EXAMPLES.md                # Detailed usage examples
├── LICENSE                    # MIT License
├── QUICKSTART.md              # Quick start guide
├── README.md                  # Main documentation
│
├── config.ini                 # Configuration file template
├── requirements.txt           # Python dependencies
│
├── network_monitor.py         # Core monitoring module
├── networkzero_cli.py         # Command-line interface
├── networkzero_gui.py         # Graphical user interface
├── test_networkzero.py        # Test suite
│
├── setup.bat                  # Windows setup script
├── setup.sh                   # Linux/macOS setup script
├── run_gui.bat                # Windows GUI launcher
├── run_gui.sh                 # Linux/macOS GUI launcher
├── run_cli.bat                # Windows CLI launcher
└── run_cli.sh                 # Linux/macOS CLI launcher
```

## File Descriptions

### Core Application Files

**network_monitor.py**
- Core network monitoring functionality
- Classes: `NetworkMonitor`, `PiHoleMonitor`
- Functions for ping, DNS lookup, connectivity checks, Pi-hole integration
- Independent module that can be imported by other scripts

**networkzero_cli.py**
- Command-line interface application
- Argument parsing and command handling
- Commands: ping, dns, status, pihole, monitor
- Can be run directly or via launcher scripts

**networkzero_gui.py**
- Graphical user interface application
- Built with tkinter
- Tabbed interface with 5 tabs: Dashboard, Ping, DNS, Pi-hole, Live Monitor
- Threading support for continuous monitoring

### Setup and Configuration

**requirements.txt**
- Python package dependencies
- Libraries: ping3, dnspython, psutil, requests, matplotlib, tkinter-tooltip

**config.ini**
- Configuration file template
- Settings for network monitoring, DNS servers, Pi-hole, UI preferences
- Can be customized by users

**setup.bat / setup.sh**
- Automated setup scripts
- Creates virtual environment
- Installs dependencies
- Platform-specific (Windows / Unix-like)

### Launcher Scripts

**run_gui.bat / run_gui.sh**
- Quick launchers for GUI application
- Activates virtual environment
- Starts GUI application

**run_cli.bat / run_cli.sh**
- Quick launchers for CLI application
- Activates virtual environment
- Passes arguments to CLI application

### Testing

**test_networkzero.py**
- Comprehensive test suite
- Tests all core functionality
- Can be run to validate installation

### Documentation

**README.md**
- Main documentation file
- Overview, features, installation, usage
- Troubleshooting and support information

**QUICKSTART.md**
- Quick reference guide
- Common commands and usage patterns
- Step-by-step instructions

**EXAMPLES.md**
- Detailed usage examples
- CLI, Python API, and integration examples
- Scripts for automation

**CHANGELOG.md**
- Version history
- Feature additions and changes
- Release notes

**LICENSE**
- MIT License
- Copyright information
- Usage rights and permissions

### Version Control

**.gitignore**
- Specifies files to exclude from git
- Excludes: venv/, __pycache__/, *.pyc, logs, etc.

## Module Dependencies

```
networkzero_gui.py
└── network_monitor.py
    ├── ping3
    ├── dnspython
    ├── psutil
    ├── requests
    └── socket, subprocess, platform, time

networkzero_cli.py
└── network_monitor.py
    └── (same dependencies as above)

test_networkzero.py
└── network_monitor.py
    └── (same dependencies as above)
```

## Key Classes

### NetworkMonitor
Located in: `network_monitor.py`

**Methods:**
- `ping_host(host, count, timeout)` - Ping a host
- `check_dns_resolution(domain, dns_server)` - DNS lookup
- `check_internet_connectivity()` - Overall connectivity check
- `get_network_info()` - Network information

### PiHoleMonitor
Located in: `network_monitor.py`

**Methods:**
- `__init__(pihole_url, api_key)` - Initialize with Pi-hole URL
- `get_summary()` - Get Pi-hole statistics
- `get_top_blocked(count)` - Get top blocked domains
- `check_status()` - Check Pi-hole status

### NetworkzeroGUI
Located in: `networkzero_gui.py`

**Methods:**
- `setup_ui()` - Create user interface
- `refresh_network_info()` - Update dashboard
- `do_ping()` - Execute ping
- `do_dns_lookup()` - Execute DNS lookup
- `toggle_monitoring()` - Start/stop monitoring
- Plus methods for Pi-hole integration

## Data Flow

### CLI Command Flow
```
User → run_cli.sh → networkzero_cli.py → network_monitor.py → Output
```

### GUI Interaction Flow
```
User → run_gui.sh → networkzero_gui.py → network_monitor.py → GUI Display
```

### Monitoring Flow
```
Start → Check Connectivity → Ping Host → Display Results → Wait (interval) → Loop
```

## Configuration Flow

1. User edits `config.ini`
2. Application reads configuration on startup
3. Settings applied to monitoring functions
4. User can override via GUI or CLI parameters

## Platform Support

### Windows
- Batch files (.bat) for setup and launching
- PowerShell compatible
- Tested on Windows 10/11

### Linux
- Shell scripts (.sh) for setup and launching
- Requires Python 3.8+
- Tested on Ubuntu 20.04+, Debian 10+

### macOS
- Shell scripts (.sh) for setup and launching
- Requires Python 3.8+
- Compatible with recent macOS versions

## Installation Workflow

```
1. Clone/Download repository
2. Run setup script (setup.bat or setup.sh)
3. Virtual environment created (venv/)
4. Dependencies installed
5. Ready to use!
```

## Usage Workflow

### GUI Usage
```
1. Run launcher (run_gui.bat/sh)
2. Application window opens
3. Navigate tabs for different functions
4. Click buttons to perform actions
5. View results in text areas
```

### CLI Usage
```
1. Open terminal/command prompt
2. Run launcher with command (run_cli.bat/sh dns google.com)
3. View output in terminal
4. Script exits after completion
```

## Extension Points

The application is designed to be extensible:

1. **New Monitoring Functions**: Add to `NetworkMonitor` class
2. **New CLI Commands**: Add subparser and handler in `networkzero_cli.py`
3. **New GUI Tabs**: Add tab creation in `networkzero_gui.py`
4. **New Integrations**: Create new monitor classes like `PiHoleMonitor`

## Best Practices

1. Always activate virtual environment before running
2. Use launcher scripts for convenience
3. Customize config.ini for your environment
4. Run tests after modifications
5. Check documentation for examples

---

*For support and updates, visit www.ionity.today*
