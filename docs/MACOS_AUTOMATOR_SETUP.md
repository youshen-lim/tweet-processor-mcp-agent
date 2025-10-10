# 🍎 macOS Automation Setup Guide

**Complete guide for automating Tweet Processor on macOS using Automator, launchd, and cron**

**Estimated Time:** 15-30 minutes  
**Difficulty:** Beginner to Intermediate

---

## 📋 Prerequisites

Before you begin:
1. ✅ Tweet Processor is installed and working manually
2. ✅ All API keys are configured in `.env` file
3. ✅ You've tested the system with `python run_tweet_processor.py --preview`
4. ✅ You have `run_tweet_processor.sh` script ready (copy from template)

---

## 🎯 Quick Setup (Recommended)

### **Option 1: Automator Calendar Alarm (Easiest)**

**Best for:** Users who want a simple, visual setup with Calendar integration

#### **Step 1: Create Shell Script**

```bash
# Navigate to your project directory
cd /path/to/your/tweet-processor-mcp-agent

# Copy the shell script template
cp run_tweet_processor.sh.template run_tweet_processor.sh

# Make it executable
chmod +x run_tweet_processor.sh

# Test it works
./run_tweet_processor.sh
```

#### **Step 2: Create Automator Application**

1. **Open Automator:**
   - Press `Cmd + Space`
   - Type "Automator"
   - Press Enter

2. **Create New Application:**
   - Choose "Application" when prompted
   - Click "Choose"

3. **Add Shell Script Action:**
   - In the left sidebar, search for "Run Shell Script"
   - Drag "Run Shell Script" to the workflow area

4. **Configure Shell Script:**
   ```bash
   # Replace with your actual path
   /path/to/your/tweet-processor-mcp-agent/run_tweet_processor.sh
   ```

5. **Save Application:**
   - Press `Cmd + S`
   - Name: "Tweet Processor"
   - Location: Applications folder
   - Click "Save"

#### **Step 3: Create Calendar Alarm**

1. **Open Calendar:**
   - Press `Cmd + Space`
   - Type "Calendar"
   - Press Enter

2. **Create New Event:**
   - Click "+" or press `Cmd + N`
   - Title: "Post Weekly Tweet"
   - Date: Next Thursday
   - Time: 11:30 AM (or your preferred time)

3. **Set Recurring:**
   - Click "repeat" dropdown
   - Select "Every Week"

4. **Add Application Alarm:**
   - Click "Add Alert"
   - Change "Message" to "Open File"
   - Click "Choose Application"
   - Select "Tweet Processor" (the app you created)
   - Set timing: "At time of event"

5. **Save Event:**
   - Click "Add" or press `Cmd + S`

**✅ Done!** Your Mac will now automatically run the Tweet Processor every Thursday at 11:30 AM.

---

## ⚙️ Advanced Setup Options

### **Option 2: launchd (System-Level Scheduling)**

**Best for:** Users who want reliable, system-level automation that runs even when not logged in

#### **Step 1: Create launchd Plist File**

Create file: `~/Library/LaunchAgents/com.tweetprocessor.weekly.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tweetprocessor.weekly</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/your/tweet-processor-mcp-agent/run_tweet_processor.sh</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>5</integer>  <!-- Thursday (0=Sunday, 1=Monday, ..., 5=Thursday) -->
        <key>Hour</key>
        <integer>11</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>/path/to/your/tweet-processor-mcp-agent/launchd_output.log</string>
    
    <key>StandardErrorPath</key>
    <string>/path/to/your/tweet-processor-mcp-agent/launchd_error.log</string>
    
    <key>WorkingDirectory</key>
    <string>/path/to/your/tweet-processor-mcp-agent</string>
</dict>
</plist>
```

**Important:** Replace `/path/to/your/tweet-processor-mcp-agent` with your actual installation path.

#### **Step 2: Load and Start launchd Job**

```bash
# Load the job
launchctl load ~/Library/LaunchAgents/com.tweetprocessor.weekly.plist

# Verify it's loaded
launchctl list | grep tweetprocessor

# Test the job manually (optional)
launchctl start com.tweetprocessor.weekly
```

