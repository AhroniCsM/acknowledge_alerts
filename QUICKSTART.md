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

### Step 3: Run the Script

Pass your API key as a command-line argument:

```bash
python3 acknowledge_alerts.py 'YOUR_API_KEY_HERE'
```

If you're NOT in EU1 region, add the region:

```bash
python3 acknowledge_alerts.py 'YOUR_API_KEY_HERE' 'us1'
```

**Alternative:** Use environment variables (more secure):

```bash
export CORALOGIX_API_KEY='YOUR_API_KEY_HERE'
export CORALOGIX_REGION='eu1'  # optional
python3 acknowledge_alerts.py
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


### Change Time Range

By default, shows alerts from last 24 hours. To change, edit line 186 in `acknowledge_alerts.py`:

```python
by_alert = manager.show_recent_alerts_summary(hours=48)  # Show last 48 hours
```

## 🤖 Automate with Cron

To automatically acknowledge alerts every hour:

```bash
# Edit crontab
crontab -e

# Add this line (adjust path and API key):
0 * * * * cd /path/to/script && echo "yes" | python3 acknowledge_alerts.py 'YOUR_API_KEY' >> /var/log/coralogix_ack.log 2>&1

# Or using environment variables (more secure):
0 * * * * export CORALOGIX_API_KEY='YOUR_API_KEY' && cd /path/to/script && echo "yes" | python3 acknowledge_alerts.py >> /var/log/coralogix_ack.log 2>&1
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

## 🎯 How It Works

The script intelligently filters alerts:
- Shows only RECENT alerts (last 24 hours by default)
- Groups by alert name
- Fast and focused on what matters
- ✅ Perfect for daily operations

## 📝 Files Included

- `acknowledge_alerts.py` - Main script (shows recent alerts only)
- `QUICKSTART.md` - This guide
- `README.md` - Detailed documentation
- `run_acknowledge.sh` - Shell wrapper

---

**Need help?** Check the detailed README.md or contact support.

