# Twitter API Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### **Step 1: Get Your Credentials**

Go to: https://developer.twitter.com/en/portal/dashboard

1. **Find your app** (the one with API Key: `[REDACTED-TWITTER-CONSUMER-KEY]`)
2. Click on **"Keys and tokens"** tab
3. **Get API Secret**:
   - Under "Consumer Keys" → Click **"Regenerate"**
   - Copy both API Key and API Secret
4. **Get Access Tokens**:
   - Under "Authentication Tokens" → Click **"Generate"**
   - Copy Access Token and Access Token Secret
5. **Check Permissions**:
   - Must be "Read and Write" (not "Read-only")
   - If you change permissions, regenerate Access Tokens!

---

### **Step 2: Update `.env` File**

Open `.env` and replace the placeholder values:

```bash
TWITTER_API_KEY=your_new_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

**Keep this setting for now:**
```bash
ENABLE_TWITTER_POSTING=false
```

---

### **Step 3: Install Twitter Library**

```bash
pip install tweepy
```

---

### **Step 4: Test Connection**

```bash
python test_twitter_connection.py
```

**Expected output:**
```
✓ TWITTER_API_KEY: 2jokKusE...0UZof
✓ TWITTER_API_SECRET: abc123de...234yz
✓ TWITTER_ACCESS_TOKEN: 12345678...567890
✓ TWITTER_ACCESS_TOKEN_SECRET: xyz987wv...gf210ed
✓ tweepy library installed
✓ OAuth handler created
✓ API client initialized
✓ Successfully authenticated!
✓ Account Details: @your_username
✅ TWITTER API TEST COMPLETE!
```

---

### **Step 5: Test Tweet Generation**

```bash
python run_tweet_processor.py --preview
```

This will:
- ✅ Generate a tweet from your Google Drive document
- ✅ Show you the tweet content
- ✅ NOT post to Twitter (safe!)

---

### **Step 6: Enable Real Posting (When Ready)**

1. **Update `.env`:**
   ```bash
   ENABLE_TWITTER_POSTING=true
   ```

2. **Post your first tweet:**
   ```bash
   python run_tweet_processor.py
   ```

3. **Check Twitter** to see your posted tweet!

---

## 🔍 Troubleshooting

### **"Could not authenticate you"**
→ Regenerate API Key & Secret in Developer Portal

### **"Invalid or expired token"**
→ Regenerate Access Token & Secret in Developer Portal

### **"Read-only application cannot POST"**
→ Change app permissions to "Read and Write", then regenerate Access Tokens

### **"tweepy not installed"**
→ Run: `pip install tweepy`

---

## 📚 Need More Help?

See detailed guide: `docs/TWITTER_API_SETUP_GUIDE.md`

---

## ✅ Checklist

- [ ] Got API Secret from Developer Portal
- [ ] Generated Access Token & Secret
- [ ] Verified app permissions are "Read and Write"
- [ ] Updated `.env` with all 4 credentials
- [ ] Installed tweepy: `pip install tweepy`
- [ ] Tested connection: `python test_twitter_connection.py`
- [ ] Tested tweet generation: `python run_tweet_processor.py --preview`
- [ ] Ready to enable real posting!

