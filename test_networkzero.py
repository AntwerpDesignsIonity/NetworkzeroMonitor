#!/usr/bin/env python3
"""
NetworkzeroMonitor - Test Suite
Ionity (Pty) Ltd - www.ionity.today

Tests all core functionality without requiring external network access.
"""

import sys
import time
import unittest
from unittest.mock import MagicMock, patch

from network_monitor import NetworkMonitor, PiHoleMonitor


class TestNetworkMonitorInfo(unittest.TestCase):
    """Tests for get_network_info()"""

    def test_returns_hostname(self):
        monitor = NetworkMonitor()
        info = monitor.get_network_info()
        self.assertIn('hostname', info)
        self.assertIsInstance(info['hostname'], str)
        self.assertTrue(len(info['hostname']) > 0)

    def test_returns_local_ip(self):
        monitor = NetworkMonitor()
        info = monitor.get_network_info()
        self.assertIn('local_ip', info)

    def test_returns_platform(self):
        monitor = NetworkMonitor()
        info = monitor.get_network_info()
        self.assertIn('platform', info)

    def test_returns_interfaces(self):
        monitor = NetworkMonitor()
        info = monitor.get_network_info()
        self.assertIn('interfaces', info)
        self.assertIsInstance(info['interfaces'], dict)

    def test_returns_timestamp(self):
        monitor = NetworkMonitor()
        info = monitor.get_network_info()
        self.assertIn('timestamp', info)


class TestNetworkMonitorPing(unittest.TestCase):
    """Tests for ping_host()"""

    def test_ping_localhost(self):
        monitor = NetworkMonitor()
        result = monitor.ping_host('127.0.0.1', count=1, timeout=2)
        self.assertIn('host', result)
        self.assertEqual(result['host'], '127.0.0.1')
        self.assertIn('success', result)
        self.assertIn('timestamp', result)

    def test_ping_unknown_host_returns_failure(self):
        monitor = NetworkMonitor()
        # An invalid hostname should fail gracefully
        result = monitor.ping_host('this.host.does.not.exist.invalid', count=1, timeout=1)
        self.assertIn('success', result)
        self.assertIn('timestamp', result)

    def test_ping_result_has_elapsed_time(self):
        monitor = NetworkMonitor()
        result = monitor.ping_host('127.0.0.1', count=1, timeout=2)
        if result['success']:
            self.assertIn('elapsed_time', result)
            self.assertGreaterEqual(result['elapsed_time'], 0)

    def test_ping_reachable_key_present(self):
        monitor = NetworkMonitor()
        result = monitor.ping_host('127.0.0.1', count=1, timeout=2)
        self.assertIn('reachable', result)


class TestNetworkMonitorDNS(unittest.TestCase):
    """Tests for check_dns_resolution()"""

    def test_dns_result_structure(self):
        monitor = NetworkMonitor()
        result = monitor.check_dns_resolution('localhost')
        self.assertIn('domain', result)
        self.assertIn('success', result)
        self.assertIn('timestamp', result)

    def test_dns_failure_has_error(self):
        monitor = NetworkMonitor()
        result = monitor.check_dns_resolution('this.domain.does.not.exist.invalid')
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    @patch('network_monitor.DNS_AVAILABLE', False)
    def test_dns_fallback_socket(self):
        monitor = NetworkMonitor()
        result = monitor.check_dns_resolution('localhost')
        self.assertIn('success', result)


class TestNetworkMonitorTraffic(unittest.TestCase):
    """Tests for get_interface_traffic()"""

    def test_returns_dict(self):
        monitor = NetworkMonitor()
        traffic = monitor.get_interface_traffic()
        self.assertIsInstance(traffic, dict)

    def test_interface_has_required_keys(self):
        monitor = NetworkMonitor()
        traffic = monitor.get_interface_traffic()
        for iface, data in traffic.items():
            for key in ('bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv'):
                self.assertIn(key, data, f"Missing '{key}' for interface '{iface}'")


class TestNetworkMonitorPorts(unittest.TestCase):
    """Tests for get_open_ports()"""

    def test_loopback_port_scan(self):
        monitor = NetworkMonitor()
        result = monitor.get_open_ports(host='127.0.0.1', ports=[22, 80])
        self.assertIn('host', result)
        self.assertIn('ports', result)
        self.assertIn('timestamp', result)
        self.assertIn(22, result['ports'])
        self.assertIn(80, result['ports'])

    def test_port_values_are_bool(self):
        monitor = NetworkMonitor()
        result = monitor.get_open_ports(host='127.0.0.1', ports=[9999])
        for port, is_open in result['ports'].items():
            self.assertIsInstance(is_open, bool)


