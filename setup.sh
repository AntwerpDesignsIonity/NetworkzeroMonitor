#!/bin/bash
# NetworkzeroMonitor Setup Script for Unix/Linux/macOS
# Ionity (Pty) Ltd - www.ionity.today

echo "========================================"
echo "NetworkzeroMonitor Setup"
echo "Ionity (Pty) Ltd"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""
echo "To start the application:"
echo "  1. Run: source venv/bin/activate"
echo "  2. For GUI: python networkzero_gui.py"
echo "  3. For CLI: python networkzero_cli.py --help"
echo ""
