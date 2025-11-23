# Quick Start Guide - Coralogix Alert Acknowledgment

Automatically acknowledge all your Coralogix alerts with a single command!

## ⚡ Quick Setup (2 minutes)

### Step 1: Install grpcurl

**macOS:**
```bash
brew install grpcurl
```

**Linux:**
```bash
# Download from https://github.com/fullstorydev/grpcurl/releases
# Or use package manager
```

### Step 2: Get Your API Key

1. Log into your Coralogix account
2. Go to **Settings → API Keys**
3. Create or copy an **"Alerts, Rules and Tags API Key"**

### Step 3: Configure the Script

Open `acknowledge_alerts_filtered.py` and update line 134:

```python
DEFAULT_API_KEY = 'YOUR_API_KEY_HERE'  # Replace with your key
```

If you're NOT in EU1 region, also update line 135:
```python
DEFAULT_REGION = 'eu1'  # Change to: us1, us2, eu1, eu2, ap1, ap2, or ap3
```

### Step 4: Run the Script

```bash
python3 acknowledge_alerts_filtered.py
```

**That's it!** The script will:
- Show you all recent unacknowledged alerts (last 24 hours)
- Ask for confirmation
- Acknowledge them all

## 📋 What You'll See

```
Found 8 unacknowledged incidents from 8 unique alerts:

[1] High CPU Usage
    Severity: INCIDENT_SEVERITY_WARNING
    Incidents: 1
    Latest: 2025-11-23T15:57:02.356Z

[2] Memory Alert
    Severity: INCIDENT_SEVERITY_CRITICAL
    Incidents: 1
    Latest: 2025-11-23T15:55:01.050Z

... (more alerts)

Do you want to acknowledge ALL these incidents? (yes/no): yes

✓ Successfully acknowledged 8 incidents
```

## 🔧 Advanced Options

### Acknowledge ALL Old Incidents (Not Just Recent)

If you want to clean up thousands of old unacknowledged incidents:

```bash
python3 acknowledge_alerts.py
```

**Warning:** This may take a while if you have many incidents.

### Environment Variables (Alternative to Editing Script)

Instead of editing the script, you can use environment variables:

```bash
export CORALOGIX_API_KEY='your-api-key-here'
export CORALOGIX_REGION='eu1'
python3 acknowledge_alerts_filtered.py
```

### Change Time Range

By default, shows alerts from last 24 hours. To change, edit line 149 in `acknowledge_alerts_filtered.py`:

```python
by_alert = manager.show_recent_alerts_summary(hours=48)  # Show last 48 hours
```

## 🤖 Automate with Cron

To automatically acknowledge alerts every hour:

```bash
# Edit crontab
crontab -e

# Add this line (adjust path to your script location):
0 * * * * cd /path/to/script && echo "yes" | python3 acknowledge_alerts_filtered.py >> /var/log/coralogix_ack.log 2>&1
```

## 📞 Troubleshooting

**"grpcurl is not installed"**
→ Install grpcurl (Step 1 above)

**"No unacknowledged incidents found"**
→ Great! You have no recent unacknowledged alerts

**"Authentication error"**
→ Check your API key is correct and has "Alerts, Rules and Tags" permissions

**"Wrong region"**
→ Update `DEFAULT_REGION` to match your Coralogix domain:
  - coralogix.com → eu1
  - coralogix.us → us1
  - eu2.coralogix.com → eu2
  - etc.

## 🎯 What's the Difference?

**acknowledge_alerts_filtered.py** (Recommended)
- Shows only RECENT alerts (last 24 hours)
- Groups by alert name
- Fast and focused
- ✅ Use this for daily operations

**acknowledge_alerts.py** (Bulk cleanup)
- Shows ALL unacknowledged incidents (including very old ones)
- Can process thousands of incidents
- Takes longer
- ✅ Use once for initial cleanup

## 📝 Files Included

- `acknowledge_alerts_filtered.py` - Main script for recent alerts
- `acknowledge_alerts.py` - Bulk acknowledgment script
- `QUICKSTART.md` - This guide
- `README.md` - Detailed documentation

---

**Need help?** Check the detailed README.md or contact support.

