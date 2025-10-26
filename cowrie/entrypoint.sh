#!/bin/bash
set -e

# Change to honeypot directory
cd /cowrie

# Create log directory if it doesn't exist
mkdir -p var/log

echo "Starting SSH honeypot with LLM integration..."
exec python3 simple_honeypot.py