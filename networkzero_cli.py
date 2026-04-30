#!/usr/bin/env python3
"""
NetworkzeroMonitor - Command Line Interface
Ionity (Pty) Ltd - www.ionity.today

CLI for network monitoring and diagnostics.

Usage:
    networkzero_cli.py ping <host> [-c COUNT] [-t TIMEOUT] [-v]
    networkzero_cli.py dns <domain> [-s SERVER]
    networkzero_cli.py status [-v]
    networkzero_cli.py ports [--host HOST] [--ports PORT [PORT ...]]
    networkzero_cli.py traffic
    networkzero_cli.py pihole <action> --url URL [--api-key KEY] [--count N]
    networkzero_cli.py monitor [--host HOST] [--interval SEC]
"""

import argparse
import sys
import time

from network_monitor import NetworkMonitor, PiHoleMonitor


BANNER = """
╔══════════════════════════════════════════════════════════╗
║          NetworkzeroMonitor  ·  Ionity (Pty) Ltd         ║
║                   www.ionity.today                       ║
╚══════════════════════════════════════════════════════════╝
"""


def print_header():
    print(BANNER)


def _bytes_human(n: int) -> str:
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_ping(args) -> int:
    monitor = NetworkMonitor()
    result = monitor.ping_host(args.host, count=args.count, timeout=args.timeout)

    print(f"\nPing Results for {args.host}")
    print("-" * 44)
    print(f"  Reachable    : {result.get('reachable', False)}")
    print(f"  Elapsed Time : {result.get('elapsed_time', 'N/A')} s")
    if 'rtt_line' in result:
        print(f"  RTT          : {result['rtt_line']}")
    print(f"  Timestamp    : {result['timestamp']}")

    if args.verbose and 'output' in result:
        print("\nRaw Output:")
        print(result['output'])

    if 'error' in result:
        print(f"  Error        : {result['error']}")

    return 0 if result.get('reachable', False) else 1


def cmd_dns(args) -> int:
    monitor = NetworkMonitor()
    result = monitor.check_dns_resolution(args.domain, args.server)

    print(f"\nDNS Resolution for {args.domain}")
    print("-" * 44)
    print(f"  DNS Server : {result['dns_server']}")

    if result['success']:
        print(f"  IP Addresses: {', '.join(result['ip_addresses'])}")
        print(f"  Query Time  : {result['query_time']} ms")
    else:
        print(f"  Error       : {result.get('error')}")

    print(f"  Timestamp   : {result['timestamp']}")
    return 0 if result['success'] else 1


def cmd_status(args) -> int:
    monitor = NetworkMonitor()

    print("\nNetwork Information")
    print("-" * 44)
    info = monitor.get_network_info()
    print(f"  Hostname        : {info.get('hostname', 'N/A')}")
    print(f"  Local IP        : {info.get('local_ip', 'N/A')}")
    print(f"  Public IP       : {info.get('public_ip', 'N/A')}")
    print(f"  Platform        : {info.get('platform', 'N/A')}")

    if args.verbose:
        ifaces = info.get('interfaces', {})
        if ifaces:
            print("\n  Network Interfaces:")
            for iface, data in ifaces.items():
                status = "UP" if data['is_up'] else "down"
                ips = ', '.join(data['ipv4']) if data['ipv4'] else 'no IPv4'
                print(f"    {iface:<20} {status:<6} {ips}")

    print("\nInternet Connectivity")
    print("-" * 44)
    connectivity = monitor.check_internet_connectivity()
    print(f"  Connected : {connectivity['connected']}")
    print(f"  Quality   : {connectivity['quality']}")

    if args.verbose:
        for test in connectivity['tests']:
            symbol = "✓" if test['reachable'] else "✗"
            print(f"    {symbol} {test['domain']}")

    return 0 if connectivity['connected'] else 1


def cmd_ports(args) -> int:
    monitor = NetworkMonitor()
    ports = args.ports if args.ports else None
    result = monitor.get_open_ports(host=args.host, ports=ports)

    print(f"\nPort Scan: {result['host']}")
    print("-" * 44)
    for port, is_open in sorted(result['ports'].items()):
        state = "OPEN" if is_open else "closed"
        print(f"  Port {port:<6}: {state}")
    print(f"\n  Timestamp: {result['timestamp']}")
    return 0


def cmd_traffic(args) -> int:  # noqa: ARG001
    monitor = NetworkMonitor()
    traffic = monitor.get_interface_traffic()

    print("\nNetwork Interface Traffic")
    print("-" * 60)
    print(f"  {'Interface':<20} {'Sent':>12} {'Received':>12} {'Err In':>8} {'Err Out':>8}")
    print("  " + "-" * 56)
    for iface, data in traffic.items():
        print(
            f"  {iface:<20} "
            f"{_bytes_human(data['bytes_sent']):>12} "
            f"{_bytes_human(data['bytes_recv']):>12} "
            f"{data['errin']:>8} "
            f"{data['errout']:>8}"
        )
    return 0