#### **Step 3: Manage launchd Job**

```bash
# Check status
launchctl list com.tweetprocessor.weekly

# Stop the job
launchctl stop com.tweetprocessor.weekly

# Unload the job (to disable)
launchctl unload ~/Library/LaunchAgents/com.tweetprocessor.weekly.plist

# Reload after making changes
launchctl unload ~/Library/LaunchAgents/com.tweetprocessor.weekly.plist
launchctl load ~/Library/LaunchAgents/com.tweetprocessor.weekly.plist
```

---

### **Option 3: cron (Traditional Unix Scheduling)**

**Best for:** Users familiar with Unix/Linux systems who prefer command-line setup

#### **Step 1: Edit Crontab**

```bash
# Open crontab editor
crontab -e
```

#### **Step 2: Add Cron Job**

Add this line to schedule for every Thursday at 11:30 AM:

```bash
# Tweet Processor - Every Thursday at 11:30 AM
30 11 * * 4 /path/to/your/tweet-processor-mcp-agent/run_tweet_processor.sh
```

**Cron Format Explanation:**
```
30 11 * * 4
│  │  │ │ │
│  │  │ │ └── Day of week (0-7, where 0 and 7 are Sunday, 4 is Thursday)
│  │  │ └──── Month (1-12)
│  │  └────── Day of month (1-31)
│  └──────── Hour (0-23)
└────────── Minute (0-59)
```

#### **Step 3: Verify Cron Job**

```bash
# List current cron jobs
crontab -l

# Check cron service is running
sudo launchctl list | grep cron
```

**Note:** On newer macOS versions, you may need to grant Terminal "Full Disk Access" in System Preferences > Security & Privacy > Privacy for cron to work properly.

---

## 🔧 Troubleshooting

### **Issue: "Permission denied" when running script**

**Solution:**
```bash
# Make sure script is executable
chmod +x /path/to/your/tweet-processor-mcp-agent/run_tweet_processor.sh

# Check file permissions
ls -la /path/to/your/tweet-processor-mcp-agent/run_tweet_processor.sh
```

### **Issue: Automator app doesn't run**

**Solutions:**
1. **Check System Preferences:**
   - Go to System Preferences > Security & Privacy > Privacy
   - Click "Automation"
   - Ensure "Tweet Processor" has permission to control other apps

2. **Test manually:**
   - Double-click the Automator app you created
   - Check if it runs successfully

### **Issue: launchd job not running**

**Solutions:**
```bash
# Check if job is loaded
launchctl list | grep tweetprocessor

# Check logs for errors
cat /path/to/your/tweet-processor-mcp-agent/launchd_error.log

# Verify plist syntax
plutil -lint ~/Library/LaunchAgents/com.tweetprocessor.weekly.plist
```

### **Issue: cron job not executing**

**Solutions:**
1. **Check cron logs:**
   ```bash
   # View system logs
   log show --predicate 'process == "cron"' --last 1d
   ```

2. **Grant Full Disk Access:**
   - System Preferences > Security & Privacy > Privacy
   - Click "Full Disk Access"
   - Add Terminal or your shell application

3. **Use absolute paths:**
   ```bash
   # Instead of relative paths, use full paths in crontab
   30 11 * * 4 /usr/bin/python3 /full/path/to/run_tweet_processor.py --post
   ```

---

## 📊 Comparison of Methods

| Method | Ease of Setup | Reliability | User Interface | Runs When Logged Out |
|--------|---------------|-------------|----------------|---------------------|
| **Automator + Calendar** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ |
| **launchd** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ✅ |
| **cron** | ⭐⭐ | ⭐⭐⭐ | ⭐ | ✅ |

**Recommendation:** Start with **Automator + Calendar** for ease of use, then consider **launchd** if you need system-level reliability.

---

## 🎯 Next Steps

1. **Choose your preferred method** from the options above
2. **Test thoroughly** by running manually first
3. **Monitor the first few automated runs** to ensure everything works
4. **Check logs regularly** to catch any issues early

**Happy automating! 🚀**
