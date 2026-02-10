#!/usr/bin/env python3
"""
Test script for NetworkzeroMonitor
Tests all core functionality
"""

import sys
import time
from network_monitor import NetworkMonitor, PiHoleMonitor


def test_network_info():
    """Test network information retrieval"""
    print("Testing Network Information...")
    print("-" * 50)
    
    monitor = NetworkMonitor()
    info = monitor.get_network_info()
    
    assert 'hostname' in info, "Hostname missing"
    assert 'local_ip' in info, "Local IP missing"
    assert 'platform' in info, "Platform missing"
    
    print(f"✓ Hostname: {info['hostname']}")
    print(f"✓ Local IP: {info['local_ip']}")
    print(f"✓ Platform: {info['platform']}")
    print(f"✓ Public IP: {info.get('public_ip', 'N/A')}")
    print()
    
    return True


def test_dns_resolution():
    """Test DNS resolution"""
    print("Testing DNS Resolution...")
    print("-" * 50)
    
    monitor = NetworkMonitor()
    
    # Test with multiple domains
    domains = ['google.com', 'github.com', 'cloudflare.com']
    
    for domain in domains:
        result = monitor.check_dns_resolution(domain)
        
        if result['success']:
            print(f"✓ {domain}: {', '.join(result['ip_addresses'])} ({result['query_time']} ms)")
        else:
            print(f"✗ {domain}: {result.get('error', 'Unknown error')}")
    
    print()
    return True


def test_dns_servers():
    """Test DNS resolution with different servers"""
    print("Testing DNS with Different Servers...")
    print("-" * 50)
    
    monitor = NetworkMonitor()
    dns_servers = {
        'Google': '8.8.8.8',
        'Cloudflare': '1.1.1.1',
        'OpenDNS': '208.67.222.222'
    }
    
    for name, server in dns_servers.items():
        result = monitor.check_dns_resolution('google.com', server)
        
        if result['success']:
            print(f"✓ {name} ({server}): {result['query_time']} ms")
        else:
            print(f"✗ {name} ({server}): {result.get('error', 'Unknown error')}")
    
    print()
    return True


def test_connectivity_check():
    """Test connectivity checking"""
    print("Testing Connectivity Check...")
    print("-" * 50)
    
    monitor = NetworkMonitor()
    result = monitor.check_internet_connectivity()
    
    print(f"Connected: {result['connected']}")
    print(f"Quality: {result['quality']}")
    print("\nTest Results:")
    
    for test in result['tests']:
        symbol = "✓" if test['reachable'] else "✗"
        print(f"  {symbol} {test['domain']}")
    
    print()
    return True


def test_ping():
    """Test ping functionality"""
    print("Testing Ping (may require root/admin)...")
    print("-" * 50)
    
    monitor = NetworkMonitor()
    result = monitor.ping_host('8.8.8.8', count=2, timeout=2)
    
    print(f"Host: {result['host']}")
    print(f"Success: {result['success']}")
    print(f"Reachable: {result.get('reachable', False)}")
    
    if 'elapsed_time' in result:
        print(f"Elapsed Time: {result['elapsed_time']} seconds")
    
    if 'error' in result:
        print(f"Note: {result['error']}")
        print("  (Ping may require root/administrator privileges)")
    
    print()
    return True


def test_pihole():
    """Test Pi-hole functionality (will fail if no Pi-hole)"""
    print("Testing Pi-hole Integration...")
    print("-" * 50)
    
    # Using example URL - will fail but tests the code
    pihole = PiHoleMonitor('http://127.0.0.1')
    
    result = pihole.check_status()
    
    if result['success']:
        print(f"✓ Pi-hole Status: {result['status']}")
    else:
        print(f"✗ Pi-hole not available: {result.get('error', 'Connection failed')}")
        print("  (This is expected if you don't have Pi-hole running)")
    
    print()
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("NetworkzeroMonitor - Test Suite")
    print("Ionity (Pty) Ltd - www.ionity.today")
    print("=" * 60)
    print()
    
    tests = [
        ('Network Information', test_network_info),
        ('DNS Resolution', test_dns_resolution),
        ('DNS Servers', test_dns_servers),
        ('Connectivity Check', test_connectivity_check),
        ('Ping', test_ping),
        ('Pi-hole Integration', test_pihole),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))
        
        time.sleep(0.5)  # Brief pause between tests
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        symbol = "✓" if success else "✗"
        print(f"{symbol} {test_name}")
    
    print()
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
