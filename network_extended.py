"""
NetworkzeroMonitor - Extended Network Layers Module
Ionity (Pty) Ltd - www.ionity.today

This module extends the core NetworkMonitor with deeper, full-stack
network details so the mobile app can report everything from the
physical link layer all the way up to GNSS (satellite positioning)
and satellite / cellular wide-area networks.

Sources are probed opportunistically. When the underlying hardware or
helper tool is not available, each probe returns a structured result
with ``available: False`` and a human-readable ``reason`` instead of
raising, so the API and mobile UI can always render a clean state.

Layers covered:
  - Cellular / mobile broadband (2G/3G/4G/5G) via ModemManager (mmcli)
  - Wi-Fi link details (SSID, signal, band) via nmcli / iw
  - Satellite internet (Starlink dish) via reachability + gRPC stats
  - GNSS / satellite positioning (GPS/GLONASS/Galileo/BeiDou) via gpsd
  - A consolidated multi-layer snapshot (link -> IP -> DNS -> WAN -> sat)
"""

import json
import shutil
import socket
import subprocess
import time
from typing import Dict, List, Optional


def _run(cmd: List[str], timeout: int = 6) -> Optional[str]:
    """Run a command, returning stdout on success or None on any failure."""
    if not cmd or shutil.which(cmd[0]) is None:
        return None
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if out.returncode == 0:
            return out.stdout
        return None
    except (subprocess.TimeoutExpired, OSError):
        return None


def _now() -> str:
    return time.strftime('%Y-%m-%d %H:%M:%S')


# Maps ModemManager access technologies to a friendly "generation" label.
_CELL_GENERATION = {
    'gsm': '2G', 'gprs': '2G', 'edge': '2G',
    'umts': '3G', 'hspa': '3G', 'hspa-plus': '3G', 'hspa+': '3G',
    'hsdpa': '3G', 'hsupa': '3G', 'evdo': '3G', '1xrtt': '2G',
    'lte': '4G', 'lte-a': '4G', 'lte-advanced': '4G',
    '5gnr': '5G', 'nr5g': '5G', '5g': '5G',
}


