# 🔐 Secrets Setup Guide

**Complete guide for setting up API keys and credentials for Tweet Processor**

**Estimated Time:** 15-30 minutes  
**Difficulty:** Beginner-friendly

---

## 📋 Prerequisites

Before you begin, you'll need accounts with:
1. **Anthropic** (for Claude API) - https://console.anthropic.com/
2. **Google Cloud** (for Google Drive API) - https://console.cloud.google.com/
3. **Twitter/X Developer** (for Twitter API) - https://developer.twitter.com/

---

## 🚀 Quick Setup (5 Minutes)

### **Step 1: Copy Template Files**

```powershell
# Copy environment variables template
cp .env.example .env

# Copy MCP Agent secrets template
cp mcp_agent.secrets.yaml.example mcp_agent.secrets.yaml
```

### **Step 2: Fill in Your API Keys**

Open `.env` in a text editor and replace placeholder values:

```bash
# Replace with your actual Anthropic API key
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-ACTUAL-KEY-HERE

# Replace with your actual Twitter API credentials
TWITTER_API_KEY=YOUR-ACTUAL-KEY-HERE
TWITTER_API_SECRET=YOUR-ACTUAL-SECRET-HERE
TWITTER_ACCESS_TOKEN=YOUR-ACTUAL-TOKEN-HERE
TWITTER_ACCESS_TOKEN_SECRET=YOUR-ACTUAL-TOKEN-SECRET-HERE

# Replace with your Google Drive document ID (see detailed instructions below)
GOOGLE_DRIVE_DOCUMENT_ID=YOUR-DOCUMENT-ID-HERE
```

Open `mcp_agent.secrets.yaml` and replace:

```yaml
anthropic:
  api_key: "sk-ant-api03-YOUR-ACTUAL-KEY-HERE"
```

### **Step 3: Set Up Google Drive Credentials**

