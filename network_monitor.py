"""
NetworkzeroMonitor - Core Network Monitoring Module
Ionity (Pty) Ltd - www.ionity.today

This module provides core network monitoring functionality including:
- Ping monitoring
- DNS resolution checks
- Network connectivity tests
- Pi-hole integration
"""

import socket
import subprocess
import platform
import time
from typing import Dict, List, Optional, Tuple
import dns.resolver
import requests


class NetworkMonitor:
    """Core network monitoring class"""
    
    def __init__(self):
        self.dns_servers = ['8.8.8.8', '1.1.1.1', '208.67.222.222']  # Google, Cloudflare, OpenDNS
        self.test_domains = ['google.com', 'cloudflare.com', 'github.com']
        
    def ping_host(self, host: str, count: int = 4, timeout: int = 2) -> Dict:
        """
        Ping a host and return statistics
        
        Args:
            host: Hostname or IP address to ping
            count: Number of ping requests
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with ping results
        """
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
        
        command = ['ping', param, str(count), timeout_param, str(timeout * 1000 if platform.system().lower() == 'windows' else timeout), host]
        
        try:
            start_time = time.time()
            output = subprocess.run(command, capture_output=True, text=True, timeout=timeout * count + 5)
            elapsed = time.time() - start_time
            
            success = output.returncode == 0
            
            # Parse output for statistics
            result = {
                'host': host,
                'success': success,
                'output': output.stdout if success else output.stderr,
                'elapsed_time': round(elapsed, 2),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Try to extract packet loss and RTT
            if success:
                lines = output.stdout.lower()
                if 'packet loss' in lines or 'received' in lines:
                    result['reachable'] = True
                else:
                    result['reachable'] = False
            else:
                result['reachable'] = False
                
            return result
            
        except subprocess.TimeoutExpired:
            return {
                'host': host,
                'success': False,
                'reachable': False,
                'error': 'Timeout',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {
                'host': host,
                'success': False,
                'reachable': False,
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def check_dns_resolution(self, domain: str, dns_server: Optional[str] = None) -> Dict:
        """
        Check DNS resolution for a domain
        
        Args:
            domain: Domain name to resolve
            dns_server: Optional DNS server to use
            
        Returns:
            Dictionary with DNS resolution results
        """
        resolver = dns.resolver.Resolver()
        
        if dns_server:
            resolver.nameservers = [dns_server]
        
        try:
            start_time = time.time()
            answers = resolver.resolve(domain, 'A')
            elapsed = time.time() - start_time
            
            ip_addresses = [str(rdata) for rdata in answers]
            
            return {
                'domain': domain,
                'success': True,
                'ip_addresses': ip_addresses,
                'dns_server': dns_server or 'system default',
                'query_time': round(elapsed * 1000, 2),  # in milliseconds
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'domain': domain,
                'success': False,
                'error': str(e),
                'dns_server': dns_server or 'system default',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def check_internet_connectivity(self) -> Dict:
        """
        Check overall internet connectivity
        
        Returns:
            Dictionary with connectivity status
        """
        results = []
        
        for domain in self.test_domains:
            result = self.ping_host(domain, count=1, timeout=2)
            results.append({
                'domain': domain,
                'reachable': result.get('reachable', False)
            })
        
        successful = sum(1 for r in results if r['reachable'])
        
        return {
            'connected': successful > 0,
            'quality': 'Good' if successful >= 2 else 'Poor' if successful == 1 else 'No Connection',
            'tests': results,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_network_info(self) -> Dict:
        """
        Get local network information
        
        Returns:
            Dictionary with network information
        """
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Try to get public IP
            public_ip = None
            try:
                response = requests.get('https://api.ipify.org?format=json', timeout=5)
                if response.status_code == 200:
                    public_ip = response.json().get('ip')
            except:
                pass
            
            return {
                'hostname': hostname,
                'local_ip': local_ip,
                'public_ip': public_ip,
                'platform': platform.system(),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }


class PiHoleMonitor:
    """Pi-hole monitoring integration"""
    
    def __init__(self, pihole_url: str, api_key: Optional[str] = None):
        """
        Initialize Pi-hole monitor
        
        Args:
            pihole_url: URL of Pi-hole instance (e.g., http://192.168.1.1)
            api_key: Optional API key for authenticated requests
        """
        self.pihole_url = pihole_url.rstrip('/')
        self.api_key = api_key
    
    def get_summary(self) -> Dict:
        """
        Get Pi-hole summary statistics
        
        Returns:
            Dictionary with Pi-hole stats
        """
        try:
            url = f"{self.pihole_url}/admin/api.php?summary"
            if self.api_key:
                url += f"&auth={self.api_key}"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'ads_blocked_today': data.get('ads_blocked_today', 0),
                    'dns_queries_today': data.get('dns_queries_today', 0),
                    'ads_percentage_today': data.get('ads_percentage_today', 0),
                    'domains_being_blocked': data.get('domains_being_blocked', 0),
                    'status': data.get('status', 'unknown'),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def get_top_blocked(self, count: int = 10) -> Dict:
        """
        Get top blocked domains
        
        Args:
            count: Number of top domains to return
            
        Returns:
            Dictionary with top blocked domains
        """
        try:
            url = f"{self.pihole_url}/admin/api.php?topItems={count}"
            if self.api_key:
                url += f"&auth={self.api_key}"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'top_ads': data.get('top_ads', {}),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def check_status(self) -> Dict:
        """
        Check Pi-hole status
        
        Returns:
            Dictionary with Pi-hole status
        """
        try:
            url = f"{self.pihole_url}/admin/api.php?status"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'enabled': data.get('status') == 'enabled',
                    'status': data.get('status', 'unknown'),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }


if __name__ == '__main__':
    # Simple test
    monitor = NetworkMonitor()
    print("Network Monitor Test")
    print("=" * 50)
    
    print("\nNetwork Info:")
    info = monitor.get_network_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\nPing Test (google.com):")
    result = monitor.ping_host('google.com', count=2)
    print(f"  Success: {result['success']}")
    print(f"  Reachable: {result.get('reachable', False)}")
    
    print("\nDNS Resolution Test (github.com):")
    dns_result = monitor.check_dns_resolution('github.com')
    if dns_result['success']:
        print(f"  IP Addresses: {', '.join(dns_result['ip_addresses'])}")
        print(f"  Query Time: {dns_result['query_time']} ms")
    else:
        print(f"  Error: {dns_result.get('error')}")
