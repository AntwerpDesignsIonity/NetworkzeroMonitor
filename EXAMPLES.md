# NetworkzeroMonitor - Examples

This file contains usage examples for NetworkzeroMonitor.

## CLI Examples

### Basic Network Status Check
```bash
# Check network information and connectivity
python networkzero_cli.py status

# Verbose output with details
python networkzero_cli.py status -v
```

### DNS Lookups
```bash
# Basic DNS lookup using system default DNS
python networkzero_cli.py dns google.com

# Lookup using specific DNS server (Google DNS)
python networkzero_cli.py dns github.com -s 8.8.8.8

# Lookup using Cloudflare DNS
python networkzero_cli.py dns example.com -s 1.1.1.1

# Lookup using OpenDNS
python networkzero_cli.py dns cloudflare.com -s 208.67.222.222
```

### Ping Tests
```bash
# Ping Google's DNS server (4 pings)
python networkzero_cli.py ping 8.8.8.8

# Ping with custom count
python networkzero_cli.py ping google.com -c 10

# Ping with custom timeout
python networkzero_cli.py ping github.com -c 5 -t 5

# Verbose ping output
python networkzero_cli.py ping cloudflare.com -v
```

### Continuous Monitoring
```bash
# Monitor Google DNS with 5-second intervals
python networkzero_cli.py monitor --host 8.8.8.8 --interval 5

# Monitor specific domain with 10-second intervals
python networkzero_cli.py monitor --host google.com --interval 10

# Monitor local gateway (example)
python networkzero_cli.py monitor --host 192.168.1.1 --interval 3
```

### Pi-hole Monitoring
```bash
# Check if Pi-hole is running
python networkzero_cli.py pihole status --url http://192.168.1.1

# Get Pi-hole statistics summary
python networkzero_cli.py pihole summary --url http://192.168.1.1

# Get top 10 blocked domains
python networkzero_cli.py pihole blocked --url http://192.168.1.1

# Get top 20 blocked domains
python networkzero_cli.py pihole blocked --url http://192.168.1.1 --count 20

# With API key for authenticated access
python networkzero_cli.py pihole summary --url http://192.168.1.1 --api-key YOUR_API_KEY
```

## Python API Examples

### Basic Network Monitoring
```python
from network_monitor import NetworkMonitor

# Create monitor instance
monitor = NetworkMonitor()

# Get network information
info = monitor.get_network_info()
print(f"Hostname: {info['hostname']}")
print(f"Local IP: {info['local_ip']}")
print(f"Public IP: {info['public_ip']}")

# Check connectivity
connectivity = monitor.check_internet_connectivity()
print(f"Connected: {connectivity['connected']}")
print(f"Quality: {connectivity['quality']}")

# Ping a host
result = monitor.ping_host('8.8.8.8', count=4)
print(f"Reachable: {result['reachable']}")

# DNS lookup
dns_result = monitor.check_dns_resolution('google.com')
print(f"IP Addresses: {dns_result['ip_addresses']}")
print(f"Query Time: {dns_result['query_time']} ms")

# DNS lookup with specific server
dns_result = monitor.check_dns_resolution('github.com', '1.1.1.1')
print(f"Resolved via {dns_result['dns_server']}")
```

### Pi-hole Integration
```python
from network_monitor import PiHoleMonitor

# Initialize Pi-hole monitor
pihole = PiHoleMonitor('http://192.168.1.1', api_key='your_api_key')

# Check status
status = pihole.check_status()
print(f"Pi-hole enabled: {status['enabled']}")

# Get summary statistics
summary = pihole.get_summary()
print(f"DNS queries today: {summary['dns_queries_today']}")
print(f"Ads blocked today: {summary['ads_blocked_today']}")
print(f"Blocking percentage: {summary['ads_percentage_today']}%")

# Get top blocked domains
blocked = pihole.get_top_blocked(count=10)
for domain, count in blocked['top_ads'].items():
    print(f"{domain}: {count} blocks")
```

### Continuous Monitoring Script
```python
import time
from network_monitor import NetworkMonitor

monitor = NetworkMonitor()

print("Starting continuous monitoring...")
try:
    while True:
        # Check connectivity
        connectivity = monitor.check_internet_connectivity()
        
        # Ping specific host
        ping_result = monitor.ping_host('8.8.8.8', count=1, timeout=2)
        
        # Display status
        timestamp = time.strftime('%H:%M:%S')
        status = "UP" if ping_result['reachable'] else "DOWN"
        quality = connectivity['quality']
        
        print(f"[{timestamp}] Status: {status} | Quality: {quality}")
        
        # Wait before next check
        time.sleep(5)
        
except KeyboardInterrupt:
    print("\nMonitoring stopped")
```

