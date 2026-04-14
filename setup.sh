#!/usr/bin/env bash
# NetworkzeroMonitor - Unix/Linux/macOS Setup Script
# Ionity (Pty) Ltd - www.ionity.today
set -euo pipefail

echo "════════════════════════════════════════════"
echo "  NetworkzeroMonitor  ·  Ionity (Pty) Ltd"
echo "  Setup Script"
echo "════════════════════════════════════════════"
echo ""

# Determine script directory so the venv is created next to the scripts
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Please install Python 3.8 or higher and re-run this script."
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Found Python $PY_VER"

# Create virtual environment
echo ""
echo "Creating virtual environment in ./venv …"
python3 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip…"
pip install --upgrade pip --quiet

# Install dependencies
echo "Installing dependencies from requirements.txt…"
pip install -r requirements.txt --quiet

echo ""
echo "════════════════════════════════════════════"
echo "  Setup complete!"
echo "════════════════════════════════════════════"
echo ""
echo "  Activate the environment:"
echo "    source venv/bin/activate"
echo ""
echo "  Launch the GUI:"
echo "    ./run_gui.sh"
echo ""
echo "  Launch the CLI:"
echo "    ./run_cli.sh --help"
echo ""
