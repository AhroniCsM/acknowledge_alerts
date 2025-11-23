# Coralogix Alert Acknowledgment Script

This script automatically acknowledges all unacknowledged incidents/alerts in your Coralogix account.

## Prerequisites

- Python 3.6 or higher
- Coralogix API Key (Alerts, Rules and Tags API Key)
- **grpcurl** - Command-line tool for gRPC

## Installation

1. Install grpcurl:

**macOS:**
```bash
brew install grpcurl
```

**Linux:**
Download from [grpcurl releases](https://github.com/fullstorydev/grpcurl/releases)

**Verify installation:**
```bash
grpcurl --version
```

2. No Python dependencies required (uses only standard library)

## Usage

### Quick Start (API Key Preconfigured)

The script is preconfigured with your API key and region. By default, it **acknowledges** incidents:

**To ACKNOWLEDGE incidents (default):**
```bash
python3 acknowledge_alerts.py
```

**To RESOLVE incidents:**
```bash
python3 acknowledge_alerts.py "" "" resolve
```

Or use the shell wrapper:
```bash
./run_acknowledge.sh
```

### Method 1: Using Environment Variables (Optional Override)

You can override the default configuration using environment variables:

```bash
export CORALOGIX_API_KEY='different-api-key'
export CORALOGIX_REGION='us1'  # Optional, default: eu1
export CORALOGIX_ACTION='acknowledge'  # Optional, default: acknowledge (can be 'acknowledge' or 'resolve')

python3 acknowledge_alerts.py
```

### Method 2: Using Command-Line Arguments

```bash
python3 acknowledge_alerts.py [api-key] [region] [action]
```

Examples:

**Acknowledge incidents (default):**
```bash
python3 acknowledge_alerts.py
```

**Resolve incidents:**
```bash
python3 acknowledge_alerts.py '' '' resolve
```

**With custom API key:**
```bash
python3 acknowledge_alerts.py 'your-api-key' 'eu1' 'acknowledge'
```

## Configuration

### API Key

The script is already configured with your Coralogix API key and region (eu1).

If you need to use a different API key, you can:
- Override via environment variable: `export CORALOGIX_API_KEY='new-key'`
- Pass as command-line argument: `python3 acknowledge_alerts.py 'new-key'`
- Edit the `DEFAULT_API_KEY` in the script

To get a new API key from Coralogix:
1. Log into your Coralogix account
2. Go to Settings > API Keys
3. Create or use an existing "Alerts, Rules and Tags API Key"

### Regions

Available regions:
- `us1` - US East (Ohio)
- `us2` - US West (Oregon)
- `eu1` - Europe (Ireland) - **Default**
- `eu2` - Europe (Stockholm)
- `ap1` - Asia Pacific (Mumbai)
- `ap2` - Asia Pacific (Singapore)

### Assignment (Optional)

You can optionally assign acknowledged incidents to a specific user by providing their email address.

## What the Script Does

1. Connects to the Coralogix gRPC API
2. Fetches all incidents with state "INCIDENT_STATE_TRIGGERED"
3. Shows you a list of the first 10 incidents to be processed
4. Asks for confirmation before proceeding
5. Processes incidents in batches of 10 (acknowledges or resolves based on your choice)
6. Provides a summary of successful and failed operations

## Difference Between Acknowledge and Resolve

- **Acknowledge**: Marks the incident as acknowledged but keeps it open. The incident state changes from "triggered, unacknowledged" to "triggered, acknowledged"
- **Resolve**: Closes the incident completely. The incident state changes to "resolved"

**Default:** The script uses **acknowledge** by default, which is the most common action for managing active alerts.

## Output

The script provides:
- List of all triggered incidents with details
- Confirmation prompt before resolving
- Progress updates for each batch being resolved
- A final summary showing:
  - Number of successfully resolved incidents
  - Number of failed resolutions
  - Total processed

## Error Handling

- If no API key is provided, the script exits with usage instructions
- If API calls fail, error details are printed
- The script exits with code 1 if any acknowledgments fail

## Example Output

**When Acknowledging (default):**
```
============================================================
Coralogix Alert Acknowledgment Script
============================================================
Region: eu1
Action: acknowledge
Started at: 2025-11-23 10:30:00
============================================================

Fetching all incidents with state: INCIDENT_STATE_TRIGGERED...
Found 5 incidents to acknowledge

Showing first 10 incidents:

[1] Incident Details:
  ID: abc-123
  Alert Name: High CPU Usage
  Created: 2025-11-23T08:15:00Z
  State: INCIDENT_STATE_TRIGGERED

[2] Incident Details:
  ID: def-456
  Alert Name: Memory Alert
  Created: 2025-11-23T09:30:00Z
  State: INCIDENT_STATE_TRIGGERED

... (3 more incidents)

============================================================
Do you want to acknowledge all 5 incidents? (yes/no): yes

============================================================
Acknowledging incidents...

[Batch 1/1] Acknowledging 5 incidents...
  ✓ Successfully acknowledged 5 incidents

============================================================
SUMMARY
============================================================
Successfully acknowledged: 5
Failed to acknowledge: 0
Total processed: 5
Completed at: 2025-11-23 10:30:15
============================================================
```

**When Resolving:**
```bash
python3 acknowledge_alerts.py '' '' resolve
```

Output will be similar but with "resolve" terminology.

## Troubleshooting

### grpcurl Not Found
If you get "grpcurl is not installed" error:
- Install grpcurl using the instructions in the Prerequisites section
- Verify it's in your PATH: `which grpcurl`

### Invalid API Key
If you get authentication errors, verify:
- You're using the correct API key type (Alerts, Rules and Tags API Key)
- The key is valid and not expired
- You're using the correct region

### No Incidents Found
If the script reports 0 incidents:
- Check that you have triggered (unresolved) alerts in the Coralogix UI
- Verify you're connected to the correct team/account

### Connection Errors
If you get connection errors:
- Verify your internet connection
- Check that the region is correct
- Ensure port 443 is not blocked by your firewall
- Ensure the Coralogix gRPC endpoint is accessible from your network