def cmd_pihole(args) -> int:
    pihole = PiHoleMonitor(args.url, getattr(args, 'api_key', None))

    if args.action == 'status':
        result = pihole.check_status()
        print(f"\nPi-hole Status ({args.url})")
        print("-" * 44)
        if result['success']:
            print(f"  Status  : {result['status']}")
            print(f"  Enabled : {result['enabled']}")
        else:
            print(f"  Error   : {result.get('error')}")

    elif args.action == 'summary':
        result = pihole.get_summary()
        print(f"\nPi-hole Summary ({args.url})")
        print("-" * 44)
        if result['success']:
            print(f"  DNS Queries Today    : {result['dns_queries_today']:,}")
            print(f"  Ads Blocked Today    : {result['ads_blocked_today']:,}")
            print(f"  Percentage Blocked   : {result['ads_percentage_today']:.1f}%")
            print(f"  Domains on Blocklist : {result['domains_being_blocked']:,}")
            print(f"  Status               : {result['status']}")
        else:
            print(f"  Error : {result.get('error')}")

    elif args.action == 'blocked':
        count = getattr(args, 'count', 10)
        result = pihole.get_top_blocked(count=count)
        print(f"\nTop {count} Blocked Domains ({args.url})")
        print("-" * 44)
        if result['success']:
            for i, (domain, hits) in enumerate(result['top_ads'].items(), 1):
                print(f"  {i:2d}. {domain:<40} {hits:,} blocks")
        else:
            print(f"  Error : {result.get('error')}")
    else:
        result = {'success': False}

    print(f"\n  Timestamp: {result['timestamp']}")
    return 0 if result.get('success', False) else 1


def cmd_monitor(args) -> int:
    monitor = NetworkMonitor()

    print(f"\nContinuous Network Monitoring  (host: {args.host}, interval: {args.interval}s)")
    print("Press Ctrl+C to stop")
    print("-" * 60)

    try:
        while True:
            connectivity = monitor.check_internet_connectivity()
            ping_result = monitor.ping_host(args.host, count=1, timeout=2)

            net_sym = "✓" if connectivity['connected'] else "✗"
            ping_sym = "✓" if ping_result.get('reachable', False) else "✗"
            ts = time.strftime('%H:%M:%S')

            print(
                f"[{ts}] Internet: {net_sym} {connectivity['quality']:<12} | "
                f"{args.host}: {ping_sym}"
            )
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

    return 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='networkzero_cli',
        description='NetworkzeroMonitor CLI — Ionity (Pty) Ltd · www.ionity.today',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ping 8.8.8.8
  %(prog)s dns github.com -s 8.8.8.8
  %(prog)s status -v
  %(prog)s ports --host 127.0.0.1 --ports 22 80 443
  %(prog)s traffic
  %(prog)s pihole status --url http://192.168.1.1
  %(prog)s pihole summary --url http://192.168.1.1 --api-key YOUR_KEY
  %(prog)s pihole blocked --url http://192.168.1.1 --count 20
  %(prog)s monitor --host 8.8.8.8 --interval 5
        """,
    )

    sub = parser.add_subparsers(dest='command', metavar='COMMAND', help='Available commands')

    # --- ping ---
    p_ping = sub.add_parser('ping', help='Ping a host')
    p_ping.add_argument('host', help='Hostname or IP address to ping')
    p_ping.add_argument('-c', '--count', type=int, default=4, help='Number of pings (default: 4)')
    p_ping.add_argument('-t', '--timeout', type=int, default=2, help='Timeout per ping in seconds (default: 2)')
    p_ping.add_argument('-v', '--verbose', action='store_true', help='Show raw ping output')

    # --- dns ---
    p_dns = sub.add_parser('dns', help='DNS lookup')
    p_dns.add_argument('domain', help='Domain name to resolve')
    p_dns.add_argument('-s', '--server', metavar='SERVER', help='DNS server to use (e.g. 8.8.8.8)')

    # --- status ---
    p_status = sub.add_parser('status', help='Show network status and info')
    p_status.add_argument('-v', '--verbose', action='store_true', help='Show detailed interface info')

    # --- ports ---
    p_ports = sub.add_parser('ports', help='Scan common ports on a host')
    p_ports.add_argument('--host', default='127.0.0.1', help='Host to scan (default: 127.0.0.1)')
    p_ports.add_argument('--ports', type=int, nargs='+', metavar='PORT',
                         help='Ports to check (defaults to common ports)')

    # --- traffic ---
    sub.add_parser('traffic', help='Show network interface traffic counters')

    # --- pihole ---
    p_pi = sub.add_parser('pihole', help='Pi-hole monitoring')
    p_pi.add_argument('action', choices=['status', 'summary', 'blocked'], help='Pi-hole action')
    p_pi.add_argument('--url', required=True, help='Pi-hole URL (e.g. http://192.168.1.1)')
    p_pi.add_argument('--api-key', dest='api_key', help='Pi-hole API key (optional)')
    p_pi.add_argument('--count', type=int, default=10, help='Number of blocked domains to list (default: 10)')

    # --- monitor ---
    p_mon = sub.add_parser('monitor', help='Continuous live monitoring')
    p_mon.add_argument('--host', default='8.8.8.8', help='Host to monitor (default: 8.8.8.8)')
    p_mon.add_argument('--interval', type=int, default=5, help='Check interval in seconds (default: 5)')

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    print_header()

    if not args.command:
        parser.print_help()
        return 1

    dispatch = {
        'ping': cmd_ping,
        'dns': cmd_dns,
        'status': cmd_status,
        'ports': cmd_ports,
        'traffic': cmd_traffic,
        'pihole': cmd_pihole,
        'monitor': cmd_monitor,
    }

    return dispatch[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
