#!/usr/bin/env python3
"""
NetworkzeroMonitor - Graphical User Interface
Ionity (Pty) Ltd - www.ionity.today

GUI for network monitoring and diagnostics.
Tabs: Dashboard · Ping · DNS Lookup · Pi-hole · Live Monitor · Port Scanner · Traffic
"""

import configparser
import os
import threading
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from network_monitor import NetworkMonitor, PiHoleMonitor

# ---------------------------------------------------------------------------
# Load config
# ---------------------------------------------------------------------------
_cfg = configparser.ConfigParser()
_cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
if os.path.exists(_cfg_path):
    _cfg.read(_cfg_path)

WINDOW_WIDTH = int(_cfg.get('UI', 'window_width', fallback='1024'))
WINDOW_HEIGHT = int(_cfg.get('UI', 'window_height', fallback='720'))
THEME = _cfg.get('UI', 'theme', fallback='clam')

IONITY_BLUE = '#0057B7'
IONITY_DARK = '#1a1a2e'
IONITY_LIGHT = '#e8f4fd'


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _bytes_human(n: int) -> str:
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


# ---------------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------------

class NetworkzeroGUI:
    """Main GUI application for NetworkzeroMonitor."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("NetworkzeroMonitor — Ionity (Pty) Ltd")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(800, 600)

        self.monitor = NetworkMonitor()
        self.pihole: PiHoleMonitor | None = None
        self.monitoring_active = False
        self._monitor_thread: threading.Thread | None = None

        # Apply ttk theme
        style = ttk.Style()
        try:
            style.theme_use(THEME)
        except tk.TclError:
            pass
        style.configure('Header.TLabel', font=('Arial', 18, 'bold'), foreground=IONITY_BLUE)
        style.configure('Brand.TLabel', font=('Arial', 10), foreground=IONITY_BLUE)
        style.configure('Status.TLabel', font=('Arial', 10), relief=tk.SUNKEN)

        self._build_ui()
        # Initial data load (non-blocking)
        threading.Thread(target=self._refresh_dashboard_data, daemon=True).start()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self._build_header()
        self._build_notebook()
        self._build_statusbar()

    def _build_header(self):
        hdr = ttk.Frame(self.root, padding=(10, 6, 10, 2))
        hdr.grid(row=0, column=0, sticky='ew')
        hdr.columnconfigure(1, weight=1)

        ttk.Label(hdr, text="NetworkzeroMonitor", style='Header.TLabel').grid(
            row=0, column=0, sticky='w')
        ttk.Label(hdr, text="Ionity (Pty) Ltd  ·  www.ionity.today",
                  style='Brand.TLabel').grid(row=1, column=0, sticky='w')
        ttk.Button(hdr, text="⟳  Refresh All", command=self._refresh_all).grid(
            row=0, column=2, rowspan=2, padx=(10, 0))

    def _build_notebook(self):
        self.nb = ttk.Notebook(self.root)
        self.nb.grid(row=1, column=0, sticky='nsew', padx=8, pady=4)

        self._tab_dashboard()
        self._tab_ping()
        self._tab_dns()
        self._tab_pihole()
        self._tab_monitor()
        self._tab_ports()
        self._tab_traffic()

    def _build_statusbar(self):
        bar = ttk.Frame(self.root)
        bar.grid(row=2, column=0, sticky='ew')
        bar.columnconfigure(0, weight=1)
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(bar, textvariable=self.status_var, style='Status.TLabel').grid(
            row=0, column=0, sticky='ew', padx=4, pady=2)

    # ------------------------------------------------------------------
    # Tab: Dashboard
    # ------------------------------------------------------------------

    def _tab_dashboard(self):
        tab = ttk.Frame(self.nb, padding=6)
        self.nb.add(tab, text="📊 Dashboard")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        # Network info
        info_f = ttk.LabelFrame(tab, text="Network Information", padding=6)
        info_f.grid(row=0, column=0, sticky='ew', pady=(0, 4))
        info_f.columnconfigure(0, weight=1)
        self.dash_info = scrolledtext.ScrolledText(info_f, height=8, state='disabled', wrap='word')
        self.dash_info.grid(row=0, column=0, sticky='ew')

        # Connectivity
        conn_f = ttk.LabelFrame(tab, text="Internet Connectivity", padding=6)
        conn_f.grid(row=1, column=0, sticky='nsew', pady=(0, 4))
        conn_f.columnconfigure(0, weight=1)
        conn_f.rowconfigure(1, weight=1)

        self.conn_label = ttk.Label(conn_f, text="Status: Checking…", font=('Arial', 12, 'bold'))
        self.conn_label.grid(row=0, column=0, pady=4, sticky='w')
        self.conn_details = scrolledtext.ScrolledText(conn_f, height=6, state='disabled', wrap='word')
        self.conn_details.grid(row=1, column=0, sticky='nsew')

        ttk.Button(tab, text="Refresh Dashboard",
                   command=lambda: threading.Thread(
                       target=self._refresh_dashboard_data, daemon=True).start()
                   ).grid(row=2, column=0, pady=4)

    def _refresh_dashboard_data(self):
        self._status("Refreshing dashboard…")
        info = self.monitor.get_network_info()
        connectivity = self.monitor.check_internet_connectivity()
        self.root.after(0, self._update_dashboard, info, connectivity)

    def _update_dashboard(self, info, connectivity):
        # Network info panel
        self.dash_info.config(state='normal')
        self.dash_info.delete('1.0', 'end')
        self.dash_info.insert('end', "Network Information\n")
        self.dash_info.insert('end', "═" * 48 + "\n\n")
        for key, val in info.items():
            if key == 'interfaces':
                self.dash_info.insert('end', "Interfaces:\n")
                for iface, data in val.items():
                    up = "UP" if data['is_up'] else "down"
                    ips = ', '.join(data['ipv4']) or 'no IPv4'
                    self.dash_info.insert('end', f"  {iface}: {up}  {ips}\n")
            elif key != 'platform_version':
                label = key.replace('_', ' ').title()
                self.dash_info.insert('end', f"{label}: {val}\n")
        self.dash_info.config(state='disabled')

        # Connectivity panel
        connected = connectivity['connected']
        quality = connectivity['quality']
        self.conn_label.config(
            text=f"Status: {'Connected' if connected else 'Disconnected'}  ({quality})",
            foreground='green' if connected else 'red',
        )
        self.conn_details.config(state='normal')
        self.conn_details.delete('1.0', 'end')
        for test in connectivity['tests']:
            sym = "✓" if test['reachable'] else "✗"
            self.conn_details.insert('end', f" {sym}  {test['domain']}\n")
        self.conn_details.config(state='disabled')
        self._status("Dashboard refreshed")

    # ------------------------------------------------------------------
    # Tab: Ping
    # ------------------------------------------------------------------

    def _tab_ping(self):
        tab = ttk.Frame(self.nb, padding=6)
        self.nb.add(tab, text="🏓 Ping")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        inp = ttk.Frame(tab)
        inp.grid(row=0, column=0, sticky='ew', pady=4)

        ttk.Label(inp, text="Host:").grid(row=0, column=0, sticky='w')
        self.ping_host = ttk.Entry(inp, width=36)
        self.ping_host.grid(row=0, column=1, padx=4)
        self.ping_host.insert(0, "8.8.8.8")

        ttk.Label(inp, text="Count:").grid(row=0, column=2, padx=(12, 0))
        self.ping_count = ttk.Spinbox(inp, from_=1, to=20, width=6)
        self.ping_count.grid(row=0, column=3, padx=4)
        self.ping_count.set(4)

        ttk.Label(inp, text="Timeout (s):").grid(row=0, column=4, padx=(12, 0))
        self.ping_timeout = ttk.Spinbox(inp, from_=1, to=10, width=6)
        self.ping_timeout.grid(row=0, column=5, padx=4)
        self.ping_timeout.set(2)

        ttk.Button(inp, text="Ping", command=self._do_ping).grid(row=0, column=6, padx=8)

        res_f = ttk.LabelFrame(tab, text="Results", padding=6)
        res_f.grid(row=1, column=0, sticky='nsew', pady=4)
        res_f.columnconfigure(0, weight=1)
        res_f.rowconfigure(0, weight=1)
        self.ping_results = scrolledtext.ScrolledText(res_f, wrap='word')
        self.ping_results.grid(row=0, column=0, sticky='nsew')

    def _do_ping(self):
        host = self.ping_host.get().strip()
        if not host:
            messagebox.showwarning("Input Error", "Please enter a host.")
            return
        count = int(self.ping_count.get())
        timeout = int(self.ping_timeout.get())
        self._status(f"Pinging {host}…")
        threading.Thread(
            target=self._run_ping, args=(host, count, timeout), daemon=True).start()

    def _run_ping(self, host, count, timeout):
        result = self.monitor.ping_host(host, count=count, timeout=timeout)
        self.root.after(0, self._show_ping, result)

    def _show_ping(self, result):
        self.ping_results.delete('1.0', 'end')
        self.ping_results.insert('end', f"Ping Results for {result['host']}\n")
        self.ping_results.insert('end', "─" * 50 + "\n")
        self.ping_results.insert('end', f"Reachable    : {result.get('reachable', False)}\n")
        self.ping_results.insert('end', f"Elapsed Time : {result.get('elapsed_time', 'N/A')} s\n")
        if 'rtt_line' in result:
            self.ping_results.insert('end', f"RTT          : {result['rtt_line']}\n")
        self.ping_results.insert('end', f"Timestamp    : {result['timestamp']}\n")
        if 'output' in result:
            self.ping_results.insert('end', "\nRaw Output:\n" + result['output'])
        if 'error' in result:
            self.ping_results.insert('end', f"\nError: {result['error']}\n")
        self._status("Ping complete")

    # ------------------------------------------------------------------
    # Tab: DNS Lookup
    # ------------------------------------------------------------------

    def _tab_dns(self):
        tab = ttk.Frame(self.nb, padding=6)
        self.nb.add(tab, text="🌐 DNS Lookup")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        inp = ttk.Frame(tab)
        inp.grid(row=0, column=0, sticky='ew', pady=4)

        ttk.Label(inp, text="Domain:").grid(row=0, column=0, sticky='w')
        self.dns_domain = ttk.Entry(inp, width=36)
        self.dns_domain.grid(row=0, column=1, padx=4)
        self.dns_domain.insert(0, "ionity.today")

        ttk.Label(inp, text="DNS Server:").grid(row=1, column=0, sticky='w', pady=4)
        self.dns_server = ttk.Entry(inp, width=20)
        self.dns_server.grid(row=1, column=1, padx=4, sticky='w')

        ttk.Label(inp, text="(leave blank for system default)").grid(row=1, column=2, sticky='w')

        btn_f = ttk.Frame(inp)
        btn_f.grid(row=0, column=3, rowspan=2, padx=8)
        ttk.Button(btn_f, text="Lookup", command=self._do_dns).grid(row=0, column=0, pady=2)
        ttk.Button(btn_f, text="Try All DNS", command=self._do_dns_all).grid(row=1, column=0)

        res_f = ttk.LabelFrame(tab, text="Results", padding=6)
        res_f.grid(row=1, column=0, sticky='nsew', pady=4)
        res_f.columnconfigure(0, weight=1)
        res_f.rowconfigure(0, weight=1)
        self.dns_results = scrolledtext.ScrolledText(res_f, wrap='word')
        self.dns_results.grid(row=0, column=0, sticky='nsew')

    def _do_dns(self):
        domain = self.dns_domain.get().strip()
        if not domain:
            messagebox.showwarning("Input Error", "Please enter a domain.")
            return
        server = self.dns_server.get().strip() or None
        self._status(f"Resolving {domain}…")
        threading.Thread(target=self._run_dns, args=(domain, server), daemon=True).start()

    def _run_dns(self, domain, server):
        result = self.monitor.check_dns_resolution(domain, server)
        self.root.after(0, self._show_dns, [result])

    def _do_dns_all(self):
        domain = self.dns_domain.get().strip()
        if not domain:
            messagebox.showwarning("Input Error", "Please enter a domain.")
            return
        self._status(f"Resolving {domain} via all DNS servers…")
        threading.Thread(target=self._run_dns_all, args=(domain,), daemon=True).start()

    def _run_dns_all(self, domain):
        results = []
        for server in self.monitor.dns_servers:
            results.append(self.monitor.check_dns_resolution(domain, server))
        self.root.after(0, self._show_dns, results)

    def _show_dns(self, results):
        self.dns_results.delete('1.0', 'end')
        for result in results:
            self.dns_results.insert('end', f"DNS Resolution: {result['domain']}\n")
            self.dns_results.insert('end', "─" * 50 + "\n")
            self.dns_results.insert('end', f"  Server      : {result['dns_server']}\n")
            if result['success']:
                self.dns_results.insert('end', f"  IP Addresses: {', '.join(result['ip_addresses'])}\n")
                self.dns_results.insert('end', f"  Query Time  : {result['query_time']} ms\n")
            else:
                self.dns_results.insert('end', f"  Error       : {result.get('error', 'Unknown')}\n")
            self.dns_results.insert('end', f"  Timestamp   : {result['timestamp']}\n\n")
        self._status("DNS lookup complete")

    # ------------------------------------------------------------------
    # Tab: Pi-hole
    # ------------------------------------------------------------------

    def _tab_pihole(self):
        tab = ttk.Frame(self.nb, padding=6)
        self.nb.add(tab, text="🕳  Pi-hole")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        cfg_f = ttk.LabelFrame(tab, text="Pi-hole Configuration", padding=6)
        cfg_f.grid(row=0, column=0, sticky='ew', pady=(0, 4))

        ttk.Label(cfg_f, text="URL:").grid(row=0, column=0, sticky='w')
        self.ph_url = ttk.Entry(cfg_f, width=36)
        self.ph_url.grid(row=0, column=1, padx=4)
        self.ph_url.insert(0, "http://192.168.1.1")

        ttk.Label(cfg_f, text="API Key:").grid(row=1, column=0, sticky='w', pady=4)
        self.ph_key = ttk.Entry(cfg_f, width=36, show="*")
        self.ph_key.grid(row=1, column=1, padx=4, pady=4)

        ttk.Label(cfg_f, text="(optional)").grid(row=1, column=2, sticky='w')

        btn_f = ttk.Frame(cfg_f)
        btn_f.grid(row=2, column=0, columnspan=3, pady=4)
        for text, cmd in [
            ("Status", self._ph_status),
            ("Summary", self._ph_summary),
            ("Top Blocked", self._ph_blocked),
        ]:
            ttk.Button(btn_f, text=text, command=cmd).pack(side='left', padx=4)

        res_f = ttk.LabelFrame(tab, text="Pi-hole Information", padding=6)
        res_f.grid(row=1, column=0, sticky='nsew', pady=4)
        res_f.columnconfigure(0, weight=1)
        res_f.rowconfigure(0, weight=1)
        self.ph_results = scrolledtext.ScrolledText(res_f, wrap='word')
        self.ph_results.grid(row=0, column=0, sticky='nsew')

    def _pihole_instance(self) -> PiHoleMonitor:
        url = self.ph_url.get().strip()
        key = self.ph_key.get().strip() or None
        return PiHoleMonitor(url, key)

    def _ph_status(self):
        self._status("Checking Pi-hole status…")
        threading.Thread(target=lambda: self.root.after(
            0, self._show_ph, self._pihole_instance().check_status()), daemon=True).start()

    def _ph_summary(self):
        self._status("Getting Pi-hole summary…")
        threading.Thread(target=lambda: self.root.after(
            0, self._show_ph_summary, self._pihole_instance().get_summary()), daemon=True).start()

    def _ph_blocked(self):
        self._status("Getting top blocked domains…")
        threading.Thread(target=lambda: self.root.after(
            0, self._show_ph_blocked, self._pihole_instance().get_top_blocked(10)), daemon=True).start()

    def _show_ph(self, result):
        self.ph_results.delete('1.0', 'end')
        self.ph_results.insert('end', f"Pi-hole Status: {self.ph_url.get()}\n")
        self.ph_results.insert('end', "─" * 50 + "\n")
        if result['success']:
            self.ph_results.insert('end', f"  Status  : {result['status']}\n")
            self.ph_results.insert('end', f"  Enabled : {result['enabled']}\n")
        else:
            self.ph_results.insert('end', f"  Error   : {result.get('error', 'Unknown')}\n")
        self.ph_results.insert('end', f"\n  Timestamp: {result['timestamp']}\n")
        self._status("Pi-hole status retrieved")

    def _show_ph_summary(self, result):
        self.ph_results.delete('1.0', 'end')
        self.ph_results.insert('end', f"Pi-hole Summary: {self.ph_url.get()}\n")
        self.ph_results.insert('end', "─" * 50 + "\n")
        if result['success']:
            self.ph_results.insert('end', f"  DNS Queries Today    : {result['dns_queries_today']:,}\n")
            self.ph_results.insert('end', f"  Ads Blocked Today    : {result['ads_blocked_today']:,}\n")
            self.ph_results.insert('end', f"  Percentage Blocked   : {result['ads_percentage_today']:.1f}%\n")
            self.ph_results.insert('end', f"  Domains on Blocklist : {result['domains_being_blocked']:,}\n")
            self.ph_results.insert('end', f"  Status               : {result['status']}\n")
        else:
            self.ph_results.insert('end', f"  Error : {result.get('error', 'Unknown')}\n")
        self.ph_results.insert('end', f"\n  Timestamp: {result['timestamp']}\n")
        self._status("Pi-hole summary retrieved")

    def _show_ph_blocked(self, result):
        self.ph_results.delete('1.0', 'end')
        self.ph_results.insert('end', f"Top Blocked Domains: {self.ph_url.get()}\n")
        self.ph_results.insert('end', "─" * 50 + "\n")
        if result['success']:
            for i, (domain, count) in enumerate(result['top_ads'].items(), 1):
                self.ph_results.insert('end', f"  {i:2d}. {domain:<40} {count:,} blocks\n")
        else:
            self.ph_results.insert('end', f"  Error : {result.get('error', 'Unknown')}\n")
        self.ph_results.insert('end', f"\n  Timestamp: {result['timestamp']}\n")
        self._status("Top blocked domains retrieved")

    # ------------------------------------------------------------------
    # Tab: Live Monitor
    # ------------------------------------------------------------------

    def _tab_monitor(self):
        tab = ttk.Frame(self.nb, padding=6)
        self.nb.add(tab, text="📡 Live Monitor")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        ctrl = ttk.Frame(tab)
        ctrl.grid(row=0, column=0, sticky='ew', pady=4)

        ttk.Label(ctrl, text="Monitor Host:").grid(row=0, column=0, sticky='w')
        self.mon_host = ttk.Entry(ctrl, width=24)
        self.mon_host.grid(row=0, column=1, padx=4)
        self.mon_host.insert(0, "8.8.8.8")

        ttk.Label(ctrl, text="Interval (s):").grid(row=0, column=2, padx=(12, 0))
        self.mon_interval = ttk.Spinbox(ctrl, from_=1, to=60, width=6)
        self.mon_interval.grid(row=0, column=3, padx=4)
        self.mon_interval.set(5)

        self.mon_btn = ttk.Button(ctrl, text="▶  Start", command=self._toggle_monitoring)
        self.mon_btn.grid(row=0, column=4, padx=8)

        ttk.Button(ctrl, text="Clear Log",
                   command=lambda: self.mon_display.delete('1.0', 'end')).grid(row=0, column=5)

        live_f = ttk.LabelFrame(tab, text="Live Activity", padding=6)
        live_f.grid(row=1, column=0, sticky='nsew', pady=4)
        live_f.columnconfigure(0, weight=1)
        live_f.rowconfigure(0, weight=1)
        self.mon_display = scrolledtext.ScrolledText(live_f, wrap='word')
        self.mon_display.grid(row=0, column=0, sticky='nsew')

    def _toggle_monitoring(self):
        if self.monitoring_active:
            self.monitoring_active = False
            self.mon_btn.config(text="▶  Start")
            self._status("Monitoring stopped")
        else:
            self.monitoring_active = True
            self.mon_btn.config(text="⏹  Stop")
            interval = int(self.mon_interval.get())
            host = self.mon_host.get().strip() or '8.8.8.8'
            self._monitor_thread = threading.Thread(
                target=self._run_monitor, args=(host, interval), daemon=True)
            self._monitor_thread.start()
            self._status(f"Monitoring {host} every {interval}s…")

    def _run_monitor(self, host: str, interval: int):
        while self.monitoring_active:
            connectivity = self.monitor.check_internet_connectivity()
            ping = self.monitor.ping_host(host, count=1, timeout=2)
            net_sym = "✓" if connectivity['connected'] else "✗"
            ping_sym = "✓" if ping.get('reachable', False) else "✗"
            ts = time.strftime('%H:%M:%S')
            line = (
                f"[{ts}] Internet: {net_sym} {connectivity['quality']:<12} | "
                f"{host}: {ping_sym}\n"
            )
            self.root.after(0, self._append_monitor, line)
            time.sleep(interval)

    def _append_monitor(self, line: str):
        self.mon_display.insert('end', line)
        self.mon_display.see('end')

    # ------------------------------------------------------------------
    # Tab: Port Scanner
    # ------------------------------------------------------------------

    def _tab_ports(self):
        tab = ttk.Frame(self.nb, padding=6)
        self.nb.add(tab, text="🔍 Port Scanner")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        inp = ttk.Frame(tab)
        inp.grid(row=0, column=0, sticky='ew', pady=4)

        ttk.Label(inp, text="Host:").grid(row=0, column=0, sticky='w')
        self.port_host = ttk.Entry(inp, width=30)
        self.port_host.grid(row=0, column=1, padx=4)
        self.port_host.insert(0, "127.0.0.1")

        ttk.Label(inp, text="Ports (comma-separated):").grid(row=0, column=2, padx=(12, 0))
        self.port_list = ttk.Entry(inp, width=40)
        self.port_list.grid(row=0, column=3, padx=4)
        self.port_list.insert(0, "21,22,23,25,53,80,110,143,443,3306,5432,8080,8443")

        ttk.Button(inp, text="Scan", command=self._do_port_scan).grid(row=0, column=4, padx=8)

        res_f = ttk.LabelFrame(tab, text="Results", padding=6)
        res_f.grid(row=1, column=0, sticky='nsew', pady=4)
        res_f.columnconfigure(0, weight=1)
        res_f.rowconfigure(0, weight=1)
        self.port_results = scrolledtext.ScrolledText(res_f, wrap='word')
        self.port_results.grid(row=0, column=0, sticky='nsew')

    def _do_port_scan(self):
        host = self.port_host.get().strip()
        raw = self.port_list.get().strip()
        try:
            ports = [int(p.strip()) for p in raw.split(',') if p.strip()]
        except ValueError:
            messagebox.showwarning("Input Error", "Ports must be comma-separated integers.")
            return
        if not host:
            messagebox.showwarning("Input Error", "Please enter a host.")
            return
        self._status(f"Scanning ports on {host}…")
        threading.Thread(target=self._run_port_scan, args=(host, ports), daemon=True).start()

    def _run_port_scan(self, host, ports):
        result = self.monitor.get_open_ports(host=host, ports=ports)
        self.root.after(0, self._show_ports, result)

    def _show_ports(self, result):
        self.port_results.delete('1.0', 'end')
        self.port_results.insert('end', f"Port Scan: {result['host']}\n")
        self.port_results.insert('end', "─" * 50 + "\n")
        open_ports = [p for p, o in sorted(result['ports'].items()) if o]
        for port, is_open in sorted(result['ports'].items()):
            state = "OPEN  ✓" if is_open else "closed"
            self.port_results.insert('end', f"  Port {port:<6}: {state}\n")
        self.port_results.insert('end', f"\n  Open ports: {len(open_ports)}/{len(result['ports'])}\n")
        self.port_results.insert('end', f"  Timestamp : {result['timestamp']}\n")
        self._status("Port scan complete")

    # ------------------------------------------------------------------
    # Tab: Traffic
    # ------------------------------------------------------------------

    def _tab_traffic(self):
        tab = ttk.Frame(self.nb, padding=6)
        self.nb.add(tab, text="📶 Traffic")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        ctrl = ttk.Frame(tab)
        ctrl.grid(row=0, column=0, sticky='ew', pady=4)
        ttk.Button(ctrl, text="⟳  Refresh Traffic", command=self._refresh_traffic).pack(side='left', padx=4)

        res_f = ttk.LabelFrame(tab, text="Interface Traffic Counters", padding=6)
        res_f.grid(row=1, column=0, sticky='nsew', pady=4)
        res_f.columnconfigure(0, weight=1)
        res_f.rowconfigure(0, weight=1)
        self.traffic_results = scrolledtext.ScrolledText(res_f, wrap='word', font=('Courier', 10))
        self.traffic_results.grid(row=0, column=0, sticky='nsew')

        # Load immediately
        self._refresh_traffic()

    def _refresh_traffic(self):
        self._status("Reading traffic counters…")
        threading.Thread(target=self._run_traffic, daemon=True).start()

    def _run_traffic(self):
        traffic = self.monitor.get_interface_traffic()
        self.root.after(0, self._show_traffic, traffic)

    def _show_traffic(self, traffic):
        self.traffic_results.delete('1.0', 'end')
        hdr = f"{'Interface':<22} {'Sent':>12} {'Received':>12} {'ErrIn':>8} {'ErrOut':>8}\n"
        self.traffic_results.insert('end', hdr)
        self.traffic_results.insert('end', "─" * 66 + "\n")
        for iface, data in traffic.items():
            self.traffic_results.insert(
                'end',
                f"{iface:<22} "
                f"{_bytes_human(data['bytes_sent']):>12} "
                f"{_bytes_human(data['bytes_recv']):>12} "
                f"{data['errin']:>8} "
                f"{data['errout']:>8}\n"
            )
        self.traffic_results.insert('end', f"\n  Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        self._status("Traffic counters updated")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _status(self, msg: str):
        self.status_var.set(msg)
        self.root.update_idletasks()

    def _refresh_all(self):
        threading.Thread(target=self._refresh_dashboard_data, daemon=True).start()
        self._refresh_traffic()
        self._status("Refreshing all data…")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    root = tk.Tk()
    app = NetworkzeroGUI(root)  # noqa: F841
    root.mainloop()


if __name__ == '__main__':
    main()
