# 🚀 Quick Start Guide - Get Tweet Processor Running in 30 Minutes

**Last Updated:** January 21, 2026
**Status:** Ready for Production

---

## ⚡ 3-Step Quick Start

### **Step 1: Fix Twitter API Permissions (15 min)**

1. Go to: https://developer.twitter.com/en/portal/dashboard
2. Select your app → Settings → User authentication settings → Edit
3. Change permissions from "Read" to **"Read and Write"**
4. Keys and tokens → Regenerate access tokens
5. Copy new tokens and update `.env`:
   ```env
   TWITTER_ACCESS_TOKEN=your-NEW-token
   TWITTER_ACCESS_TOKEN_SECRET=your-NEW-secret
   ```

### **Step 2: Test Tweet Posting (5 min)**

```bash
# Test that everything works
python run_tweet_processor.py --post
```

**Expected Output:**
```
✅ Tweet posted successfully!
   Tweet ID: 1234567890123456789
   Tweet URL: https://twitter.com/YourUsername/status/1234567890123456789
```

### **Step 3: Verify Windows Task Scheduler (10 min)**

1. Press `Win + R` → Type `taskschd.msc` → Enter
2. Find task: "Tweet Processor - Weekly Posting"
3. Right-click → Run (to test)
4. Verify "Next Run Time" shows next Monday at 11:30 AM ET

---

## ✅ Success Checklist

After completing the 3 steps above, verify:

- [ ] ✅ Tweet posted successfully to Twitter
- [ ] ✅ Tweet appears on your Twitter profile
- [ ] ✅ Windows Task Scheduler task runs without errors
- [ ] ✅ Next run time is correct (Monday 11:30 AM ET)
- [ ] ✅ `posting_log.txt` shows successful execution

---

## 🎯 What Happens Next?

### **Automated Weekly Posting:**

Every Monday at 11:30 AM ET, your laptop will:

1. Wake up (if sleeping)
2. Run `run_tweet_processor.bat`
3. Generate next tweet using Claude Sonnet 4.5
4. Post to Twitter
5. Update state for next week
6. Log execution to `posting_log.txt`

### **Content Schedule:**

- **5 articles** × **4 variations** = **20 tweets total**
- **1 tweet per week** = **20 weeks of content** (~5 months)
- After 20 weeks, cycle repeats with Article #1, Variation #1

---

## 📊 Monitoring Your System

### **Check Status Anytime:**
```bash
python run_tweet_processor.py --status
```

### **Preview Next Tweet:**
```bash
python run_tweet_processor.py --preview
```

### **View 3-Week Pipeline:**
```bash
python run_tweet_processor.py --pipeline
```

### **Check Logs:**
- **Execution log:** `posting_log.txt`
- **MCP Agent logs:** `logs/tweet-processor-*.jsonl`
- **State file:** `workflow_state.json`

---

## 🔧 Common Issues & Quick Fixes

### **Issue: Tweet not posting (403 error)**
**Fix:** Twitter permissions not updated
- See Step 1 above
- Must regenerate tokens after changing permissions

### **Issue: Task Scheduler not running**
**Fix:** Check task configuration
- Uncheck "Start only if on AC power"
- Check "Run as soon as possible after missed start"
- Verify path to `run_tweet_processor.bat` is correct

### **Issue: Laptop was off during scheduled time**
**Fix:** Task Scheduler will auto-retry
- Task runs "as soon as possible after missed start"
- Check `posting_log.txt` for execution time

### **Issue: Tweet exceeds 280 characters**
**Fix:** Already handled by URL shortening
- System accounts for Twitter's 23-char URL shortening
- Tweets are validated before posting

---

## 💰 Cost Breakdown

### **Current Setup (Desktop):**
- **Hosting:** $0 (runs on your laptop)
- **Claude Sonnet 4.5:** ~$0.0016 per tweet
- **Twitter API:** Free
- **Total per quarter:** ~$0.021 (13 tweets)

### **Annual Cost:** ~$0.08/year 🎉

---

## 📚 Full Documentation

For detailed information, see:

- **`COMPREHENSIVE_ACTION_PLAN.md`** - Complete deployment guide
- **`TWITTER_API_FIX.md`** - Detailed Twitter setup
- **`MCP_AGENT_CLOUD_REFACTORING_COMPLETE.md`** - Technical details
- **`DEPLOYMENT_GUIDE.md`** - Advanced deployment options

---

## 🆘 Need Help?

### **Quick Diagnostics:**

```bash
# Check Python version
python --version

# Check if all packages installed
pip list | findstr "anthropic mcp-agent tweepy"

# Test local article file access
python -c "from utils.article_parser import ArticleParser; p = ArticleParser(); print(f'Found {len(p.get_all_articles())} articles in data/articles.md')"

# Check current state
python run_tweet_processor.py --status
```

### **Support Resources:**

- **MCP Agent Docs:** https://docs.mcp-agent.com
- **Twitter API Docs:** https://developer.twitter.com/en/docs
- **GitHub Issues:** (if you have a repo)

---

## 🎉 You're All Set!

Your Tweet Processor is now:

✅ **Fully operational** with MCP Agent Cloud framework  
✅ **Using Claude Sonnet 4.5** for best-in-class tweet generation  
✅ **Automated** with Windows Task Scheduler  
✅ **Cost-effective** at ~$0.08/year  
✅ **Reliable** with proper error handling and logging

**Next tweet posts:** Monday, 11:30 AM ET

Sit back and let your AI-powered tweet automation do the work! 🚀

---

**Last Updated:** January 21, 2026
**Framework:** LastMile AI MCP Agent Cloud
**Model:** Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)