### Batch DNS Lookups
```python
from network_monitor import NetworkMonitor

monitor = NetworkMonitor()

domains = [
    'google.com',
    'github.com',
    'cloudflare.com',
    'stackoverflow.com',
    'reddit.com'
]

print("Domain Resolution Results:")
print("-" * 60)

for domain in domains:
    result = monitor.check_dns_resolution(domain)
    
    if result['success']:
        ips = ', '.join(result['ip_addresses'])
        print(f"{domain:30s} {ips:30s} {result['query_time']}ms")
    else:
        print(f"{domain:30s} ERROR: {result['error']}")
```

### Network Health Check
```python
from network_monitor import NetworkMonitor
import json

def network_health_check():
    """Comprehensive network health check"""
    monitor = NetworkMonitor()
    
    # Gather all information
    health = {
        'network_info': monitor.get_network_info(),
        'connectivity': monitor.check_internet_connectivity(),
        'dns_checks': {},
        'ping_checks': {}
    }
    
    # Test multiple DNS servers
    dns_servers = {
        'Google': '8.8.8.8',
        'Cloudflare': '1.1.1.1',
        'OpenDNS': '208.67.222.222'
    }
    
    for name, server in dns_servers.items():
        result = monitor.check_dns_resolution('google.com', server)
        health['dns_checks'][name] = {
            'success': result['success'],
            'query_time': result.get('query_time', 'N/A')
        }
    
    # Test connectivity to key hosts
    test_hosts = ['8.8.8.8', '1.1.1.1']
    
    for host in test_hosts:
        result = monitor.ping_host(host, count=2, timeout=2)
        health['ping_checks'][host] = {
            'reachable': result.get('reachable', False)
        }
    
    # Output as JSON
    print(json.dumps(health, indent=2))
    
    return health

# Run the health check
if __name__ == '__main__':
    network_health_check()
```

## Shell Script Examples

### Automated Network Monitoring (Bash)
```bash
#!/bin/bash
# monitor.sh - Automated network monitoring

source venv/bin/activate

LOG_FILE="network_monitor_$(date +%Y%m%d).log"

echo "Starting network monitoring... Logging to $LOG_FILE"

while true; do
    echo "=== $(date) ===" >> "$LOG_FILE"
    python networkzero_cli.py status >> "$LOG_FILE" 2>&1
    echo "" >> "$LOG_FILE"
    
    sleep 300  # Check every 5 minutes
done
```

### Batch Testing Script (Bash)
```bash
#!/bin/bash
# test_hosts.sh - Test connectivity to multiple hosts

source venv/bin/activate

HOSTS="google.com github.com cloudflare.com 8.8.8.8 1.1.1.1"

for HOST in $HOSTS; do
    echo "Testing $HOST..."
    python networkzero_cli.py ping "$HOST" -c 2
    echo ""
done
```

### Windows Batch Monitoring
```batch
@echo off
REM monitor.bat - Windows network monitoring

call venv\Scripts\activate.bat

set LOG_FILE=network_monitor_%DATE:~-4,4%%DATE:~-10,2%%DATE:~-7,2%.log

echo Starting network monitoring... Logging to %LOG_FILE%

:loop
echo === %DATE% %TIME% === >> %LOG_FILE%
python networkzero_cli.py status >> %LOG_FILE% 2>&1
echo. >> %LOG_FILE%

timeout /t 300 /nobreak
goto loop
```

## Integration Examples

### Cron Job (Linux)
```bash
# Add to crontab: crontab -e

# Check network status every hour
0 * * * * cd /path/to/NetworkzeroMonitor && source venv/bin/activate && python networkzero_cli.py status >> /var/log/network_monitor.log 2>&1

# Check Pi-hole stats every 30 minutes
*/30 * * * * cd /path/to/NetworkzeroMonitor && source venv/bin/activate && python networkzero_cli.py pihole summary --url http://192.168.1.1 >> /var/log/pihole_monitor.log 2>&1
```

### Systemd Service (Linux)
```ini
# /etc/systemd/system/networkzero-monitor.service

[Unit]
Description=NetworkzeroMonitor Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/NetworkzeroMonitor
ExecStart=/path/to/NetworkzeroMonitor/venv/bin/python networkzero_cli.py monitor --host 8.8.8.8 --interval 5
Restart=always

[Install]
WantedBy=multi-user.target
```

### Task Scheduler (Windows)
Create a scheduled task that runs:
```
Program: C:\Path\To\NetworkzeroMonitor\venv\Scripts\python.exe
Arguments: networkzero_cli.py status
Start in: C:\Path\To\NetworkzeroMonitor
```

---

*For more information, visit www.ionity.today*