class ExtendedNetworkMonitor:
    """Probes wide-area, wireless and satellite network layers."""

    # Starlink "Dishy" gRPC management endpoint (default on most installs).
    STARLINK_HOST = '192.168.100.1'
    STARLINK_PORT = 9200

    # gpsd default JSON endpoint.
    GPSD_HOST = '127.0.0.1'
    GPSD_PORT = 2947

    # ------------------------------------------------------------------ #
    # Cellular / mobile broadband (2G / 3G / 4G / 5G)
    # ------------------------------------------------------------------ #
    def get_cellular_info(self) -> Dict:
        """
        Report mobile-broadband modems via ModemManager (``mmcli``).

        Returns a dict with ``available`` plus a list of ``modems``,
        each carrying operator, access technology, generation and signal.
        """
        result = {'available': False, 'modems': [], 'timestamp': _now()}

        listing = _run(['mmcli', '-L'])
        if listing is None:
            result['reason'] = 'ModemManager (mmcli) not available or no modem present'
            return result

        modem_paths = [tok for tok in listing.split() if '/Modem/' in tok]
        if not modem_paths:
            result['reason'] = 'No cellular modems detected'
            return result

        for path in modem_paths:
            detail = _run(['mmcli', '-m', path, '-J'])
            modem = self._parse_modem_json(detail) if detail else None
            if modem:
                result['modems'].append(modem)

        result['available'] = bool(result['modems'])
        if not result['available']:
            result['reason'] = 'Modem present but details could not be read'
        return result

    @staticmethod
    def _parse_modem_json(raw: str) -> Optional[Dict]:
        try:
            data = json.loads(raw).get('modem', {})
        except (json.JSONDecodeError, AttributeError):
            return None

        generic = data.get('generic', {})
        access_techs = generic.get('access-technologies', []) or []
        primary_tech = access_techs[0].lower() if access_techs else ''
        signal = generic.get('signal-quality', {}) or {}

        return {
            'manufacturer': data.get('modem', {}).get('manufacturer')
            if isinstance(data.get('modem'), dict) else None,
            'model': generic.get('model') or generic.get('device-identifier'),
            'operator': generic.get('operator-name') or generic.get('operator-code'),
            'state': generic.get('state'),
            'access_technologies': access_techs,
            'generation': _CELL_GENERATION.get(primary_tech, 'Unknown'),
            'signal_percent': int(signal['value']) if str(signal.get('value', '')).isdigit() else None,
            'signal_recent': signal.get('recent') == 'yes',
        }

    # ------------------------------------------------------------------ #
    # Wi-Fi link details
    # ------------------------------------------------------------------ #
    def get_wifi_info(self) -> Dict:
        """Report the active Wi-Fi association via ``nmcli`` (or ``iw``)."""
        result = {'available': False, 'networks': [], 'timestamp': _now()}

        nmcli_out = _run([
            'nmcli', '-t', '-f',
            'ACTIVE,SSID,SIGNAL,FREQ,RATE,SECURITY', 'dev', 'wifi'
        ])
        if nmcli_out is not None:
            for line in nmcli_out.strip().splitlines():
                # nmcli escapes ':' inside fields as '\:'
                parts = line.replace('\\:', '\x00').split(':')
                parts = [p.replace('\x00', ':') for p in parts]
                if len(parts) < 6:
                    continue
                active, ssid, signal, freq, rate, security = parts[:6]
                if active != 'yes':
                    continue
                band = '5 GHz' if freq.startswith('5') or freq.startswith('6') else '2.4 GHz'
                result['networks'].append({
                    'ssid': ssid or '(hidden)',
                    'signal_percent': int(signal) if signal.isdigit() else None,
                    'frequency_mhz': int(freq.split()[0]) if freq.split() else None,
                    'band': band,
                    'rate': rate,
                    'security': security or 'open',
                })
            result['available'] = bool(result['networks'])
            if not result['available']:
                result['reason'] = 'No active Wi-Fi association'
            return result

        result['reason'] = 'Wi-Fi tooling (nmcli) not available'
        return result

    # ------------------------------------------------------------------ #
    # Satellite internet (Starlink "Dishy")
    # ------------------------------------------------------------------ #
    def get_satellite_internet(self) -> Dict:
        """
        Report satellite-internet (Starlink) status.

        First checks reachability of the dish management endpoint, then
        attempts to pull live telemetry via the gRPC API if the optional
        ``grpcurl`` tool is installed. Falls back to a reachability-only
        report when telemetry tooling is absent.
        """
        result = {
            'available': False,
            'provider': 'Starlink',
            'endpoint': f'{self.STARLINK_HOST}:{self.STARLINK_PORT}',
            'timestamp': _now(),
        }

        reachable = self._tcp_reachable(self.STARLINK_HOST, self.STARLINK_PORT, timeout=2)
        result['dish_reachable'] = reachable
        if not reachable:
            result['reason'] = 'Starlink dish endpoint not reachable on this network'
            return result

        telemetry = self._starlink_grpc_status()
        if telemetry:
            result['available'] = True
            result.update(telemetry)
        else:
            # Dish is reachable but we cannot decode telemetry without grpcurl.
            result['available'] = True
            result['telemetry'] = 'unavailable'
            result['reason'] = 'Dish reachable; install grpcurl for live telemetry'
        return result

    def _starlink_grpc_status(self) -> Optional[Dict]:
        endpoint = f'{self.STARLINK_HOST}:{self.STARLINK_PORT}'
        raw = _run([
            'grpcurl', '-plaintext', '-d', '{"get_status":{}}',
            endpoint, 'SpaceX.API.Device.Device/Handle'
        ], timeout=8)
        if raw is None:
            return None
        try:
            status = json.loads(raw).get('dishGetStatus', {})
        except (json.JSONDecodeError, AttributeError):
            return None

        obstruction = status.get('obstructionStats', {}) or {}
        return {
            'state': status.get('deviceState', {}).get('uptimeS') and 'online',
            'uptime_s': status.get('deviceState', {}).get('uptimeS'),
            'downlink_bps': status.get('downlinkThroughputBps'),
            'uplink_bps': status.get('uplinkThroughputBps'),
            'ping_latency_ms': status.get('popPingLatencyMs'),
            'ping_drop_rate': status.get('popPingDropRate'),
            'obstruction_fraction': obstruction.get('fractionObstructed'),
            'hardware_version': status.get('deviceInfo', {}).get('hardwareVersion'),
            'software_version': status.get('deviceInfo', {}).get('softwareVersion'),
        }

    # ------------------------------------------------------------------ #
    # GNSS / satellite positioning
    # ------------------------------------------------------------------ #
    def get_gnss_info(self) -> Dict:
        """
        Report GNSS (GPS/GLONASS/Galileo/BeiDou) positioning via gpsd.

        Connects to the local ``gpsd`` JSON socket and reads a TPV (fix)
        and SKY (satellites-in-view) report. Returns ``available: False``
        with a reason when gpsd or a receiver is not present.
        """
        result = {'available': False, 'timestamp': _now()}

        try:
            sock = socket.create_connection((self.GPSD_HOST, self.GPSD_PORT), timeout=2)
        except OSError:
            result['reason'] = 'gpsd not running / no GNSS receiver on this device'
            return result

        try:
            sock.sendall(b'?WATCH={"enable":true,"json":true};\n')
            sock.settimeout(4)
            tpv, sky = None, None
            buffer = ''
            deadline = time.time() + 5
            while time.time() < deadline and (tpv is None or sky is None):
                try:
                    chunk = sock.recv(8192).decode('utf-8', errors='ignore')
                except socket.timeout:
                    break
                if not chunk:
                    break
                buffer += chunk
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if msg.get('class') == 'TPV' and tpv is None:
                        tpv = msg
                    elif msg.get('class') == 'SKY' and sky is None:
                        sky = msg
        finally:
            try:
                sock.sendall(b'?WATCH={"enable":false};\n')
            except OSError:
                pass
            sock.close()

        if tpv is None and sky is None:
            result['reason'] = 'gpsd reachable but no fix/satellite data yet'
            return result

        result['available'] = True
        if tpv:
            fix_modes = {0: 'unknown', 1: 'no fix', 2: '2D fix', 3: '3D fix'}
            result['fix'] = {
                'mode': fix_modes.get(tpv.get('mode', 0), 'unknown'),
                'latitude': tpv.get('lat'),
                'longitude': tpv.get('lon'),
                'altitude_m': tpv.get('alt'),
                'speed_mps': tpv.get('speed'),
                'track_deg': tpv.get('track'),
                'time': tpv.get('time'),
            }
        if sky:
            sats = sky.get('satellites', []) or []
            result['satellites'] = {
                'in_view': len(sats),
                'used': sum(1 for s in sats if s.get('used')),
                'hdop': sky.get('hdop'),
                'vdop': sky.get('vdop'),
                'pdop': sky.get('pdop'),
                'detail': [
                    {
                        'prn': s.get('PRN'),
                        'constellation': self._gnss_constellation(s.get('gnssid')),
                        'elevation': s.get('el'),
                        'azimuth': s.get('az'),
                        'snr': s.get('ss'),
                        'used': s.get('used', False),
                    }
                    for s in sats
                ],
            }
        return result

    @staticmethod
    def _gnss_constellation(gnssid: Optional[int]) -> str:
        return {
            0: 'GPS', 1: 'SBAS', 2: 'Galileo', 3: 'BeiDou',
            4: 'IMES', 5: 'QZSS', 6: 'GLONASS', 7: 'NavIC',
        }.get(gnssid, 'Unknown')

    # ------------------------------------------------------------------ #
    # Helpers + consolidated snapshot
    # ------------------------------------------------------------------ #
    @staticmethod
    def _tcp_reachable(host: str, port: int, timeout: int = 2) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            reachable = sock.connect_ex((host, port)) == 0
            sock.close()
            return reachable
        except OSError:
            return False

    def get_all_layers(self) -> Dict:
        """
        Return a single consolidated, layered snapshot of every network
        tier this module can probe. Designed for the mobile app's
        "full stack" view.
        """
        return {
            'cellular': self.get_cellular_info(),
            'wifi': self.get_wifi_info(),
            'satellite_internet': self.get_satellite_internet(),
            'gnss': self.get_gnss_info(),
            'timestamp': _now(),
        }


if __name__ == '__main__':
    mon = ExtendedNetworkMonitor()
    print("NetworkzeroMonitor - Extended Layers")
    print("Ionity (Pty) Ltd - www.ionity.today")
    print("=" * 50)
    print(json.dumps(mon.get_all_layers(), indent=2))
