"""
NetworkzeroMonitor - Core Network Monitoring Module
Ionity (Pty) Ltd - www.ionity.today

This module provides core network monitoring functionality including:
- Ping monitoring
- DNS resolution checks
- Network connectivity tests
- Network interface statistics (via psutil)
- Pi-hole integration
"""

import socket
import subprocess
import platform
import time
import configparser
import os
from typing import Dict, List, Optional
import psutil
import requests

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

# Load configuration
_config = configparser.ConfigParser()
_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
if os.path.exists(_config_path):
    _config.read(_config_path)


class NetworkMonitor:
    """Core network monitoring class"""

    def __init__(self):
        self.dns_servers = ['8.8.8.8', '1.1.1.1', '208.67.222.222']  # Google, Cloudflare, OpenDNS
        self.test_domains = ['google.com', 'cloudflare.com', 'github.com']

        # Override defaults from config if available
        if _config.has_option('Network', 'dns_servers'):
            self.dns_servers = [s.strip() for s in _config.get('Network', 'dns_servers').split(',')]
        if _config.has_option('Network', 'test_domains'):
            self.test_domains = [d.strip() for d in _config.get('Network', 'test_domains').split(',')]

    def ping_host(self, host: str, count: int = 4, timeout: int = 2) -> Dict:
        """
        Ping a host and return statistics.

        Args:
            host: Hostname or IP address to ping
            count: Number of ping requests
            timeout: Timeout in seconds

        Returns:
            Dictionary with ping results
        """
        system = platform.system().lower()
        if system == 'windows':
            param = '-n'
            timeout_param = '-w'
            timeout_val = str(timeout * 1000)
        else:
            param = '-c'
            timeout_param = '-W'
            timeout_val = str(timeout)

        command = ['ping', param, str(count), timeout_param, timeout_val, host]

        try:
            start_time = time.time()
            output = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout * count + 5
            )
            elapsed = time.time() - start_time

            success = output.returncode == 0
            stdout = output.stdout if success else (output.stdout + output.stderr)

            result = {
                'host': host,
                'success': success,
                'output': stdout,
                'elapsed_time': round(elapsed, 2),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }

            if success:
                lines_lower = stdout.lower()
                result['reachable'] = (
                    'packet loss' in lines_lower or
                    'received' in lines_lower or
                    'bytes from' in lines_lower
                )
            else:
                result['reachable'] = False

            # Parse min/avg/max RTT where possible
            for line in stdout.splitlines():
                line_l = line.lower()
                if 'min/avg/max' in line_l or 'minimum' in line_l:
                    result['rtt_line'] = line.strip()
                    break

            return result

        except subprocess.TimeoutExpired:
            return {
                'host': host,
                'success': False,
                'reachable': False,
                'error': 'Timeout',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
        except FileNotFoundError:
            return {
                'host': host,
                'success': False,
                'reachable': False,
                'error': 'ping command not found',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
        except Exception as exc:
            return {
                'host': host,
                'success': False,
                'reachable': False,
                'error': str(exc),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }

    def check_dns_resolution(self, domain: str, dns_server: Optional[str] = None) -> Dict:
        """
        Check DNS resolution for a domain.

        Args:
            domain: Domain name to resolve
            dns_server: Optional DNS server to use

        Returns:
            Dictionary with DNS resolution results
        """
        if DNS_AVAILABLE:
            return self._dns_via_dnspython(domain, dns_server)
        else:
            return self._dns_via_socket(domain)

    def _dns_via_dnspython(self, domain: str, dns_server: Optional[str]) -> Dict:
        """DNS resolution using dnspython."""
        import dns.resolver  # noqa: PLC0415

        resolver = dns.resolver.Resolver()
        if dns_server:
            resolver.nameservers = [dns_server]

        try:
            start_time = time.time()
            answers = resolver.resolve(domain, 'A')
            elapsed = time.time() - start_time

            return {
                'domain': domain,
                'success': True,
                'ip_addresses': [str(r) for r in answers],
                'dns_server': dns_server or 'system default',
                'query_time': round(elapsed * 1000, 2),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
        except Exception as exc:
            return {
                'domain': domain,
                'success': False,
                'error': str(exc),
                'dns_server': dns_server or 'system default',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }

    def _dns_via_socket(self, domain: str) -> Dict:
        """Fallback DNS resolution using the system socket library."""
        try:
            start_time = time.time()
            results = socket.getaddrinfo(domain, None)
            elapsed = time.time() - start_time
            ips = list({r[4][0] for r in results})
            return {
                'domain': domain,
                'success': True,
                'ip_addresses': ips,
                'dns_server': 'system default',
                'query_time': round(elapsed * 1000, 2),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
        except Exception as exc:
            return {
                'domain': domain,
                'success': False,
                'error': str(exc),
                'dns_server': 'system default',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }

    def check_internet_connectivity(self) -> Dict:
        """
        Check overall internet connectivity by pinging test domains.

        Returns:
            Dictionary with connectivity status
        """
        results = []
        for domain in self.test_domains:
            result = self.ping_host(domain, count=1, timeout=2)
            results.append({
                'domain': domain,
                'reachable': result.get('reachable', False),
            })

        successful = sum(1 for r in results if r['reachable'])
        total = len(results)

        if successful == 0:
            quality = 'No Connection'
        elif successful < total:
            quality = 'Degraded'
        else:
            quality = 'Excellent'

        return {
            'connected': successful > 0,
            'quality': quality,
            'tests': results,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def get_network_info(self) -> Dict:
        """
        Get local network information including interface stats.

        Returns:
            Dictionary with network information
        """
        try:
            hostname = socket.gethostname()
            try:
                local_ip = socket.gethostbyname(hostname)
            except Exception:
                local_ip = '127.0.0.1'

            # Collect interface statistics via psutil
            interfaces = {}
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            net_io = psutil.net_io_counters(pernic=True)

            for iface, addrs in net_if_addrs.items():
                ipv4 = [a.address for a in addrs if a.family == socket.AF_INET]
                stats = net_if_stats.get(iface)
                io = net_io.get(iface)
                interfaces[iface] = {
                    'ipv4': ipv4,
                    'is_up': stats.isup if stats else False,
                    'speed_mbps': stats.speed if stats else 0,
                    'bytes_sent': io.bytes_sent if io else 0,
                    'bytes_recv': io.bytes_recv if io else 0,
                }

            # Try to get public IP
            public_ip = None
            try:
                response = requests.get('https://api.ipify.org?format=json', timeout=5)
                if response.status_code == 200:
                    public_ip = response.json().get('ip')
            except Exception:
                pass

            return {
                'hostname': hostname,
                'local_ip': local_ip,
                'public_ip': public_ip or 'Unavailable',
                'platform': platform.system(),
                'platform_version': platform.version(),
                'interfaces': interfaces,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }

        except Exception as exc:
            return {
                'error': str(exc),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }

    def get_interface_traffic(self) -> Dict:
        """
        Get current per-interface traffic counters.

        Returns:
            Dictionary mapping interface name to traffic stats
        """
        counters = psutil.net_io_counters(pernic=True)
        result = {}
        for iface, io in counters.items():
            result[iface] = {
                'bytes_sent': io.bytes_sent,
                'bytes_recv': io.bytes_recv,
                'packets_sent': io.packets_sent,
                'packets_recv': io.packets_recv,
                'errin': io.errin,
                'errout': io.errout,
                'dropin': io.dropin,
                'dropout': io.dropout,
            }
        return result

    def get_open_ports(self, host: str = '127.0.0.1', ports: Optional[List[int]] = None) -> Dict:
        """
        Check which of the given ports are open on host.

        Args:
            host: Host to scan
            ports: List of port numbers to check (defaults to common ports)

        Returns:
            Dictionary mapping port -> open (bool)
        """
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 5432, 8080, 8443]

        results = {}
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                connected = sock.connect_ex((host, port)) == 0
                sock.close()
                results[port] = connected
            except Exception:
                results[port] = False

        return {
            'host': host,
            'ports': results,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        }


class PiHoleMonitor:
    """Pi-hole monitoring integration"""

    def __init__(self, pihole_url: str, api_key: Optional[str] = None):
        """
        Initialize Pi-hole monitor.

        Args:
            pihole_url: URL of Pi-hole instance (e.g., http://192.168.1.1)
            api_key: Optional API key for authenticated requests
        """
        self.pihole_url = pihole_url.rstrip('/')
        self.api_key = api_key

    @staticmethod
    def _sanitize_error(exc: Exception) -> str:
        """Return an error string with any auth token value redacted."""
        import re
        return re.sub(r'(auth=)[^&\s\'"]+', r'\1[REDACTED]', str(exc))

    def _api_get(self, params: str) -> Dict:
        """Helper to call the Pi-hole admin API."""
        base_url = f"{self.pihole_url}/admin/api.php?{params}"
        if self.api_key:
            base_url += "&auth="
        # Build final URL separately so the key value isn't in exception context
        request_url = (base_url + self.api_key) if self.api_key else base_url
        response = requests.get(request_url, timeout=5)
        response.raise_for_status()
        return response.json()

    def get_summary(self) -> Dict:
        """
        Get Pi-hole summary statistics.

        Returns:
            Dictionary with Pi-hole stats
        """
        try:
            data = self._api_get('summary')
            return {
                'success': True,
                'ads_blocked_today': data.get('ads_blocked_today', 0),
                'dns_queries_today': data.get('dns_queries_today', 0),
                'ads_percentage_today': data.get('ads_percentage_today', 0),
                'domains_being_blocked': data.get('domains_being_blocked', 0),
                'status': data.get('status', 'unknown'),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
        except Exception as exc:
            return {
                'success': False,
                'error': self._sanitize_error(exc),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }

    def get_top_blocked(self, count: int = 10) -> Dict:
        """
        Get top blocked domains.

        Args:
            count: Number of top domains to return

        Returns:
            Dictionary with top blocked domains
        """
        try:
            data = self._api_get(f'topItems={count}')
            return {
                'success': True,
                'top_ads': data.get('top_ads', {}),
                'top_queries': data.get('top_queries', {}),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
        except Exception as exc:
            return {
                'success': False,
                'error': self._sanitize_error(exc),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }

    def check_status(self) -> Dict:
        """
        Check Pi-hole enabled/disabled status.

        Returns:
            Dictionary with Pi-hole status
        """
        try:
            data = self._api_get('status')
            return {
                'success': True,
                'enabled': data.get('status') == 'enabled',
                'status': data.get('status', 'unknown'),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
        except Exception as exc:
            return {
                'success': False,
                'error': self._sanitize_error(exc),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
    monitor = NetworkMonitor()
    print("NetworkzeroMonitor - Core Module Test")
    print("Ionity (Pty) Ltd - www.ionity.today")
    print("=" * 50)

    print("\nNetwork Info:")
    info = monitor.get_network_info()
    print(f"  Hostname : {info.get('hostname', 'N/A')}")
    print(f"  Local IP : {info.get('local_ip', 'N/A')}")
    print(f"  Platform : {info.get('platform', 'N/A')}")

    print("\nPing Test (localhost):")
    result = monitor.ping_host('127.0.0.1', count=2)
    print(f"  Reachable: {result.get('reachable', False)}")
