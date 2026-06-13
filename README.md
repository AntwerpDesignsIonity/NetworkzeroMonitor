# NetworkzeroMonitor

> **Ionity (Pty) Ltd** — [www.ionity.today](https://www.ionity.today)

A cross-platform, Python-based network monitoring tool with a full **GUI**, a rich **CLI**,
and an installable **mobile app (PWA)**. Monitor pings, DNS, active ports, interface traffic
and Pi-hole statistics — plus the *full network stack* from physical interfaces all the way up
to **cellular (2G–5G)**, **Wi-Fi**, **satellite internet (Starlink)** and **GNSS / satellite
positioning** — all from one place, including from your phone.

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

### 📱 Mobile app — extended network stack

A separate **mobile PWA** (served by the built-in API server) adds full-stack
visibility you can open on any phone:

| Layer | Source | Notes |
|---|---|---|
| Host / interfaces / IP / traffic | psutil | Same data as desktop |
| Internet connectivity & quality | ping | Live dashboard |
| **Cellular (2G/3G/4G/5G)** | ModemManager (`mmcli`) | Operator, generation, signal |
| **Wi-Fi link** | `nmcli` / `iw` | SSID, signal, band, rate |
| **Satellite internet (Starlink)** | Dish gRPC @ `192.168.100.1` | Latency, throughput, obstruction |
| **GNSS / satellite positioning** | `gpsd` | Fix, lat/lon, satellites in view (GPS/Galileo/GLONASS/BeiDou) |
| Ping / DNS / port tools | core engine | Interactive, on-device |

Each extended layer degrades gracefully: when the hardware or helper tool
isn't present, the app shows a clear "unavailable" state with the reason
instead of failing.

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

**📱 Mobile app (PWA):**
```bash
./run_mobile.sh       # Unix
run_mobile.bat        # Windows
```
Then, on your phone (connected to the same network), open the printed URL
(e.g. `http://192.168.1.50:8088`) in your browser and choose **"Add to Home
Screen"** to install it as an app. The server binds to `0.0.0.0:8088` by
default; override with `NZM_HOST` / `NZM_PORT` or the `[Mobile]` section of
`config.ini`.

---

## 📡 Mobile REST API

The mobile app is backed by a small Flask API (`api_server.py`). The same
endpoints can be consumed by any client:

| Endpoint | Description |
|---|---|
| `GET /api/overview` | Everything for the dashboard in one call |
| `GET /api/network` | Hostname, IPs, interfaces |
| `GET /api/connectivity` | Internet reachability & quality |
| `GET /api/traffic` | Per-interface traffic counters |
| `GET /api/ping?host=&count=` | Ping a host |
| `GET /api/dns?domain=&server=` | DNS lookup |
| `GET /api/ports?host=&ports=` | Port scan |
| `GET /api/pihole/<action>` | Pi-hole status / summary / blocked |
| `GET /api/extended/cellular` | Mobile broadband (2G–5G) |
| `GET /api/extended/wifi` | Wi-Fi link details |
| `GET /api/extended/satellite` | Satellite internet (Starlink) |
| `GET /api/extended/gnss` | GNSS / satellite positioning |
| `GET /api/extended/all` | Consolidated multi-layer snapshot |

### Optional helper tools (for full extended data)

These are auto-detected; install only the layers you need:

- **Cellular:** `ModemManager` (provides `mmcli`)
- **Wi-Fi:** `network-manager` (provides `nmcli`)
- **Satellite internet:** `grpcurl` (for live Starlink telemetry)
- **GNSS:** `gpsd` + a connected GNSS/GPS receiver

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
├── network_extended.py     # Extended layers: cellular, wifi, satellite, GNSS
├── networkzero_cli.py      # Command-line interface
├── networkzero_gui.py      # Graphical user interface (tkinter)
├── api_server.py           # Mobile REST API + PWA server (Flask)
├── mobile/                 # Installable mobile PWA front-end
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   ├── manifest.webmanifest
│   ├── service-worker.js
│   └── icon.svg
├── test_networkzero.py     # Unit + integration tests
├── config.ini              # Application configuration
├── requirements.txt        # Python dependencies
├── setup.sh / setup.bat    # Setup scripts
├── run_cli.sh / run_cli.bat
├── run_gui.sh / run_gui.bat
└── run_mobile.sh / run_mobile.bat
```

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

*NetworkzeroMonitor is a product of **Ionity (Pty) Ltd** — [www.ionity.today](https://www.ionity.today)*