class TestNetworkMonitorConnectivity(unittest.TestCase):
    """Tests for check_internet_connectivity()"""

    def test_result_has_connected_key(self):
        monitor = NetworkMonitor()
        result = monitor.check_internet_connectivity()
        self.assertIn('connected', result)
        self.assertIsInstance(result['connected'], bool)

    def test_result_has_quality(self):
        monitor = NetworkMonitor()
        result = monitor.check_internet_connectivity()
        self.assertIn('quality', result)

    def test_result_has_tests(self):
        monitor = NetworkMonitor()
        result = monitor.check_internet_connectivity()
        self.assertIn('tests', result)
        self.assertIsInstance(result['tests'], list)


class TestPiHoleMonitor(unittest.TestCase):
    """Tests for PiHoleMonitor (mocked HTTP)"""

    def _make_pihole(self):
        return PiHoleMonitor('http://127.0.0.1', api_key=None)

    def test_check_status_returns_dict(self):
        pihole = self._make_pihole()
        result = pihole.check_status()
        self.assertIn('success', result)
        self.assertIn('timestamp', result)

    def test_check_status_failure_on_connection_error(self):
        pihole = self._make_pihole()
        result = pihole.check_status()
        # Pi-hole is not running locally so it should fail gracefully
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_get_summary_returns_dict(self):
        pihole = self._make_pihole()
        result = pihole.get_summary()
        self.assertIn('success', result)

    def test_get_top_blocked_returns_dict(self):
        pihole = self._make_pihole()
        result = pihole.get_top_blocked(count=5)
        self.assertIn('success', result)

    @patch('network_monitor.requests.get')
    def test_get_summary_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ads_blocked_today': 100,
            'dns_queries_today': 1000,
            'ads_percentage_today': 10.0,
            'domains_being_blocked': 5000,
            'status': 'enabled',
        }
        mock_get.return_value = mock_response

        pihole = PiHoleMonitor('http://192.168.1.1')
        result = pihole.get_summary()

        self.assertTrue(result['success'])
        self.assertEqual(result['ads_blocked_today'], 100)
        self.assertEqual(result['status'], 'enabled')

    @patch('network_monitor.requests.get')
    def test_check_status_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'enabled'}
        mock_get.return_value = mock_response

        pihole = PiHoleMonitor('http://192.168.1.1')
        result = pihole.check_status()

        self.assertTrue(result['success'])
        self.assertTrue(result['enabled'])
        self.assertEqual(result['status'], 'enabled')


def run_manual_demo():
    """Quick manual demo that prints results to stdout."""
    print("=" * 60)
    print("NetworkzeroMonitor - Manual Demo")
    print("Ionity (Pty) Ltd - www.ionity.today")
    print("=" * 60)

    monitor = NetworkMonitor()

    print("\n[1] Network Information")
    print("-" * 40)
    info = monitor.get_network_info()
    print(f"  Hostname : {info.get('hostname', 'N/A')}")
    print(f"  Local IP : {info.get('local_ip', 'N/A')}")
    print(f"  Platform : {info.get('platform', 'N/A')}")

    print("\n[2] Ping localhost")
    print("-" * 40)
    ping = monitor.ping_host('127.0.0.1', count=2)
    print(f"  Reachable: {ping.get('reachable', False)}")

    print("\n[3] DNS (localhost)")
    print("-" * 40)
    dns = monitor.check_dns_resolution('localhost')
    if dns['success']:
        print(f"  IPs: {', '.join(dns['ip_addresses'])}")
    else:
        print(f"  Error: {dns.get('error')}")

    print("\n[4] Interface Traffic")
    print("-" * 40)
    traffic = monitor.get_interface_traffic()
    for iface, data in list(traffic.items())[:3]:
        print(f"  {iface}: sent={data['bytes_sent']:,} B, recv={data['bytes_recv']:,} B")

    print("\n[5] Port Scan (127.0.0.1, ports 22/80/443)")
    print("-" * 40)
    ports = monitor.get_open_ports('127.0.0.1', ports=[22, 80, 443])
    for p, is_open in sorted(ports['ports'].items()):
        print(f"  Port {p}: {'OPEN' if is_open else 'closed'}")

    print("\n[6] Pi-hole (localhost — expected to fail)")
    print("-" * 40)
    pihole = PiHoleMonitor('http://127.0.0.1')
    result = pihole.check_status()
    print(f"  Success: {result['success']}")
    if not result['success']:
        print(f"  (Expected) Error: {result.get('error')}")


if __name__ == '__main__':
    if '--demo' in sys.argv:
        run_manual_demo()
    else:
        unittest.main(verbosity=2)
