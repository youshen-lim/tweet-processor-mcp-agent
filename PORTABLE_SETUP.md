# 🔧 Portable Setup Guide

**Platform-agnostic setup instructions for Tweet Processor MCP Agent**

**Works on:** Windows, macOS, Linux  
**Installation:** Any directory location  
**Time:** 10-15 minutes

---

## 🎯 Overview

This guide helps you set up Tweet Processor to work from **any installation location** on **any operating system** without manual path configuration.

**Key Features:**
- ✅ **Automatic path detection** - No hardcoded paths to edit
- ✅ **Cross-platform compatibility** - Windows, macOS, Linux
- ✅ **Portable installation** - Works from any directory
- ✅ **Easy automation** - Platform-specific scheduling options

---

## 📦 Step 1: Download and Install

### **For Any Installation Location**

```bash
# Clone to any directory you prefer
git clone https://github.com/youshen-lim/tweet-processor-mcp-agent.git

# Examples of valid installation locations:
# Windows: C:\Projects\tweet-processor-mcp-agent
# Windows: D:\MyApps\tweet-processor-mcp-agent
# macOS:   /Users/yourname/Projects/tweet-processor-mcp-agent
# Linux:   /home/yourname/apps/tweet-processor-mcp-agent

# Navigate to your chosen directory
cd tweet-processor-mcp-agent

# Install dependencies
pip install -r requirements.txt
```

---

## 🔑 Step 2: Configure Secrets

### **Copy Template Files**

```bash
# Copy environment variables template
cp .env.example .env

# Copy MCP Agent secrets template
cp mcp_agent.secrets.yaml.example mcp_agent.secrets.yaml
```

### **Configure API Keys**

Edit `.env` file with your actual credentials:

```bash
# Required: Your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-ACTUAL-KEY-HERE

# Required: Your Google Drive document ID (see SECRETS_SETUP.md for how to get this)
GOOGLE_DRIVE_DOCUMENT_ID=your_actual_document_id_here

# Required: Your Twitter API credentials
TWITTER_API_KEY=YOUR-ACTUAL-KEY-HERE
TWITTER_API_SECRET=YOUR-ACTUAL-SECRET-HERE
TWITTER_ACCESS_TOKEN=YOUR-ACTUAL-TOKEN-HERE
TWITTER_ACCESS_TOKEN_SECRET=YOUR-ACTUAL-TOKEN-SECRET-HERE
```

**📖 Detailed Instructions:** See [SECRETS_SETUP.md](SECRETS_SETUP.md) for step-by-step API setup.

---

## 🤖 Step 3: Platform-Specific Automation

### **Windows: Task Scheduler**

**Easy Setup (Recommended):**

```batch
# Copy the portable batch script template
copy run_tweet_processor.bat.template run_tweet_processor.bat

# The script automatically detects its location - no editing needed!
```

**Task Scheduler Configuration:**
1. Open Task Scheduler (`Win + R` → `taskschd.msc`)
2. Create New Task
3. **Actions** → **New** → **Start a program**
4. **Program/script:** `C:\Windows\System32\cmd.exe`
5. **Add arguments:** `/c "path\to\your\tweet-processor-mcp-agent\run_tweet_processor.bat"`
6. **Start in:** `path\to\your\tweet-processor-mcp-agent`

**Example:**
- Add arguments: `/c "C:\Projects\tweet-processor-mcp-agent\run_tweet_processor.bat"`
- Start in: `C:\Projects\tweet-processor-mcp-agent`

---

### **macOS: Multiple Options**

**📖 Detailed Guide:** [macOS Automator Setup](docs/MACOS_AUTOMATOR_SETUP.md)

**Quick Setup:**

```bash
# Copy shell script template
cp run_tweet_processor.sh.template run_tweet_processor.sh
chmod +x run_tweet_processor.sh

# Test it works
./run_tweet_processor.sh
```

**Automation Options:**
1. **Automator + Calendar** (Easiest) - Visual setup with Calendar integration
2. **launchd** (Most reliable) - System-level scheduling
3. **cron** (Traditional) - Unix-style scheduling

**Example cron setup:**
```bash
# Edit crontab
crontab -e

# Add line for every Thursday at 11:30 AM:
30 11 * * 4 /path/to/your/tweet-processor-mcp-agent/run_tweet_processor.sh
```

---

### **Linux: cron or systemd**

**Setup Shell Script:**

