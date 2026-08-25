# Twitter API Setup Guide

## 📋 Overview

This guide will help you obtain all required Twitter API credentials for the Tweet Processor.

---

## 🔑 Required Credentials

You need **4 credentials** to post tweets:

1. ✅ **API Key (Consumer Key)**: `shown under "Consumer Keys" in your app` (Already have)
2. ❓ **API Secret (Consumer Secret)**: Need to obtain
3. ❓ **Access Token**: Need to obtain
4. ❓ **Access Token Secret**: Need to obtain

---

## 🚀 Step-by-Step Instructions

### **Step 1: Access Twitter Developer Portal**

1. Go to: https://developer.twitter.com/en/portal/dashboard
2. Log in with your Twitter account
3. You should see your existing app/project

---

### **Step 2: Find Your App**

1. In the Developer Portal, look for **"Projects & Apps"** in the left sidebar
2. Click on your project name
3. You should see your app listed (the one with API Key: `shown under "Consumer Keys" in your app`)
4. Click on the **app name** or the **gear icon** (⚙️) to access app settings

---

### **Step 3: Get API Secret (Consumer Secret)**

The API Secret was shown **only once** when you first created the app. If you didn't save it:

**Option A: If you saved it originally**
- Find your saved API Secret from when you created the app
- It looks like: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (50 characters)

**Option B: If you lost it - Regenerate Keys**
1. In your app settings, find **"Keys and tokens"** tab
2. Under **"Consumer Keys"** section, you'll see:
   - **API Key**: `shown under "Consumer Keys" in your app` (visible)
   - **API Secret**: `••••••••••••••••••••••••••••••••••••••••••••••••••` (hidden)
3. Click **"Regenerate"** button next to the API Key & Secret
4. ⚠️ **WARNING**: This will invalidate your current API Key!
5. Copy **both** the new API Key and API Secret immediately
6. Update your `.env` file with the new API Key and Secret

**Recommended: Option B** - Regenerate to get both keys fresh

---

### **Step 4: Generate Access Token & Secret**

Access tokens allow your app to post on behalf of your Twitter account.

1. In the **"Keys and tokens"** tab, scroll down to **"Authentication Tokens"** section
2. Look for **"Access Token and Secret"**
3. Click **"Generate"** button (or **"Regenerate"** if tokens already exist)
4. You'll see a popup with:
   - **Access Token**: Starts with your user ID (e.g., `1234567890-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
   - **Access Token Secret**: A long string (e.g., `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
5. **IMPORTANT**: Copy both immediately - they won't be shown again!
6. Click **"Yes, I saved them"** or **"Done"**

---

### **Step 5: Verify App Permissions**

Your app needs **Read and Write** permissions to post tweets.

1. In your app settings, find **"App permissions"** section
2. Check current permission level:
   - ❌ **Read-only**: Cannot post tweets
   - ✅ **Read and Write**: Can post tweets (required)
   - ✅ **Read and Write and Direct Messages**: Can post tweets + DMs
3. If permission is **Read-only**:
   - Click **"Edit"** button
   - Select **"Read and Write"**
   - Click **"Save"**
   - ⚠️ **After changing permissions, you MUST regenerate Access Token & Secret**

---

### **Step 6: Update `.env` File**

Once you have all 4 credentials, update your `.env` file:

```bash
# =============================================================================
# TWITTER CONFIGURATION
# =============================================================================

TWITTER_API_KEY=your_new_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

**Example** (with fake values):
```bash
TWITTER_API_KEY=AbCd1234EfGh5678IjKl9012M
TWITTER_API_SECRET=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
TWITTER_ACCESS_TOKEN=1234567890-AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
TWITTER_ACCESS_TOKEN_SECRET=xyz987wvu654tsr321qpo098nml765kji432hgf210ed
```

---

## 🔍 **What Each Credential Does**

| Credential | Purpose | Format |
|------------|---------|--------|
| **API Key** | Identifies your app | 25 characters (alphanumeric) |
| **API Secret** | Authenticates your app | ~50 characters (alphanumeric) |
| **Access Token** | Identifies your Twitter account | Starts with user ID + hyphen + ~40 chars |
| **Access Token Secret** | Authenticates your account | ~45 characters (alphanumeric) |

---

## 🔐 **Security Best Practices**

1. ✅ **Never commit credentials to Git**
   - The `.env` file is already in `.gitignore`
   - Never share your `.env` file publicly

2. ✅ **Keep credentials secure**
   - Don't share them in screenshots
   - Don't paste them in public forums
   - Store them in a password manager

3. ✅ **Regenerate if compromised**
   - If credentials are exposed, regenerate immediately
   - Update your `.env` file with new credentials

4. ✅ **Use environment-specific credentials**
   - Consider separate apps for testing vs. production
   - Use different credentials for different environments

---

## 🧪 **Testing Your Credentials**

After updating `.env`, test the connection:

```powershell
# Test Twitter API connection (read-only, posts nothing)
python -c "import os, tweepy; from dotenv import load_dotenv; load_dotenv(); c = tweepy.Client(consumer_key=os.getenv('TWITTER_API_KEY'), consumer_secret=os.getenv('TWITTER_API_SECRET'), access_token=os.getenv('TWITTER_ACCESS_TOKEN'), access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')); print('Authenticated as:', c.get_me().data.username)"
```

This will verify:
- ✅ Credentials are valid
- ✅ Authentication works
- ✅ App has correct permissions
- ✅ Can access your Twitter account info

---

## ❓ **Troubleshooting**

### **Error: "Could not authenticate you"**
- **Cause**: Invalid API Key or Secret
- **Solution**: Regenerate Consumer Keys in Developer Portal

### **Error: "Invalid or expired token"**
- **Cause**: Invalid Access Token or Secret
- **Solution**: Regenerate Access Token & Secret in Developer Portal

### **Error: "Read-only application cannot POST"**
- **Cause**: App permissions are Read-only
- **Solution**: 
  1. Change app permissions to "Read and Write"
  2. Regenerate Access Token & Secret (required after permission change)

### **Error: "403 Forbidden"**
- **Cause**: App doesn't have permission to post
- **Solution**: Check app permissions and regenerate tokens

### **Error: "429 Too Many Requests"**
- **Cause**: Rate limit exceeded
- **Solution**: Wait 15 minutes and try again

---

## 📚 **Additional Resources**

- **Twitter Developer Portal**: https://developer.twitter.com/en/portal/dashboard
- **Twitter API Documentation**: https://developer.twitter.com/en/docs/twitter-api
- **Authentication Guide**: https://developer.twitter.com/en/docs/authentication/oauth-1-0a

---

## ✅ **Quick Checklist**

Before proceeding, make sure you have:

- [ ] Logged into Twitter Developer Portal
- [ ] Found your app with API Key: `shown under "Consumer Keys" in your app`
- [ ] Retrieved or regenerated API Secret
- [ ] Generated Access Token & Secret
- [ ] Verified app permissions are "Read and Write"
- [ ] Updated `.env` file with all 4 credentials
- [ ] Kept `ENABLE_TWITTER_POSTING=false` for testing
- [ ] Ready to run the connection check from "Testing Your Credentials" above

---

## 🎯 **Next Steps**

Once you have all credentials:

1. Update `.env` file with all 4 credentials
2. Run the connection check from "Testing Your Credentials" above to verify
3. If test passes, you can enable real posting
4. Run `python run_tweet_processor.py --preview` to test tweet generation
5. When ready, set `ENABLE_TWITTER_POSTING=true` in `.env`
6. Run `python run_tweet_processor.py` to post your first real tweet!

---

**Need help?** Let me know which step you're stuck on!