See [Detailed Google Drive Setup](#detailed-google-drive-setup) below.

---

## 🔑 Detailed Setup Instructions

### **1. Anthropic API Key**

**Time:** 5 minutes

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create Key**
5. Copy the key (starts with `sk-ant-api03-`)
6. Paste into both:
   - `.env` → `ANTHROPIC_API_KEY=`
   - `mcp_agent.secrets.yaml` → `anthropic.api_key:`

**Security Note:** This key provides access to your Anthropic account. Never share it or commit it to version control.

---

### **2. Twitter/X API Credentials**

**Time:** 10-15 minutes

#### **A. Create Twitter Developer Account**

1. Go to https://developer.twitter.com/
2. Sign up for a developer account (if you don't have one)
3. Complete the application form
4. Wait for approval (usually instant for basic access)

#### **B. Create a Twitter App**

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Click **+ Create Project**
3. Fill in project details:
   - **Project Name:** "Tweet Processor" (or your choice)
   - **Use Case:** "Making a bot" or "Exploring the API"
4. Create an App within the project
5. **App Name:** "Tweet Processor Bot" (must be unique)

#### **C. Generate API Keys**

1. In your app settings, go to **Keys and tokens**
2. **API Key and Secret:**
   - Click **Regenerate** (if needed)
   - Copy **API Key** → `.env` → `TWITTER_API_KEY=`
   - Copy **API Key Secret** → `.env` → `TWITTER_API_SECRET=`

3. **Access Token and Secret:**
   - Click **Generate** under "Access Token and Secret"
   - **IMPORTANT:** Set permissions to **Read and Write**
   - Copy **Access Token** → `.env` → `TWITTER_ACCESS_TOKEN=`
   - Copy **Access Token Secret** → `.env` → `TWITTER_ACCESS_TOKEN_SECRET=`

#### **D. Verify Permissions**

1. Go to **App Settings** → **User authentication settings**
2. Ensure **App permissions** is set to **Read and Write**
3. If not, click **Edit** and change to **Read and Write**
4. **Regenerate** Access Token and Secret after changing permissions

**Troubleshooting:** If you get "403 Forbidden" errors when posting, your access token doesn't have write permissions. Regenerate it with Read and Write permissions.

---

### **3. Google Drive API Setup**

**Time:** 10-15 minutes

#### **A. Create Google Cloud Project**

1. Go to https://console.cloud.google.com/
2. Click **Select a project** → **New Project**
3. **Project name:** "Tweet Processor" (or your choice)
4. Click **Create**

#### **B. Enable Google Drive API**

1. In your project, go to **APIs & Services** → **Library**
2. Search for "Google Drive API"
3. Click **Google Drive API**
4. Click **Enable**

#### **C. Create Service Account**

1. Go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **Service Account**
3. **Service account details:**
   - **Name:** "tweet-processor-drive-reader"
   - **Description:** "Service account for reading newsletter documents"
4. Click **Create and Continue**
5. **Grant this service account access to project:**
   - Skip this step (click **Continue**)
6. **Grant users access to this service account:**
   - Skip this step (click **Done**)

#### **D. Generate Service Account Key**

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON** format
5. Click **Create**
6. A JSON file will download automatically
7. **Rename** the file to `google-drive-credentials.json`
8. **Move** it to the `credentials/` folder in your project

#### **E. Share Google Drive Document**

1. Open your Google Drive document containing newsletter articles
2. Click **Share** button
3. Copy the **service account email** from the JSON file:
   - Look for `"client_email": "tweet-processor-drive-reader@..."`
4. Paste the service account email in the Share dialog
5. Set permission to **Viewer**
6. Click **Send**

#### **F. Get Document ID**

**⚠️ IMPORTANT:** You must configure your own Google Drive document ID. The application will not work without this step.

1. Open your Google Drive document containing newsletter articles
2. Look at the URL in your browser's address bar:
   ```
   https://docs.google.com/document/d/1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t/edit
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                      This part is your Document ID
   ```
3. Copy the Document ID (the long string between `/d/` and `/edit`)
4. Paste into `.env` → `GOOGLE_DRIVE_DOCUMENT_ID=1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t`

**Example:**
- URL: `https://docs.google.com/document/d/1kZMdOrmI5JZR65jvZbzGZ9VKKvGlLqFO/edit`
- Document ID: `1kZMdOrmI5JZR65jvZbzGZ9VKKvGlLqFO`
- In .env: `GOOGLE_DRIVE_DOCUMENT_ID=1kZMdOrmI5JZR65jvZbzGZ9VKKvGlLqFO`

---

## ✅ Verification

### **Test Your Setup**

```powershell
# Test environment variables loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ Anthropic API Key loaded:', bool(os.getenv('ANTHROPIC_API_KEY')))"

# Test Google Drive credentials
python -c "import os; print('✅ Google credentials exist:', os.path.exists('credentials/google-drive-credentials.json'))"

# Run Tweet Processor in preview mode (no posting)
python run_tweet_processor.py --preview
```

**Expected Output:**
- ✅ Environment variables loaded successfully
- ✅ Google Drive document read successfully
- ✅ Articles analyzed successfully
- ✅ Tweets generated successfully

---

## 🔒 Security Best Practices

### **DO:**
- ✅ Keep `.env` and `mcp_agent.secrets.yaml` in `.gitignore`
- ✅ Store credentials in a password manager
- ✅ Rotate API keys regularly (every 3-6 months)
- ✅ Use separate API keys for development and production
- ✅ Set minimum required permissions for each API

### **DON'T:**
- ❌ Commit `.env` or `mcp_agent.secrets.yaml` to Git
- ❌ Share API keys in chat, email, or screenshots
- ❌ Use production API keys for testing
- ❌ Store credentials in cloud storage without encryption
- ❌ Hardcode API keys in source code

---

## 🆘 Troubleshooting

### **"Anthropic API Key not found"**
- Verify `.env` file exists in project root
- Check `ANTHROPIC_API_KEY` is set in `.env`
- Ensure no extra spaces around the `=` sign
- Verify the key starts with `sk-ant-api03-`

### **"Twitter 403 Forbidden"**
- Access token doesn't have write permissions
- Regenerate access token with "Read and Write" permissions
- See [Twitter API Setup Guide](docs/TWITTER_API_SETUP_GUIDE.md)

### **"Google Drive permission denied"**
- Service account email not shared with document
- Share document with service account email (from JSON file)
- Set permission to "Viewer" or higher

### **"Google credentials file not found"**
- Verify file is named `google-drive-credentials.json`
- Verify file is in `credentials/` folder
- Check path in `.env` → `GOOGLE_DRIVE_CREDENTIALS_PATH`

### **"GOOGLE_DRIVE_DOCUMENT_ID environment variable is not set"**
- This error means you haven't configured your Google Drive document ID
- Open `.env` file and set `GOOGLE_DRIVE_DOCUMENT_ID=your_actual_document_id`
- See section "F. Get Document ID" above for detailed instructions
- Make sure you're using your own document ID, not a placeholder value

---

## 📚 Additional Resources

- [Security Guide](SECURITY_GUIDE.md) - Comprehensive security best practices
- [Twitter API Setup Guide](docs/TWITTER_API_SETUP_GUIDE.md) - Detailed Twitter setup
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Deployment options
- [Main README](README.md) - Project overview and usage

---

## 🎯 Next Steps

Once your secrets are set up:

1. **Test in preview mode:**
   ```powershell
   python run_tweet_processor.py --preview
   ```

2. **Generate tweet pipeline:**
   ```powershell
   python run_tweet_processor.py --pipeline
   ```

3. **Review generated tweets:**
   - Check `tweet_pipeline.md` for human-readable schedule
   - Check `all_tweets.json` for all generated tweets

4. **Post your first tweet:**
   ```powershell
   python run_tweet_processor.py --post
   ```

**Happy tweeting! 🐦**