```bash
# Copy shell script template
cp run_tweet_processor.sh.template run_tweet_processor.sh
chmod +x run_tweet_processor.sh

# Test it works
./run_tweet_processor.sh
```

**Option 1: cron (Simple)**

```bash
# Edit crontab
crontab -e

# Add line for every Thursday at 11:30 AM:
30 11 * * 4 /path/to/your/tweet-processor-mcp-agent/run_tweet_processor.sh
```

**Option 2: systemd Timer (Advanced)**

Create service file: `/etc/systemd/user/tweet-processor.service`

```ini
[Unit]
Description=Tweet Processor
After=network.target

[Service]
Type=oneshot
ExecStart=/path/to/your/tweet-processor-mcp-agent/run_tweet_processor.sh
WorkingDirectory=/path/to/your/tweet-processor-mcp-agent
```

Create timer file: `/etc/systemd/user/tweet-processor.timer`

```ini
[Unit]
Description=Run Tweet Processor weekly
Requires=tweet-processor.service

[Timer]
OnCalendar=Thu *-*-* 11:30:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable timer:

```bash
systemctl --user enable tweet-processor.timer
systemctl --user start tweet-processor.timer
```

---

## ✅ Step 4: Test Your Setup

### **Manual Test**

```bash
# Test in preview mode (safe - no posting)
python run_tweet_processor.py --preview

# Expected output:
# ✅ Environment variables loaded
# ✅ Google Drive document read
# ✅ Articles analyzed
# ✅ Tweets generated
```

### **Automation Test**

**Windows:**
```batch
# Test batch script manually
run_tweet_processor.bat
```

**macOS/Linux:**
```bash
# Test shell script manually
./run_tweet_processor.sh
```

### **Verify Environment**

```bash
# Check all required files exist
python -c "
import os
files = ['.env', 'mcp_agent.config.yaml', 'run_tweet_processor.py']
for f in files:
    status = '✅' if os.path.exists(f) else '❌'
    print(f'{status} {f}')
"

# Check environment variables
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
vars = ['ANTHROPIC_API_KEY', 'GOOGLE_DRIVE_DOCUMENT_ID', 'TWITTER_API_KEY']
for v in vars:
    status = '✅' if os.getenv(v) else '❌'
    print(f'{status} {v}')
"
```

---

## 🔧 Troubleshooting

### **"GOOGLE_DRIVE_DOCUMENT_ID environment variable is not set"**

**Solution:**
1. Open `.env` file in your installation directory
2. Set `GOOGLE_DRIVE_DOCUMENT_ID=your_actual_document_id`
3. See [SECRETS_SETUP.md](SECRETS_SETUP.md) for how to get your document ID

### **"Python not found" (Windows)**

**Solutions:**
1. **Add Python to PATH** (recommended)
2. **Use py launcher:** Edit batch script to use `py` instead of `python`
3. **Use full path:** Edit batch script with full Python path

### **"Permission denied" (macOS/Linux)**

**Solution:**
```bash
# Make script executable
chmod +x run_tweet_processor.sh

# Check permissions
ls -la run_tweet_processor.sh
```

### **Automation not running**

**Check:**
1. **Paths are correct** in your scheduler configuration
2. **Scripts are executable** (macOS/Linux)
3. **Working directory** is set correctly
4. **Logs** for error messages (check `posting_log.txt`)

---

## 📊 Platform Comparison

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| **Setup Difficulty** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Automation Options** | Task Scheduler | Automator, launchd, cron | cron, systemd |
| **GUI Setup** | ✅ | ✅ (Automator) | ❌ |
| **System-Level Scheduling** | ✅ | ✅ | ✅ |
| **Runs When Logged Out** | ✅ | ✅ (launchd) | ✅ |

---

## 🎯 Next Steps

1. **Choose your platform** and follow the appropriate automation setup
2. **Test thoroughly** with preview mode first
3. **Monitor first few runs** to ensure everything works correctly
4. **Check logs regularly** (`posting_log.txt`) for any issues

**📚 Additional Resources:**
- [SECRETS_SETUP.md](SECRETS_SETUP.md) - Detailed API configuration
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Advanced deployment options
- [docs/MACOS_AUTOMATOR_SETUP.md](docs/MACOS_AUTOMATOR_SETUP.md) - macOS-specific guide
- [README.md](README.md) - Project overview and features

**Happy tweeting! 🐦**
