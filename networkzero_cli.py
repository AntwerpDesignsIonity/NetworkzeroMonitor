#!/usr/bin/env python3
"""
NetworkzeroMonitor - Command Line Interface
Ionity (Pty) Ltd - www.ionity.today

CLI for network monitoring and diagnostics
"""

import argparse
import sys
import json
from network_monitor import NetworkMonitor, PiHoleMonitor


def print_header():
    """Print application header"""
    print("=" * 60)
    print("NetworkzeroMonitor CLI")
    print("Ionity (Pty) Ltd - www.ionity.today")
    print("=" * 60)
    print()


def cmd_ping(args):
    """Execute ping command"""
    monitor = NetworkMonitor()
    result = monitor.ping_host(args.host, count=args.count, timeout=args.timeout)
    
    print(f"\nPing Results for {args.host}:")
    print("-" * 40)
    print(f"Success: {result['success']}")
    print(f"Reachable: {result.get('reachable', False)}")
    print(f"Elapsed Time: {result.get('elapsed_time', 'N/A')} seconds")
    print(f"Timestamp: {result['timestamp']}")
    
    if args.verbose and 'output' in result:
        print("\nDetailed Output:")
        print(result['output'])
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    
    return 0 if result['success'] else 1


def cmd_dns(args):
    """Execute DNS lookup command"""
    monitor = NetworkMonitor()
    result = monitor.check_dns_resolution(args.domain, args.server)
    
    print(f"\nDNS Resolution for {args.domain}:")
    print("-" * 40)
    print(f"Success: {result['success']}")
    print(f"DNS Server: {result['dns_server']}")
    
    if result['success']:
        print(f"IP Addresses: {', '.join(result['ip_addresses'])}")
        print(f"Query Time: {result['query_time']} ms")
    else:
        print(f"Error: {result.get('error')}")
    
    print(f"Timestamp: {result['timestamp']}")
    
    return 0 if result['success'] else 1


def cmd_status(args):
    """Check overall network status"""
    monitor = NetworkMonitor()
    
    print("\nNetwork Information:")
    print("-" * 40)
    info = monitor.get_network_info()
    for key, value in info.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print("\n\nInternet Connectivity:")
    print("-" * 40)
    connectivity = monitor.check_internet_connectivity()
    print(f"Connected: {connectivity['connected']}")
    print(f"Quality: {connectivity['quality']}")
    
    if args.verbose:
        print("\nConnectivity Tests:")
        for test in connectivity['tests']:
            status = "✓" if test['reachable'] else "✗"
            print(f"  {status} {test['domain']}")
    
    return 0 if connectivity['connected'] else 1


def cmd_pihole(args):
    """Check Pi-hole status and statistics"""
    if not args.url:
        print("Error: Pi-hole URL is required (use --url)")
        return 1
    
    pihole = PiHoleMonitor(args.url, args.api_key)
    
    if args.action == 'status':
        result = pihole.check_status()
        print(f"\nPi-hole Status ({args.url}):")
        print("-" * 40)
        
        if result['success']:
            print(f"Enabled: {result['enabled']}")
            print(f"Status: {result['status']}")
        else:
            print(f"Error: {result.get('error')}")
        
        print(f"Timestamp: {result['timestamp']}")
        
    elif args.action == 'summary':
        result = pihole.get_summary()
        print(f"\nPi-hole Summary ({args.url}):")
        print("-" * 40)
        
        if result['success']:
            print(f"DNS Queries Today: {result['dns_queries_today']:,}")
            print(f"Ads Blocked Today: {result['ads_blocked_today']:,}")
            print(f"Percentage Blocked: {result['ads_percentage_today']:.1f}%")
            print(f"Domains on Blocklist: {result['domains_being_blocked']:,}")
            print(f"Status: {result['status']}")
        else:
            print(f"Error: {result.get('error')}")
        
        print(f"Timestamp: {result['timestamp']}")
        
    elif args.action == 'blocked':
        result = pihole.get_top_blocked(count=args.count)
        print(f"\nTop {args.count} Blocked Domains ({args.url}):")
        print("-" * 40)
        
        if result['success']:
            for i, (domain, count) in enumerate(result['top_ads'].items(), 1):
                print(f"{i:2d}. {domain} ({count:,} blocks)")
        else:
            print(f"Error: {result.get('error')}")
        
        print(f"Timestamp: {result['timestamp']}")
    
    return 0 if result.get('success', False) else 1


def cmd_monitor(args):
    """Continuous monitoring mode"""
    import time
    
    monitor = NetworkMonitor()
    
    print("\nContinuous Network Monitoring")
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    try:
        while True:
            # Check connectivity
            connectivity = monitor.check_internet_connectivity()
            status_symbol = "✓" if connectivity['connected'] else "✗"
            
            # Ping primary host
            ping_result = monitor.ping_host(args.host, count=1, timeout=2)
            ping_symbol = "✓" if ping_result.get('reachable', False) else "✗"
            
            timestamp = time.strftime('%H:%M:%S')
            print(f"[{timestamp}] Internet: {status_symbol} {connectivity['quality']:15s} | {args.host}: {ping_symbol}")
            
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='NetworkzeroMonitor - Network Monitoring CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ping google.com
  %(prog)s dns github.com
  %(prog)s status
  %(prog)s pihole --url http://192.168.1.1 summary
  %(prog)s monitor --host 8.8.8.8 --interval 5
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Ping command
    ping_parser = subparsers.add_parser('ping', help='Ping a host')
    ping_parser.add_argument('host', help='Hostname or IP address to ping')
    ping_parser.add_argument('-c', '--count', type=int, default=4, help='Number of ping requests (default: 4)')
    ping_parser.add_argument('-t', '--timeout', type=int, default=2, help='Timeout in seconds (default: 2)')
    ping_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed output')
    
    # DNS command
    dns_parser = subparsers.add_parser('dns', help='DNS lookup')
    dns_parser.add_argument('domain', help='Domain name to resolve')
    dns_parser.add_argument('-s', '--server', help='DNS server to use')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check network status')
    status_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed information')
    
    # Pi-hole command
    pihole_parser = subparsers.add_parser('pihole', help='Pi-hole monitoring')
    pihole_parser.add_argument('action', choices=['status', 'summary', 'blocked'], help='Action to perform')
    pihole_parser.add_argument('--url', required=True, help='Pi-hole URL (e.g., http://192.168.1.1)')
    pihole_parser.add_argument('--api-key', help='Pi-hole API key for authenticated requests')
    pihole_parser.add_argument('--count', type=int, default=10, help='Number of blocked domains to show (default: 10)')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Continuous monitoring')
    monitor_parser.add_argument('--host', default='8.8.8.8', help='Host to monitor (default: 8.8.8.8)')
    monitor_parser.add_argument('--interval', type=int, default=5, help='Check interval in seconds (default: 5)')
    
    args = parser.parse_args()
    
    if not args.command:
        print_header()
        parser.print_help()
        return 1
    
    print_header()
    
    # Execute command
    commands = {
        'ping': cmd_ping,
        'dns': cmd_dns,
        'status': cmd_status,
        'pihole': cmd_pihole,
        'monitor': cmd_monitor,
    }
    
    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
