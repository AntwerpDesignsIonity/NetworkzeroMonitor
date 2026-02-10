# Changelog

All notable changes to NetworkzeroMonitor will be documented in this file.

## [1.0.0] - 2026-02-10

### Added
- Initial release of NetworkzeroMonitor
- Core network monitoring functionality
  - Ping monitoring with detailed statistics
  - DNS resolution testing with custom DNS server support
  - Internet connectivity checking with quality indicators
  - Network information retrieval (hostname, local IP, public IP)
  
- Command-line interface (CLI)
  - `ping` command for host connectivity testing
  - `dns` command for DNS lookups
  - `status` command for overall network status
  - `pihole` command for Pi-hole monitoring
  - `monitor` command for continuous monitoring
  
- Graphical user interface (GUI)
  - Dashboard tab with network information and connectivity status
  - Ping tab for interactive ping testing
  - DNS Lookup tab for domain resolution
  - Pi-hole tab for Pi-hole integration and monitoring
  - Live Monitor tab for real-time continuous monitoring
  
- Pi-hole integration
  - Status checking
  - Summary statistics (DNS queries, ads blocked, blocking percentage)
  - Top blocked domains list
  - API key support for authenticated access
  
- Setup and launcher scripts
  - `setup.bat` and `setup.sh` for automated environment setup
  - `run_gui.bat` and `run_gui.sh` for quick GUI launch
  - `run_cli.bat` and `run_cli.sh` for CLI access
  
- Documentation
  - Comprehensive README with installation and usage instructions
  - QUICKSTART guide for quick reference
  - EXAMPLES with detailed usage examples
  - Configuration file template (config.ini)
  
- Testing
  - Test suite for validating all core functionality
  - Example scripts for integration
  
- Branding
  - Ionity (Pty) Ltd branding throughout the application
  - Link to www.ionity.today
  
### Notes
- Requires Python 3.8 or higher
- Ping functionality may require administrator/root privileges on some systems
- Pi-hole features require an active Pi-hole instance
- Designed for Windows, Linux, and macOS compatibility

---

*Ionity (Pty) Ltd - www.ionity.today*
