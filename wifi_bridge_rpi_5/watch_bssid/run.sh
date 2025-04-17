#!/bin/bash

set -e  # Stop on first error

# Define a name for the image
IMAGE_NAME="bssid-watcher"

# Go to script directory (optional, if running from crontab or systemd)
cd "$(dirname "$0")"

echo "🛠 Building Docker image..."
docker build -t "$IMAGE_NAME" .

echo "🧹 Cleaning up existing container (if any)..."
docker rm -f "$IMAGE_NAME" 2>/dev/null || true

echo "🚀 Running the container..."
docker run \
  --group-add gpio \
  --device /dev/gpiochip0 \
  --device /dev/gpiochip4 \
  --device /dev/gpiochip10 \
  --device /dev/gpiochip11 \
  --device /dev/gpiochip12 \
  --device /dev/gpiochip13 \
  -v /proc/cpuinfo:/proc/cpuinfo:ro \
  -v /sys:/sys \
  --name "$IMAGE_NAME" \
  --restart unless-stopped \
  -d \
  "$IMAGE_NAME:latest"


