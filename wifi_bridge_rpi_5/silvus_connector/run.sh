#!/bin/bash

set -e  # Stop on first error

echo "🔄 Installing dependencies..."
sudo apt install -y \
  python3-scapy