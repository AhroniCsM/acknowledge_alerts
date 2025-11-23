#!/bin/bash
# Quick start script to acknowledge all Coralogix alerts
# 
# Usage:
#   1. Set your environment variables in this file or export them before running
#   2. Run: ./run_acknowledge.sh

# Configuration - API key and region are now hardcoded in the Python script
# You can still override them by exporting environment variables:
# export CORALOGIX_API_KEY="different-key"
# export CORALOGIX_REGION="us1"
# export CORALOGIX_ASSIGN_TO="your-email@example.com"  # Optional

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install requirements if needed
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Installing requirements..."
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
fi

# Run the acknowledgment script
echo "Running Coralogix alert acknowledgment..."
echo ""

python3 "$SCRIPT_DIR/acknowledge_alerts.py"

exit $?

