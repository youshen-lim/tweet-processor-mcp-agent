# Tweet Processor - Deployment Guide

Complete guide for deploying and running the Tweet Processor on your local Windows laptop.

---

## 📋 Table of Contents

1. [Local Desktop Deployment](#local-desktop-deployment)
2. [Automated Scheduling](#automated-scheduling)
3. [User Interface Options](#user-interface-options)
4. [Security Best Practices](#security-best-practices)
5. [Troubleshooting](#troubleshooting)

---

## 🖥️ Local Desktop Deployment

### **Option 1: Python Environment (Recommended for Development)**

#### **Prerequisites:**
- Python 3.9 or higher
- pip (Python package manager)
- Git (optional, for version control)

#### **Step 1: Install Dependencies**

```bash
# Navigate to project directory
cd "C:\Users\Youshen\Documents\augment-projects\Tweet Processor using LastMile MCP Agent Cloud"

# Install required packages
pip install -r requirements.txt
```

#### **Step 2: Configure Environment Variables**

```bash
# Copy template to create your .env file
copy .env.example .env

# Edit .env with your actual credentials
notepad .env
```

**Required values:**
- `ANTHROPIC_API_KEY` - Your Claude API key
- `GOOGLE_DRIVE_DOCUMENT_ID` - Your newsletter document ID
- `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`

#### **Step 3: Set Up Google Drive Credentials**

```bash
# Create credentials directory (if not exists)
mkdir credentials

# Place your service account JSON file
# File should be: credentials/google-drive-credentials.json
```

#### **Step 4: Test the System**

```bash
# Test preview mode (no posting)
python run_tweet_processor.py --preview

# Test pipeline generation
python run_tweet_processor.py --pipeline

# Review generated pipeline
notepad tweet_pipeline.md
```

#### **Step 5: Enable Production Posting**

```bash
# Edit .env and set:
# ENABLE_TWITTER_POSTING=true

# Run actual posting
python run_tweet_processor.py --post
```

---

### **Option 2: Docker Containerization (Recommended for Production)**

#### **Prerequisites:**
- Docker Desktop for Windows
- Docker Compose (included with Docker Desktop)

#### **Step 1: Build Docker Image**

```bash
# Build the image
docker build -t tweet-processor:latest .

# Verify image created
docker images | findstr tweet-processor
```

#### **Step 2: Create Docker Compose File**

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  tweet-processor:
    image: tweet-processor:latest
    container_name: tweet-processor
    env_file:
      - .env
    volumes:
      - ./credentials:/app/credentials:ro
      - ./workflow_state.json:/app/workflow_state.json
      - ./all_tweets.json:/app/all_tweets.json
      - ./tweet_pipeline.json:/app/tweet_pipeline.json
    restart: unless-stopped
    command: python run_tweet_processor.py --post
```

#### **Step 3: Run Container**

```bash
# Start container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop container
docker-compose down
```

---

### **Option 3: Standalone Executable (Future Enhancement)**

**Current Status:** CLI-only application

**To create .exe (optional):**

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --name TweetProcessor run_tweet_processor.py

# Executable will be in: dist/TweetProcessor.exe
```

**Note:** This creates a CLI executable, not a GUI application.

---

## ⏰ Automated Scheduling

### **Option 1: Windows Task Scheduler (Recommended)**

#### **Step 1: Create Batch Script**

Create `run_tweet_processor.bat`:

```batch
@echo off
REM Tweet Processor - Automated Posting Script

REM Set working directory
cd /d "C:\Users\Youshen\Documents\augment-projects\Tweet Processor using LastMile MCP Agent Cloud"

REM Activate virtual environment (if using one)
REM call venv\Scripts\activate

REM Run tweet processor
python run_tweet_processor.py --post

REM Log completion
echo Tweet posted at %date% %time% >> posting_log.txt
```

#### **Step 2: Configure Task Scheduler**

1. **Open Task Scheduler:**
   - Press `Win + R`
   - Type `taskschd.msc`
   - Press Enter

2. **Create New Task:**
   - Click "Create Task" (not "Create Basic Task")
   - Name: "Tweet Processor - Weekly Posting"
   - Description: "Automatically post tweets every Thursday at 11:30 AM ET"

3. **Configure Triggers:**
   - Click "Triggers" tab → "New"
   - Begin the task: "On a schedule"
   - Settings: "Weekly"
   - Days: Check "Thursday"
   - Start time: "11:30:00 AM"
   - Enabled: ✓

4. **Configure Actions:**
   - Click "Actions" tab → "New"
   - Action: "Start a program"
   - Program/script: `C:\Windows\System32\cmd.exe`
   - Add arguments: `/c "C:\Users\Youshen\Documents\augment-projects\Tweet Processor using LastMile MCP Agent Cloud\run_tweet_processor.bat"`

5. **Configure Conditions:**
   - Uncheck "Start the task only if the computer is on AC power"
   - Check "Wake the computer to run this task" (if desired)

6. **Configure Settings:**
   - Check "Allow task to be run on demand"
   - Check "Run task as soon as possible after a scheduled start is missed"
   - If task fails, restart every: "15 minutes"
   - Attempt to restart up to: "3 times"

7. **Save Task:**
   - Click "OK"
   - Enter your Windows password if prompted

#### **Step 3: Test Scheduled Task**

```bash
# Right-click task in Task Scheduler
# Select "Run"
# Check if tweet was posted
```

---

### **Option 2: Python Scheduling Library**

Create `scheduler.py`:

```python
import schedule
import time
import subprocess
from datetime import datetime

def post_tweet():
    """Run tweet processor"""
    print(f"[{datetime.now()}] Running tweet processor...")
    result = subprocess.run(
        ["python", "run_tweet_processor.py", "--post"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")

# Schedule for Thursday at 11:30 AM ET
schedule.every().thursday.at("11:30").do(post_tweet)

print("Tweet Processor Scheduler Started")
print("Scheduled: Every Thursday at 11:30 AM ET")
print("Press Ctrl+C to stop")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

**Run scheduler:**

```bash
# Install schedule library
pip install schedule

# Run scheduler (keeps running)
python scheduler.py
```

**Keep scheduler running:**
- Use Windows Task Scheduler to start `scheduler.py` at system startup
- Or run in background with `pythonw scheduler.py`

---

### **Option 3: APScheduler (Advanced)**

Create `advanced_scheduler.py`:

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
from datetime import datetime
import pytz

def post_tweet():
    """Run tweet processor"""
    print(f"[{datetime.now()}] Running tweet processor...")
    result = subprocess.run(
        ["python", "run_tweet_processor.py", "--post"],
        capture_output=True,
        text=True
    )
    print(result.stdout)

# Create scheduler
scheduler = BlockingScheduler()

# Schedule for Thursday at 11:30 AM ET
eastern = pytz.timezone('America/New_York')
trigger = CronTrigger(
    day_of_week='thu',
    hour=11,
    minute=30,
    timezone=eastern
)

scheduler.add_job(post_tweet, trigger)

print("Advanced Tweet Processor Scheduler Started")
print("Scheduled: Every Thursday at 11:30 AM ET")
print("Press Ctrl+C to stop")

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    print("\nScheduler stopped")
```

**Run advanced scheduler:**

```bash
# Install APScheduler
pip install apscheduler

# Run scheduler
python advanced_scheduler.py
```

---

## 🎨 User Interface Options

### **Current Status: Command-Line Interface (CLI)**

The Tweet Processor is currently a CLI application. You interact with it through commands:

```bash
# Preview next tweet
python run_tweet_processor.py --preview

# Post next tweet
python run_tweet_processor.py --post

# Generate pipeline
python run_tweet_processor.py --pipeline

# Generate all tweets
python run_tweet_processor.py --generate-all
```

---

### **Future Enhancement: Graphical User Interface (GUI)**

**Option 1: Simple GUI with Tkinter**

Create `gui_app.py`:

```python
import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading

class TweetProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tweet Processor")
        self.root.geometry("800x600")
        
        # Create UI elements
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title = ttk.Label(self.root, text="Tweet Processor", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Buttons
        ttk.Button(button_frame, text="Preview Tweet", command=self.preview_tweet).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Post Tweet", command=self.post_tweet).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate Pipeline", command=self.generate_pipeline).pack(side=tk.LEFT, padx=5)
        
        # Output text area
        self.output = scrolledtext.ScrolledText(self.root, width=90, height=30)
        self.output.pack(pady=10, padx=10)
    
    def run_command(self, args):
        """Run command in background thread"""
        def execute():
            self.output.insert(tk.END, f"\n{'='*80}\n")
            self.output.insert(tk.END, f"Running: {' '.join(args)}\n")
            self.output.insert(tk.END, f"{'='*80}\n\n")
            
            result = subprocess.run(args, capture_output=True, text=True)
            self.output.insert(tk.END, result.stdout)
            if result.stderr:
                self.output.insert(tk.END, f"\nErrors:\n{result.stderr}")
            
            self.output.see(tk.END)
        
        thread = threading.Thread(target=execute)
        thread.start()
    
    def preview_tweet(self):
        self.run_command(["python", "run_tweet_processor.py", "--preview"])
    
    def post_tweet(self):
        self.run_command(["python", "run_tweet_processor.py", "--post"])
    
    def generate_pipeline(self):
        self.run_command(["python", "run_tweet_processor.py", "--pipeline"])

if __name__ == "__main__":
    root = tk.Tk()
    app = TweetProcessorGUI(root)
    root.mainloop()
```

**Run GUI:**

```bash
python gui_app.py
```

**Create GUI executable:**

```bash
pyinstaller --onefile --windowed --name "Tweet Processor" gui_app.py
```

---

**Option 2: Web-Based Dashboard (Advanced)**

Use Flask or Streamlit to create a web interface:

```bash
# Install Streamlit
pip install streamlit

# Create streamlit_app.py (see example below)
# Run web app
streamlit run streamlit_app.py
```

---

## 🔒 Security Best Practices

### **1. Protect Sensitive Files**

**Never commit these files to version control:**
- `.env` (API keys and secrets)
- `credentials/*.json` (Google Drive credentials)
- `workflow_state.json` (may contain cached data)
- `all_tweets.json` (your content)

**Verify .gitignore:**

```bash
# Check if .gitignore exists
type .gitignore

# Test what would be committed
git status
git add .
git status

# If sensitive files appear, add them to .gitignore
```

---

### **2. File Permissions (Windows)**

```bash
# Restrict access to credentials folder
icacls credentials /inheritance:r
icacls credentials /grant:r "%USERNAME%:(OI)(CI)F"

# Restrict access to .env file
icacls .env /inheritance:r
icacls .env /grant:r "%USERNAME%:F"
```

---

### **3. Environment Variable Security**

**Best practices:**
- Never hardcode API keys in code
- Use `.env` file for local development
- Use environment variables for production
- Rotate API keys regularly
- Use read-only API keys when possible

---

### **4. Backup Strategy**

```bash
# Create encrypted backup of credentials
# Use 7-Zip with password protection

# Backup .env
7z a -p -mhe=on env_backup.7z .env

# Backup credentials
7z a -p -mhe=on credentials_backup.7z credentials/

# Store backups in secure location (not in project folder)
```

---

## 🐛 Troubleshooting

### **Issue: Task Scheduler doesn't run**

**Solutions:**
1. Check task history in Task Scheduler
2. Verify batch script path is correct
3. Test batch script manually
4. Check Windows Event Viewer for errors
5. Ensure "Run whether user is logged on or not" is NOT checked (requires password)

---

### **Issue: Python not found**

**Solutions:**
```bash
# Add Python to PATH
# Or use full path in batch script:
"C:\Users\Youshen\AppData\Local\Programs\Python\Python39\python.exe" run_tweet_processor.py --post
```

---

### **Issue: Module not found**

**Solutions:**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Or install specific package
pip install anthropic google-api-python-client tweepy
```

---

## 📚 Additional Resources

- [Windows Task Scheduler Documentation](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)
- [Python Schedule Library](https://schedule.readthedocs.io/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Docker Documentation](https://docs.docker.com/)

---

**Next Steps:**
1. Choose deployment method (Python environment recommended for start)
2. Set up automated scheduling (Windows Task Scheduler recommended)
3. Test thoroughly in preview mode
4. Enable production posting
5. Monitor and maintain

---

**Need Help?** Check the main README.md or create an issue on GitHub.

