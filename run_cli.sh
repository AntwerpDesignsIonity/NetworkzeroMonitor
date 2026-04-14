#!/usr/bin/env bash
# NetworkzeroMonitor - Launch CLI (Unix/Linux/macOS)
# Ionity (Pty) Ltd - www.ionity.today

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ ! -f "venv/bin/python" ]; then
    echo "Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

exec venv/bin/python networkzero_cli.py "$@"
