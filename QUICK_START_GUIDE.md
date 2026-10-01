# 🚀 Quick Start Guide - Get Tweet Processor Running in 30 Minutes

**Last Updated:** October 1, 2026
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
4. Verify "Next Run Time" shows the next Monday run for `run_tweet_processor.bat`

---

## ✅ Success Checklist

After completing the 3 steps above, verify:

- [ ] ✅ Tweet posted successfully to Twitter
- [ ] ✅ Tweet appears on your Twitter profile
- [ ] ✅ Windows Task Scheduler task runs without errors
- [ ] ✅ Next run time is correct for the Monday Task Scheduler trigger
- [ ] ✅ `posting_log.txt` shows successful execution

---

## 🎯 What Happens Next?

### **Automated Weekly Posting:**

Every Monday, Windows Task Scheduler will run `run_tweet_processor.bat`. The Task Scheduler trigger is the authoritative schedule for this workspace.

1. Wake up (if sleeping)
2. Run `run_tweet_processor.bat`
3. Generate next tweet using Claude Sonnet 5.5
4. Post to Twitter
5. Update state for next week
6. Log execution to `posting_log.txt`

### **Content Schedule:**

- **23 articles** × **4 variations** = **92 tweets total**
- **1 tweet per week** = **92 weeks of content** (~1.75 years)
- After the last variation, the cycle repeats with Article #1, Variation #1

> Articles are authored in `data/articles.docx` and converted to `data/articles.md`. See [Updating Articles](#-updating-articles) below.

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

## ✍️ Updating Articles

Articles are authored in **`data/articles.docx`** (Word) and converted to **`data/articles.md`**, which is what the app reads. Editing the `.docx` alone is **not enough** unless you let the converter run.

**Author format in `articles.docx`** (per article):
```
Article #N                  (Heading 1)
Article #N Title: <title>
Article #N URL: : <url>
<body paragraphs...>
```

**To publish edits:**
```powershell
# Convert and refresh the cache in one step
python scripts/convert_docx_to_md.py --clear-cache
```

**Or just let automation do it:** the scheduled runners auto-convert when `articles.docx` is newer than `articles.md` (`--if-newer --clear-cache`), so you can simply edit the `.docx` and the next weekly run picks it up. The step is fail-open — if conversion fails, the last-good `articles.md` is used and the result is logged to `posting_log.txt` / `analysis_log.txt`.

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
- **Claude Sonnet 5.5:** ~$0.034 per posted tweet (each article costs ~$0.136 over its 4 weekly runs: one analysis plus 4 tweet-writing calls per run)
- **Twitter API:** Free
- **Total per quarter:** ~$0.44 (13 tweets)

### **Annual Cost:** ~$1.77/year

Figures are measured from a dry run of all 24 articles on 2026-10-01 at Claude API list prices ($2 / $10 per million input / output tokens). Actual per-call usage and cost are logged to `logs/token_usage.jsonl`.

---

## 📚 Full Documentation

For detailed information, see:

- **`README.md`** - Full project documentation and architecture
- **`docs/TWITTER_API_SETUP_GUIDE.md`** - Detailed Twitter setup
- **`TROUBLESHOOTING_GUIDE.md`** - Diagnosing failed runs
- **`SECURITY_GUIDE.md`** - Secrets handling and publishing safety

---

## 🆘 Need Help?

### **Quick Diagnostics:**

```bash
# Check Python version
python --version

# Check if all packages installed
pip list | findstr "anthropic mcp-agent tweepy"

# Test local article file access
python -c "import sys; sys.path.insert(0, 'src'); from parsers.article_parser import ArticleParser; p = ArticleParser(); p.parse(); print(f'Found {p.get_total_articles()} articles in data/articles.md')"

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
✅ **Using Claude Sonnet 5.5** for tweet generation  
✅ **Automated** with Windows Task Scheduler  
✅ **Cost-effective** at ~$1.77/year  
✅ **Reliable** with proper error handling and logging

**Next tweet posts:** Monday, according to the Windows Task Scheduler trigger

Sit back and let your AI-powered tweet automation do the work! 🚀

---

**Last Updated:** October 1, 2026
**Framework:** LastMile AI MCP Agent Cloud
**Model:** Claude Sonnet 5.5 (`claude-sonnet-5-5`, set in `mcp_agent.config.yaml`)
