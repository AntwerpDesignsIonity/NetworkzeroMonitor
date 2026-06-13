#!/usr/bin/env python3
"""
NetworkzeroMonitor - Mobile API Server
Ionity (Pty) Ltd - www.ionity.today

A lightweight Flask REST API that exposes the full NetworkzeroMonitor
backend over HTTP and serves the installable mobile PWA. Point any
phone's browser at this server (http://<host>:8088) to monitor the
network from a handset, or "Add to Home Screen" to install it as an app.

Endpoints (all return JSON unless noted):
    GET  /                          -> mobile PWA (HTML)
    GET  /api/health                -> server liveness + version
    GET  /api/network               -> hostname, IPs, interfaces
    GET  /api/connectivity          -> internet reachability + quality
    GET  /api/traffic               -> per-interface traffic counters
    GET  /api/ping?host=&count=     -> ping a host
    GET  /api/dns?domain=&server=   -> DNS lookup
    GET  /api/ports?host=&ports=    -> port scan
    GET  /api/pihole/<action>       -> pihole status|summary|blocked (query: url, api_key)
    GET  /api/extended/cellular     -> mobile broadband (2G-5G)
    GET  /api/extended/wifi         -> Wi-Fi link details
    GET  /api/extended/satellite    -> satellite internet (Starlink)
    GET  /api/extended/gnss         -> GNSS / satellite positioning
    GET  /api/extended/all          -> consolidated multi-layer snapshot
    GET  /api/overview              -> everything in one call (mobile dashboard)
"""

import os
import configparser

from flask import Flask, jsonify, request, send_from_directory

from network_monitor import NetworkMonitor, PiHoleMonitor
from network_extended import ExtendedNetworkMonitor

APP_VERSION = '1.1.0'
MOBILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mobile')

app = Flask(__name__, static_folder=None)

_monitor = NetworkMonitor()
_extended = ExtendedNetworkMonitor()

# Load config for sensible server + pihole defaults.
_config = configparser.ConfigParser()
_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
if os.path.exists(_config_path):
    _config.read(_config_path)


def _cfg(section: str, option: str, fallback=None):
    if _config.has_option(section, option):
        return _config.get(section, option)
    return fallback


# --------------------------------------------------------------------------- #
# Static / PWA routes
# --------------------------------------------------------------------------- #
@app.route('/')
def index():
    return send_from_directory(MOBILE_DIR, 'index.html')


@app.route('/<path:filename>')
def static_files(filename):
    # Serve the PWA assets (manifest, service worker, icons, css, js).
    return send_from_directory(MOBILE_DIR, filename)


# --------------------------------------------------------------------------- #
# Core API
# --------------------------------------------------------------------------- #
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'app': 'NetworkzeroMonitor',
        'version': APP_VERSION,
        'company': 'Ionity (Pty) Ltd',
        'website': 'www.ionity.today',
    })


@app.route('/api/network')
def network():
    return jsonify(_monitor.get_network_info())


@app.route('/api/connectivity')
def connectivity():
    return jsonify(_monitor.check_internet_connectivity())


@app.route('/api/traffic')
def traffic():
    return jsonify({'interfaces': _monitor.get_interface_traffic()})


@app.route('/api/ping')
def ping():
    host = request.args.get('host', _cfg('Network', 'default_ping_host', '8.8.8.8'))
    count = request.args.get('count', default=4, type=int)
    timeout = request.args.get('timeout', default=2, type=int)
    return jsonify(_monitor.ping_host(host, count=count, timeout=timeout))


@app.route('/api/dns')
def dns():
    domain = request.args.get('domain')
    if not domain:
        return jsonify({'success': False, 'error': 'domain query parameter required'}), 400
    server = request.args.get('server')
    return jsonify(_monitor.check_dns_resolution(domain, server))


@app.route('/api/ports')
def ports():
    host = request.args.get('host', '127.0.0.1')
    ports_arg = request.args.get('ports')
    port_list = None
    if ports_arg:
        try:
            port_list = [int(p) for p in ports_arg.replace(',', ' ').split()]
        except ValueError:
            return jsonify({'error': 'ports must be integers'}), 400
    return jsonify(_monitor.get_open_ports(host=host, ports=port_list))


@app.route('/api/pihole/<action>')
def pihole(action):
    if action not in ('status', 'summary', 'blocked'):
        return jsonify({'success': False, 'error': 'unknown action'}), 404
    url = request.args.get('url', _cfg('PiHole', 'url'))
    if not url:
        return jsonify({'success': False, 'error': 'pihole url not configured'}), 400
    api_key = request.args.get('api_key', _cfg('PiHole', 'api_key'))
    pi = PiHoleMonitor(url, api_key)
    if action == 'status':
        return jsonify(pi.check_status())
    if action == 'summary':
        return jsonify(pi.get_summary())
    count = request.args.get('count', default=10, type=int)
    return jsonify(pi.get_top_blocked(count=count))


# --------------------------------------------------------------------------- #
# Extended network layers (cellular, wifi, satellite internet, GNSS)
# --------------------------------------------------------------------------- #
@app.route('/api/extended/cellular')
def ext_cellular():
    return jsonify(_extended.get_cellular_info())


@app.route('/api/extended/wifi')
def ext_wifi():
    return jsonify(_extended.get_wifi_info())


@app.route('/api/extended/satellite')
def ext_satellite():
    return jsonify(_extended.get_satellite_internet())


@app.route('/api/extended/gnss')
def ext_gnss():
    return jsonify(_extended.get_gnss_info())


@app.route('/api/extended/all')
def ext_all():
    return jsonify(_extended.get_all_layers())


# --------------------------------------------------------------------------- #
# Aggregated dashboard payload (single round-trip for the mobile home screen)
# --------------------------------------------------------------------------- #
@app.route('/api/overview')
def overview():
    return jsonify({
        'network': _monitor.get_network_info(),
        'connectivity': _monitor.check_internet_connectivity(),
        'extended': _extended.get_all_layers(),
        'version': APP_VERSION,
    })


def main():
    host = os.environ.get('NZM_HOST', '0.0.0.0')
    port = int(os.environ.get('NZM_PORT', '8088'))
    print("NetworkzeroMonitor - Mobile API Server")
    print("Ionity (Pty) Ltd - www.ionity.today")
    print(f"Serving on http://{host}:{port}  (open this on your phone)")
    app.run(host=host, port=port, threaded=True)


if __name__ == '__main__':
    main()
