# NetworkzeroMonitor

> **Ionity (Pty) Ltd** — [www.ionity.today](https://www.ionity.today)

A cross-platform, Python-based network monitoring tool with a full **GUI** and a rich **CLI**.
Monitor pings, DNS, active ports, interface traffic and Pi-hole statistics — all from one place.

---

## ✨ Features

| Feature | CLI | GUI |
|---|---|---|
| Ping host (with RTT stats) | ✓ | ✓ |
| DNS resolution (custom DNS server) | ✓ | ✓ |
| DNS comparison across all servers | — | ✓ |
| Network information (hostname, IP, interfaces) | ✓ | ✓ |
| Internet connectivity quality check | ✓ | ✓ |
| Port scanner | ✓ | ✓ |
| Interface traffic counters | ✓ | ✓ |
| Pi-hole status / summary / top blocked | ✓ | ✓ |
| Live continuous monitoring | ✓ | ✓ |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- `pip` (bundled with Python)
- `tkinter` (for GUI — pre-installed on most systems; on Ubuntu: `sudo apt install python3-tk`)

### 1. Clone or download the repository

```bash
git clone https://github.com/AntwerpDesignsIonity/NetworkzeroMonitor.git
cd NetworkzeroMonitor
```

### 2. Run setup (creates a virtual environment and installs dependencies)

**Unix / Linux / macOS:**
```bash
chmod +x setup.sh run_cli.sh run_gui.sh
./setup.sh
```

**Windows:**
```bat
setup.bat
```

### 3. Launch

**GUI:**
```bash
./run_gui.sh          # Unix
run_gui.bat           # Windows
```

**CLI:**
```bash
./run_cli.sh --help   # Unix
run_cli.bat --help    # Windows
```

---

## 📟 CLI Reference

```
networkzero_cli.py <command> [options]
```

| Command | Description |
|---|---|
| `ping <host>` | Ping a host |
| `dns <domain>` | DNS lookup (optionally via a specific server) |
| `status` | Show network info and connectivity |
| `ports` | Scan common ports on a host |
| `traffic` | Show interface traffic counters |
| `pihole <action>` | Pi-hole status / summary / top blocked |
| `monitor` | Continuous live monitoring |

### Examples

```bash
# Ping with 10 packets
./run_cli.sh ping 8.8.8.8 -c 10

# DNS lookup using Cloudflare
./run_cli.sh dns github.com -s 1.1.1.1

# Verbose network status
./run_cli.sh status -v

# Scan specific ports
./run_cli.sh ports --host 192.168.1.1 --ports 22 80 443

# Show interface traffic
./run_cli.sh traffic

# Pi-hole summary
./run_cli.sh pihole summary --url http://192.168.1.1 --api-key YOUR_KEY

# Continuous monitoring every 3 seconds
./run_cli.sh monitor --host 8.8.8.8 --interval 3
```

---

## 🖥️ GUI Overview

The GUI is organised into seven tabs:

1. **📊 Dashboard** — hostname, IP addresses, interfaces, connectivity quality
2. **🏓 Ping** — interactive ping with RTT display
3. **🌐 DNS Lookup** — single lookup or compare across all configured DNS servers
4. **🕳 Pi-hole** — status, daily statistics, top blocked domains
5. **📡 Live Monitor** — scrolling live log of connectivity and ping results
6. **🔍 Port Scanner** — scan a host for open/closed ports
7. **📶 Traffic** — per-interface traffic counters (bytes sent/received, errors)

---

## ⚙️ Configuration

Edit `config.ini` to change defaults:

```ini
[Network]
default_ping_host = 8.8.8.8
test_domains = google.com,cloudflare.com,github.com
dns_servers = 8.8.8.8,1.1.1.1,208.67.222.222
monitor_interval = 5
ping_count = 4
ping_timeout = 2

[PiHole]
# url = http://192.168.1.1
# api_key = your_api_key_here

[UI]
window_width = 1024
window_height = 720
theme = clam
```

---

## 🧪 Running Tests

```bash
# Activate the virtual environment first
source venv/bin/activate       # Unix
venv\Scripts\activate.bat      # Windows

# Run unit tests
python test_networkzero.py

# Or run the manual demo
python test_networkzero.py --demo
```

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `dnspython` | DNS resolution with custom servers |
| `psutil` | Interface statistics and traffic counters |
| `requests` | Public IP lookup, Pi-hole API |
| `matplotlib` | (optional) Future chart support |

---

## 📁 Project Structure

```
NetworkzeroMonitor/
├── network_monitor.py      # Core monitoring engine
├── networkzero_cli.py      # Command-line interface
├── networkzero_gui.py      # Graphical user interface (tkinter)
├── test_networkzero.py     # Unit + integration tests
├── config.ini              # Application configuration
├── requirements.txt        # Python dependencies
├── setup.sh                # Unix setup script
├── setup.bat               # Windows setup script
├── run_cli.sh / run_cli.bat
└── run_gui.sh / run_gui.bat
```

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

*NetworkzeroMonitor is a product of **Ionity (Pty) Ltd** — [www.ionity.today](https://www.ionity.today)*
