#!/usr/bin/env python3
"""
NetworkzeroMonitor - Graphical User Interface
Ionity (Pty) Ltd - www.ionity.today

GUI for network monitoring and diagnostics
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from network_monitor import NetworkMonitor, PiHoleMonitor


class NetworkzeroGUI:
    """Main GUI application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("NetworkzeroMonitor - Ionity (Pty) Ltd")
        self.root.geometry("900x700")
        
        self.monitor = NetworkMonitor()
        self.pihole = None
        self.monitoring_active = False
        
        self.setup_ui()
        
        # Start with initial status check
        self.refresh_network_info()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # Notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_ping_tab()
        self.create_dns_tab()
        self.create_pihole_tab()
        self.create_monitor_tab()
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Create application header"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Title
        title_label = ttk.Label(header_frame, text="NetworkzeroMonitor", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Ionity branding
        brand_label = ttk.Label(header_frame, text="Ionity (Pty) Ltd - www.ionity.today", 
                               font=("Arial", 10), foreground="blue")
        brand_label.grid(row=1, column=0, sticky=tk.W)
        
        # Refresh button
        refresh_btn = ttk.Button(header_frame, text="Refresh All", 
                                command=self.refresh_all)
        refresh_btn.grid(row=0, column=1, rowspan=2, padx=10)
    
    def create_dashboard_tab(self):
        """Create network status dashboard tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Dashboard")
        
        # Network Info Section
        info_frame = ttk.LabelFrame(tab, text="Network Information", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=5, pady=5)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=8, width=70, 
                                                   wrap=tk.WORD, state='disabled')
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Connectivity Status Section
        conn_frame = ttk.LabelFrame(tab, text="Internet Connectivity", padding="10")
        conn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), padx=5, pady=5)
        
        self.connectivity_label = ttk.Label(conn_frame, text="Status: Unknown", 
                                           font=("Arial", 12))
        self.connectivity_label.grid(row=0, column=0, pady=5)
        
        self.connectivity_details = scrolledtext.ScrolledText(conn_frame, height=5, 
                                                             width=70, wrap=tk.WORD, 
                                                             state='disabled')
        self.connectivity_details.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Refresh button
        ttk.Button(tab, text="Refresh Dashboard", 
                  command=self.refresh_network_info).grid(row=2, column=0, pady=10)
    
    def create_ping_tab(self):
        """Create ping tool tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Ping")
        
        # Input frame
        input_frame = ttk.Frame(tab, padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(input_frame, text="Host:").grid(row=0, column=0, sticky=tk.W)
        self.ping_host_entry = ttk.Entry(input_frame, width=40)
        self.ping_host_entry.grid(row=0, column=1, padx=5)
        self.ping_host_entry.insert(0, "8.8.8.8")
        
        ttk.Label(input_frame, text="Count:").grid(row=0, column=2, padx=(10, 0))
        self.ping_count_spin = ttk.Spinbox(input_frame, from_=1, to=10, width=10)
        self.ping_count_spin.grid(row=0, column=3, padx=5)
        self.ping_count_spin.set(4)
        
        ttk.Button(input_frame, text="Ping", 
                  command=self.do_ping).grid(row=0, column=4, padx=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(tab, text="Results", padding="10")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        
        self.ping_results = scrolledtext.ScrolledText(results_frame, height=20, 
                                                     wrap=tk.WORD)
        self.ping_results.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_dns_tab(self):
        """Create DNS lookup tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="DNS Lookup")
        
        # Input frame
        input_frame = ttk.Frame(tab, padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(input_frame, text="Domain:").grid(row=0, column=0, sticky=tk.W)
        self.dns_domain_entry = ttk.Entry(input_frame, width=40)
        self.dns_domain_entry.grid(row=0, column=1, padx=5)
        self.dns_domain_entry.insert(0, "google.com")
        
        ttk.Label(input_frame, text="DNS Server:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dns_server_entry = ttk.Entry(input_frame, width=40)
        self.dns_server_entry.grid(row=1, column=1, padx=5, pady=5)
        self.dns_server_entry.insert(0, "8.8.8.8")
        
        ttk.Button(input_frame, text="Lookup", 
                  command=self.do_dns_lookup).grid(row=0, column=2, rowspan=2, padx=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(tab, text="Results", padding="10")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        
        self.dns_results = scrolledtext.ScrolledText(results_frame, height=20, wrap=tk.WORD)
        self.dns_results.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_pihole_tab(self):
        """Create Pi-hole monitoring tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Pi-hole")
        
        # Configuration frame
        config_frame = ttk.LabelFrame(tab, text="Pi-hole Configuration", padding="10")
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(config_frame, text="Pi-hole URL:").grid(row=0, column=0, sticky=tk.W)
        self.pihole_url_entry = ttk.Entry(config_frame, width=40)
        self.pihole_url_entry.grid(row=0, column=1, padx=5)
        self.pihole_url_entry.insert(0, "http://192.168.1.1")
        
        ttk.Label(config_frame, text="API Key (optional):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pihole_key_entry = ttk.Entry(config_frame, width=40, show="*")
        self.pihole_key_entry.grid(row=1, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(config_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(button_frame, text="Check Status", 
                  command=self.check_pihole_status).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Get Summary", 
                  command=self.get_pihole_summary).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Top Blocked", 
                  command=self.get_pihole_blocked).grid(row=0, column=2, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(tab, text="Pi-hole Information", padding="10")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        
        self.pihole_results = scrolledtext.ScrolledText(results_frame, height=15, wrap=tk.WORD)
        self.pihole_results.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_monitor_tab(self):
        """Create continuous monitoring tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Live Monitor")
        
        # Control frame
        control_frame = ttk.Frame(tab, padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(control_frame, text="Monitor Host:").grid(row=0, column=0, sticky=tk.W)
        self.monitor_host_entry = ttk.Entry(control_frame, width=30)
        self.monitor_host_entry.grid(row=0, column=1, padx=5)
        self.monitor_host_entry.insert(0, "8.8.8.8")
        
        ttk.Label(control_frame, text="Interval (sec):").grid(row=0, column=2, padx=(10, 0))
        self.monitor_interval_spin = ttk.Spinbox(control_frame, from_=1, to=60, width=10)
        self.monitor_interval_spin.grid(row=0, column=3, padx=5)
        self.monitor_interval_spin.set(5)
        
        self.monitor_btn = ttk.Button(control_frame, text="Start Monitoring", 
                                     command=self.toggle_monitoring)
        self.monitor_btn.grid(row=0, column=4, padx=10)
        
        # Monitor display frame
        display_frame = ttk.LabelFrame(tab, text="Live Activity", padding="10")
        display_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        display_frame.columnconfigure(0, weight=1)
        
        self.monitor_display = scrolledtext.ScrolledText(display_frame, height=20, wrap=tk.WORD)
        self.monitor_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        status_frame.columnconfigure(0, weight=1)
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def refresh_network_info(self):
        """Refresh network information on dashboard"""
        self.update_status("Refreshing network information...")
        
        # Get network info
        info = self.monitor.get_network_info()
        
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "Network Information\n")
        self.info_text.insert(tk.END, "=" * 50 + "\n\n")
        
        for key, value in info.items():
            self.info_text.insert(tk.END, f"{key.replace('_', ' ').title()}: {value}\n")
        
        self.info_text.config(state='disabled')
        
        # Check connectivity
        connectivity = self.monitor.check_internet_connectivity()
        
        status_text = f"Status: {'Connected' if connectivity['connected'] else 'Disconnected'} ({connectivity['quality']})"
        self.connectivity_label.config(text=status_text)
        
        if connectivity['connected']:
            self.connectivity_label.config(foreground='green')
        else:
            self.connectivity_label.config(foreground='red')
        
        self.connectivity_details.config(state='normal')
        self.connectivity_details.delete(1.0, tk.END)
        self.connectivity_details.insert(tk.END, "Connectivity Tests:\n")
        
        for test in connectivity['tests']:
            symbol = "✓" if test['reachable'] else "✗"
            self.connectivity_details.insert(tk.END, f"  {symbol} {test['domain']}\n")
        
        self.connectivity_details.config(state='disabled')
        
        self.update_status("Network information refreshed")
    
    def do_ping(self):
        """Execute ping operation"""
        host = self.ping_host_entry.get().strip()
        if not host:
            messagebox.showwarning("Input Error", "Please enter a host to ping")
            return
        
        count = int(self.ping_count_spin.get())
        
        self.update_status(f"Pinging {host}...")
        self.ping_results.delete(1.0, tk.END)
        self.ping_results.insert(tk.END, f"Pinging {host} with {count} packets...\n\n")
        self.root.update_idletasks()
        
        result = self.monitor.ping_host(host, count=count)
        
        self.ping_results.insert(tk.END, f"Results:\n")
        self.ping_results.insert(tk.END, "=" * 50 + "\n")
        self.ping_results.insert(tk.END, f"Success: {result['success']}\n")
        self.ping_results.insert(tk.END, f"Reachable: {result.get('reachable', False)}\n")
        self.ping_results.insert(tk.END, f"Elapsed Time: {result.get('elapsed_time', 'N/A')} seconds\n")
        self.ping_results.insert(tk.END, f"Timestamp: {result['timestamp']}\n\n")
        
        if 'output' in result:
            self.ping_results.insert(tk.END, "Detailed Output:\n")
            self.ping_results.insert(tk.END, "-" * 50 + "\n")
            self.ping_results.insert(tk.END, result['output'])
        
        if 'error' in result:
            self.ping_results.insert(tk.END, f"\nError: {result['error']}\n")
        
        self.update_status("Ping completed")
    
    def do_dns_lookup(self):
        """Execute DNS lookup"""
        domain = self.dns_domain_entry.get().strip()
        if not domain:
            messagebox.showwarning("Input Error", "Please enter a domain to lookup")
            return
        
        dns_server = self.dns_server_entry.get().strip() or None
        
        self.update_status(f"Looking up {domain}...")
        self.dns_results.delete(1.0, tk.END)
        self.dns_results.insert(tk.END, f"DNS Lookup for {domain}\n\n")
        self.root.update_idletasks()
        
        result = self.monitor.check_dns_resolution(domain, dns_server)
        
        self.dns_results.insert(tk.END, f"Results:\n")
        self.dns_results.insert(tk.END, "=" * 50 + "\n")
        self.dns_results.insert(tk.END, f"Success: {result['success']}\n")
        self.dns_results.insert(tk.END, f"DNS Server: {result['dns_server']}\n")
        
        if result['success']:
            self.dns_results.insert(tk.END, f"Query Time: {result['query_time']} ms\n\n")
            self.dns_results.insert(tk.END, "IP Addresses:\n")
            for ip in result['ip_addresses']:
                self.dns_results.insert(tk.END, f"  • {ip}\n")
        else:
            self.dns_results.insert(tk.END, f"\nError: {result.get('error')}\n")
        
        self.dns_results.insert(tk.END, f"\nTimestamp: {result['timestamp']}\n")
        
        self.update_status("DNS lookup completed")
    
    def get_pihole_instance(self):
        """Get or create Pi-hole instance"""
        url = self.pihole_url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter Pi-hole URL")
            return None
        
        api_key = self.pihole_key_entry.get().strip() or None
        return PiHoleMonitor(url, api_key)
    
    def check_pihole_status(self):
        """Check Pi-hole status"""
        pihole = self.get_pihole_instance()
        if not pihole:
            return
        
        self.update_status("Checking Pi-hole status...")
        self.pihole_results.delete(1.0, tk.END)
        
        result = pihole.check_status()
        
        self.pihole_results.insert(tk.END, "Pi-hole Status\n")
        self.pihole_results.insert(tk.END, "=" * 50 + "\n\n")
        
        if result['success']:
            self.pihole_results.insert(tk.END, f"Status: {result['status']}\n")
            self.pihole_results.insert(tk.END, f"Enabled: {result['enabled']}\n")
        else:
            self.pihole_results.insert(tk.END, f"Error: {result.get('error')}\n")
        
        self.pihole_results.insert(tk.END, f"\nTimestamp: {result['timestamp']}\n")
        
        self.update_status("Pi-hole status check completed")
    
    def get_pihole_summary(self):
        """Get Pi-hole summary statistics"""
        pihole = self.get_pihole_instance()
        if not pihole:
            return
        
        self.update_status("Getting Pi-hole summary...")
        self.pihole_results.delete(1.0, tk.END)
        
        result = pihole.get_summary()
        
        self.pihole_results.insert(tk.END, "Pi-hole Summary\n")
        self.pihole_results.insert(tk.END, "=" * 50 + "\n\n")
        
        if result['success']:
            self.pihole_results.insert(tk.END, f"DNS Queries Today: {result['dns_queries_today']:,}\n")
            self.pihole_results.insert(tk.END, f"Ads Blocked Today: {result['ads_blocked_today']:,}\n")
            self.pihole_results.insert(tk.END, f"Percentage Blocked: {result['ads_percentage_today']:.1f}%\n")
            self.pihole_results.insert(tk.END, f"Domains on Blocklist: {result['domains_being_blocked']:,}\n")
            self.pihole_results.insert(tk.END, f"Status: {result['status']}\n")
        else:
            self.pihole_results.insert(tk.END, f"Error: {result.get('error')}\n")
        
        self.pihole_results.insert(tk.END, f"\nTimestamp: {result['timestamp']}\n")
        
        self.update_status("Pi-hole summary retrieved")
    
    def get_pihole_blocked(self):
        """Get top blocked domains from Pi-hole"""
        pihole = self.get_pihole_instance()
        if not pihole:
            return
        
        self.update_status("Getting top blocked domains...")
        self.pihole_results.delete(1.0, tk.END)
        
        result = pihole.get_top_blocked(count=10)
        
        self.pihole_results.insert(tk.END, "Top Blocked Domains\n")
        self.pihole_results.insert(tk.END, "=" * 50 + "\n\n")
        
        if result['success']:
            for i, (domain, count) in enumerate(result['top_ads'].items(), 1):
                self.pihole_results.insert(tk.END, f"{i:2d}. {domain} ({count:,} blocks)\n")
        else:
            self.pihole_results.insert(tk.END, f"Error: {result.get('error')}\n")
        
        self.pihole_results.insert(tk.END, f"\nTimestamp: {result['timestamp']}\n")
        
        self.update_status("Top blocked domains retrieved")
    
    def toggle_monitoring(self):
        """Toggle continuous monitoring on/off"""
        if not self.monitoring_active:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        self.monitoring_active = True
        self.monitor_btn.config(text="Stop Monitoring")
        self.monitor_display.delete(1.0, tk.END)
        self.monitor_display.insert(tk.END, "Starting continuous monitoring...\n")
        self.monitor_display.insert(tk.END, "=" * 60 + "\n\n")
        
        # Start monitoring in a separate thread
        thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        thread.start()
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        self.monitor_btn.config(text="Start Monitoring")
        self.monitor_display.insert(tk.END, "\n" + "=" * 60 + "\n")
        self.monitor_display.insert(tk.END, "Monitoring stopped.\n")
        self.update_status("Monitoring stopped")
    
    def monitoring_loop(self):
        """Continuous monitoring loop"""
        host = self.monitor_host_entry.get().strip()
        interval = int(self.monitor_interval_spin.get())
        
        while self.monitoring_active:
            timestamp = time.strftime('%H:%M:%S')
            
            # Check connectivity
            connectivity = self.monitor.check_internet_connectivity()
            status_symbol = "✓" if connectivity['connected'] else "✗"
            
            # Ping host
            ping_result = self.monitor.ping_host(host, count=1, timeout=2)
            ping_symbol = "✓" if ping_result.get('reachable', False) else "✗"
            
            # Update display
            line = f"[{timestamp}] Internet: {status_symbol} {connectivity['quality']:15s} | {host}: {ping_symbol}\n"
            
            self.monitor_display.insert(tk.END, line)
            self.monitor_display.see(tk.END)
            
            time.sleep(interval)
        
    def refresh_all(self):
        """Refresh all tabs"""
        self.refresh_network_info()
        self.update_status("All data refreshed")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = NetworkzeroGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
