# Coralogix Alert Acknowledgment Script

Automatically acknowledge Coralogix alerts using the gRPC API. This script intelligently filters and shows only recent unacknowledged alerts (last 24 hours) to help you manage active incidents efficiently.

## Features

- ✅ Shows only **recent** unacknowledged alerts (last 24 hours)
- ✅ Groups incidents by alert name
- ✅ Displays severity and incident count
- ✅ Batch processing for efficiency
- ✅ Easy configuration - just add your API key
- ✅ Works with all Coralogix regions

## Quick Start

### Prerequisites

1. **Python 3.6+** (already installed on most systems)
2. **grpcurl** - Command-line tool for gRPC

Install grpcurl:

**macOS:**
```bash
brew install grpcurl
```

**Linux:**
```bash
# Download from https://github.com/fullstorydev/grpcurl/releases
```

**Verify installation:**
```bash
grpcurl --version
```

### Setup

1. **Clone this repository:**
```bash
git clone https://github.com/AhroniCsM/acknowledge_alerts.git
cd acknowledge_alerts
```

2. **Get your Coralogix API key:**
   - Log into your Coralogix account
   - Go to **Settings → API Keys**
   - Create or copy an **"Alerts, Rules and Tags API Key"**

3. **Configure the script:**

Open `acknowledge_alerts.py` and update lines 134-135:

```python
DEFAULT_API_KEY = 'your-api-key-here'  # Replace with your key
DEFAULT_REGION = 'eu1'  # Change if needed: us1, us2, eu1, eu2, ap1, ap2, ap3
```

4. **Run the script:**
```bash
python3 acknowledge_alerts.py
```

## Usage Examples

### Basic Usage

```bash
python3 acknowledge_alerts.py
```

The script will:
1. Fetch all unacknowledged incidents from the last 24 hours
2. Group them by alert name
3. Show you a summary with severity and count
4. Ask for confirmation before acknowledging

### Using Environment Variables

Instead of editing the script, you can use environment variables:

```bash
export CORALOGIX_API_KEY='your-api-key'
export CORALOGIX_REGION='eu1'
python3 acknowledge_alerts.py
```

### Change Time Range

Edit line 149 in `acknowledge_alerts.py` to change the time window:

```python
by_alert = manager.show_recent_alerts_summary(hours=48)  # Last 48 hours
```

### Automate with Cron

Run automatically every hour:

```bash
crontab -e
```

Add this line:
```bash
0 * * * * cd /path/to/acknowledge_alerts && echo "yes" | python3 acknowledge_alerts.py >> /var/log/coralogix_ack.log 2>&1
```

## Example Output

```
================================================================================
Coralogix Alert Acknowledgment Script (Filtered)
================================================================================
Region: eu1
Started at: 2025-11-23 10:30:00
================================================================================

Fetching incidents from the last 24 hours...

================================================================================
Found 6 unacknowledged incidents from 6 unique alerts:
================================================================================

[1] KPS not sending metrics to Mimir
    Severity: INCIDENT_SEVERITY_CRITICAL
    Incidents: 1
    Latest: 2025-11-23T15:57:02.356Z

[2] postgres exporters missing metrics
    Severity: INCIDENT_SEVERITY_WARNING
    Incidents: 1
    Latest: 2025-11-23T15:55:01.050Z

[3] rds high cpu or load average
    Severity: INCIDENT_SEVERITY_ERROR
    Incidents: 1
    Latest: 2025-11-23T16:07:02.931Z

... (3 more alerts)

================================================================================
Do you want to acknowledge ALL these incidents? (yes/no): yes

Acknowledging 6 incidents...
  ✓ Acknowledged 6 incidents (Total: 6/6)

================================================================================
Successfully acknowledged: 6
================================================================================
```

## Configuration

### Regions

Available Coralogix regions:

| Region Code | Domain | Description |
|------------|--------|-------------|
| `us1` | coralogix.us | US East (Ohio) |
| `us2` | cx498.coralogix.com | US West (Oregon) |
| `eu1` | coralogix.com | Europe (Ireland) |
| `eu2` | eu2.coralogix.com | Europe (Stockholm) |
| `ap1` | coralogix.in | Asia Pacific (Mumbai) |
| `ap2` | coralogixsg.com | Asia Pacific (Singapore) |
| `ap3` | ap3.coralogix.com | Asia Pacific |

### API Key Permissions

Make sure your API key has **"Alerts, Rules and Tags"** permissions. This allows the script to:
- List incidents
- Acknowledge incidents

## How It Works

1. **Connects to Coralogix** via gRPC API using your API key
2. **Fetches all incidents** with state `INCIDENT_STATE_TRIGGERED`
3. **Filters** for only unacknowledged incidents (status `INCIDENT_STATUS_TRIGGERED`)
4. **Time filters** to show only recent incidents (last 24 hours)
5. **Groups** incidents by alert name for clarity
6. **Batch processes** acknowledgments in groups of 50 for efficiency

## Troubleshooting

### grpcurl not found
```
ERROR: grpcurl is not installed
```
**Solution:** Install grpcurl using `brew install grpcurl` (macOS) or download from the releases page

### Authentication error
```
Code: Unauthenticated
```
**Solution:** Check that:
- Your API key is correct
- The API key has "Alerts, Rules and Tags" permissions
- No extra spaces in the API key

### No incidents found
```
No unacknowledged incidents in the last 24 hours!
```
**Solution:** This is good! It means you have no recent unacknowledged alerts.

### Wrong region
```
Connection error
```
**Solution:** Verify you're using the correct region for your Coralogix account:
- Check your Coralogix URL
- Update `DEFAULT_REGION` in the script

## Files

- `acknowledge_alerts.py` - Main script
- `QUICKSTART.md` - Quick start guide
- `README.md` - This file
- `requirements.txt` - Dependencies info
- `run_acknowledge.sh` - Shell wrapper script

## Technical Details

### Dependencies

- Python 3.6+
- grpcurl (external tool)

No Python packages required - uses only standard library!

### API Endpoints

The script uses the Coralogix gRPC API:
- **Service:** `com.coralogixapis.incidents.v1.IncidentsService`
- **Methods:** `ListIncidents`, `AcknowledgeIncidents`

### Incident States

- `INCIDENT_STATE_TRIGGERED` - Alert is active
- `INCIDENT_STATE_RESOLVED` - Alert is closed

### Incident Status

- `INCIDENT_STATUS_TRIGGERED` - Unacknowledged
- `INCIDENT_STATUS_ACKNOWLEDGED` - Acknowledged (but still active)
- `INCIDENT_STATUS_RESOLVED` - Resolved and closed

## Support

For issues or questions:
- Open an issue on GitHub
- Check the Coralogix documentation
- Verify your API key permissions

## License

MIT License - Feel free to use and modify!

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

---

**Made with ❤️ for Coralogix users**
