# Tweet Processor - Security Guide

Complete guide to protecting sensitive data and securing your Tweet Processor deployment.

---

## 🔒 Table of Contents

1. [Data Exposure Risks](#data-exposure-risks)
2. [Sensitive Files Inventory](#sensitive-files-inventory)
3. [Security Best Practices](#security-best-practices)
4. [GitHub Publishing Security](#github-publishing-security)
5. [Incident Response](#incident-response)

---

## ⚠️ Data Exposure Risks

### **Critical Risk: API Keys and Credentials**

If your API keys are exposed publicly, attackers can:
- **Anthropic API Key:** Consume your Claude API credits (costly!)
- **Twitter API Keys:** Post tweets on your behalf, access DMs, delete content
- **Google Drive Credentials:** Access your Google Drive documents

**Impact:** Financial loss, reputation damage, data breach

---

## 📋 Sensitive Files Inventory

### **🔴 CRITICAL - NEVER EXPOSE THESE FILES**

#### **1. `.env` File**

**Location:** `/.env`

**Contains:**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...
TWITTER_API_KEY=xxxxx...
TWITTER_API_SECRET=xxxxx...
TWITTER_ACCESS_TOKEN=xxxxx...
TWITTER_ACCESS_TOKEN_SECRET=xxxxx...
GOOGLE_DRIVE_DOCUMENT_ID=xxxxx...
```

**Risk Level:** 🔴 **CRITICAL**

**Exposure Impact:**
- Unauthorized API usage → Financial charges
- Unauthorized tweets → Reputation damage
- Access to private documents → Data breach

**Protection:**
- ✅ Listed in `.gitignore`
- ✅ Never commit to Git
- ✅ Never share in screenshots
- ✅ Never paste in chat/email
- ✅ Use `.env.example` template instead

---

#### **2. Google Drive Credentials**

**Location:** `/credentials/google-drive-credentials.json`

**Contains:**
```json
{
  "type": "service_account",
  "project_id": "your-project",
  "private_key_id": "xxxxx...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nxxxxx...",
  "client_email": "your-service-account@project.iam.gserviceaccount.com",
  "client_id": "xxxxx...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

**Risk Level:** 🔴 **CRITICAL**

**Exposure Impact:**
- Full access to Google Drive documents
- Potential access to other Google Cloud resources
- Data exfiltration

**Protection:**
- ✅ Entire `credentials/` folder in `.gitignore`
- ✅ Never commit to Git
- ✅ Store backup in encrypted archive
- ✅ Rotate credentials if exposed

---

### **🟡 MODERATE - SENSITIVE CONTENT**

#### **3. `workflow_state.json`**

**Location:** `/workflow_state.json`

**Contains:**
```json
{
  "current_article": 2,
  "current_variation": 3,
  "last_posted": "2025-10-01T09:34:34.721562",
  "total_posts": 6,
  "articles_cache": [...],
  "analysis_1": {...},
  "analysis_2": {...}
}
```

**Risk Level:** 🟡 **MODERATE**

**Exposure Impact:**
- Reveals your posting schedule
- Contains cached article content
- Contains LLM analysis results
- No direct security risk, but reveals your content strategy

**Protection:**
- ✅ Listed in `.gitignore`
- ⚠️ Consider excluding from public repos
- ✅ Safe to share if you don't mind revealing content

---

#### **4. `all_tweets.json`**

**Location:** `/all_tweets.json`

**Contains:**
```json
{
  "generated_at": "2025-10-01T10:54:07",
  "tweets": [
    {
      "article_number": 1,
      "variation_number": 1,
      "content": "Your tweet content here...",
      "character_count": 243,
      "hashtags": ["#AI", "#Leadership"]
    }
  ]
}
```

**Risk Level:** 🟡 **MODERATE**

**Exposure Impact:**
- Reveals your unpublished tweets
- Someone could copy your content
- Reveals your content strategy

**Protection:**
- ✅ Listed in `.gitignore`
- ⚠️ Exclude from public repos if tweets are unpublished
- ✅ Safe to share after tweets are posted

---

#### **5. `tweet_pipeline.json` & `tweet_pipeline.md`**

**Location:** `/tweet_pipeline.json`, `/tweet_pipeline.md`

**Contains:**
- Scheduled tweets for next 3 weeks
- Article URLs
- Posting schedule

**Risk Level:** 🟡 **MODERATE**

**Exposure Impact:**
- Reveals upcoming content
- Someone could post your tweets before you

**Protection:**
- ✅ Listed in `.gitignore`
- ⚠️ Exclude from public repos
- ✅ Safe to share after tweets are posted

---

### **🟢 LOW RISK - SAFE TO SHARE**

#### **6. Source Code Files**

**Files:** `*.py`, `src/`, `requirements.txt`, `Dockerfile`, `README.md`

**Risk Level:** 🟢 **LOW**

**Safe to share publicly:**
- No sensitive data
- Generic code
- Can be open-sourced

---

## 🛡️ Security Best Practices

### **1. Use `.gitignore` Properly**

**Verify .gitignore is working:**

```bash
# Check what would be committed
git status

# Add all files
git add .

# Check again - sensitive files should NOT appear
git status

# If sensitive files appear, they're not in .gitignore!
```

**Test .gitignore:**

```bash
# Check if file is ignored
git check-ignore -v .env
# Should output: .gitignore:4:.env    .env

git check-ignore -v credentials/google-drive-credentials.json
# Should output: .gitignore:6:credentials/    credentials/google-drive-credentials.json
```

---

### **2. Never Commit Secrets**

**Before first commit:**

```bash
# 1. Create .gitignore FIRST
copy .env.example .env.example
copy .gitignore .gitignore

# 2. Verify .gitignore is working
git add .
git status

# 3. Check for sensitive files
# If you see .env or credentials/, STOP!

# 4. Only commit if safe
git commit -m "Initial commit"
```

---

### **3. Scan for Exposed Secrets**

**Use git-secrets (optional):**

```bash
# Install git-secrets
# https://github.com/awslabs/git-secrets

# Scan repository
git secrets --scan

# Scan history
git secrets --scan-history
```

---

### **4. Rotate Credentials Regularly**

**If you suspect exposure:**

1. **Anthropic API Key:**
   - Go to https://console.anthropic.com/
   - Delete old key
   - Create new key
   - Update `.env`

2. **Twitter API Keys:**
   - Go to https://developer.twitter.com/en/portal/dashboard
   - Regenerate keys
   - Update `.env`

3. **Google Drive Credentials:**
   - Go to Google Cloud Console
   - Delete old service account
   - Create new service account
   - Download new JSON
   - Update `credentials/google-drive-credentials.json`

---

### **5. Secure File Permissions (Windows)**

```bash
# Restrict access to .env
icacls .env /inheritance:r
icacls .env /grant:r "%USERNAME%:F"

# Restrict access to credentials folder
icacls credentials /inheritance:r
icacls credentials /grant:r "%USERNAME%:(OI)(CI)F"

# Verify permissions
icacls .env
icacls credentials
```

---

### **6. Encrypted Backups**

**Create encrypted backup:**

```bash
# Install 7-Zip: https://www.7-zip.org/

# Backup credentials with password
7z a -p -mhe=on credentials_backup.7z credentials/ .env

# Store backup in secure location (NOT in project folder)
# Example: External drive, password manager, encrypted cloud storage
```

---

## 🐙 GitHub Publishing Security

### **Pre-Publishing Checklist**

Before publishing to GitHub, verify:

- [ ] `.gitignore` file exists and is comprehensive
- [ ] `.env.example` template created (no real values)
- [ ] `.env` file is NOT committed
- [ ] `credentials/` folder is NOT committed
- [ ] `workflow_state.json` is NOT committed
- [ ] `all_tweets.json` is NOT committed
- [ ] No API keys in code
- [ ] No hardcoded secrets
- [ ] README.md documents required environment variables
- [ ] Security guide included

---

### **Safe Publishing Workflow**

#### **Option 1: Clean Repository (Recommended)**

```bash
# 1. Create new folder for clean repo
mkdir "C:\Users\Youshen\Documents\tweet-processor-clean"
cd "C:\Users\Youshen\Documents\tweet-processor-clean"

# 2. Initialize Git
git init

# 3. Copy .gitignore FIRST
copy "..\Tweet Processor using LastMile MCP Agent Cloud\.gitignore" .gitignore

# 4. Copy safe files only
copy "..\Tweet Processor using LastMile MCP Agent Cloud\*.py" .
copy "..\Tweet Processor using LastMile MCP Agent Cloud\*.md" .
copy "..\Tweet Processor using LastMile MCP Agent Cloud\requirements.txt" .
copy "..\Tweet Processor using LastMile MCP Agent Cloud\Dockerfile" .
copy "..\Tweet Processor using LastMile MCP Agent Cloud\.env.example" .env.example

# 5. Copy source code
xcopy "..\Tweet Processor using LastMile MCP Agent Cloud\src" src\ /E /I
xcopy "..\Tweet Processor using LastMile MCP Agent Cloud\docs" docs\ /E /I
xcopy "..\Tweet Processor using LastMile MCP Agent Cloud\examples" examples\ /E /I

# 6. Verify no sensitive files
dir /s /b

# 7. Test .gitignore
git add .
git status
# Should NOT see .env, credentials/, workflow_state.json, etc.

# 8. Commit
git commit -m "Initial commit: Tweet Processor"

# 9. Push to GitHub (using GitHub Desktop or command line)
```

---

#### **Option 2: Current Repository (Careful!)**

```bash
# 1. Navigate to current folder
cd "C:\Users\Youshen\Documents\augment-projects\Tweet Processor using LastMile MCP Agent Cloud"

# 2. Verify .gitignore exists
type .gitignore

# 3. Test what would be committed
git add .
git status

# 4. If sensitive files appear, add to .gitignore
notepad .gitignore

# 5. Test again
git reset
git add .
git status

# 6. Only commit if safe
git commit -m "Initial commit: Tweet Processor"
```

---

### **GitHub Repository Settings**

After publishing:

1. **Make repository public or private:**
   - Private: Only you can see it
   - Public: Anyone can see it (ensure no secrets!)

2. **Add repository secrets (for GitHub Actions):**
   - Settings → Secrets and variables → Actions
   - Add: `ANTHROPIC_API_KEY`, `TWITTER_API_KEY`, etc.
   - These are encrypted and not visible in code

3. **Enable security features:**
   - Settings → Security → Enable "Dependency graph"
   - Enable "Dependabot alerts"
   - Enable "Secret scanning" (if available)

---

## 🚨 Incident Response

### **If API Keys Are Exposed**

**Immediate Actions:**

1. **Revoke compromised keys immediately:**
   - Anthropic: https://console.anthropic.com/
   - Twitter: https://developer.twitter.com/en/portal/dashboard
   - Google Cloud: https://console.cloud.google.com/

2. **Generate new keys:**
   - Create new API keys
   - Update `.env` file
   - Test system with new keys

3. **Check for unauthorized usage:**
   - Anthropic: Check usage dashboard
   - Twitter: Check recent tweets
   - Google Cloud: Check audit logs

4. **Remove from Git history (if committed):**

```bash
# Use BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/

# Remove .env from history
bfg --delete-files .env

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (WARNING: Rewrites history)
git push --force
```

5. **Notify affected parties:**
   - If Twitter account compromised, notify followers
   - If data breach, follow legal requirements

---

### **Prevention Checklist**

- [ ] Use `.gitignore` before first commit
- [ ] Never commit `.env` file
- [ ] Never commit `credentials/` folder
- [ ] Use `.env.example` template
- [ ] Scan for secrets before pushing
- [ ] Use encrypted backups
- [ ] Rotate keys regularly
- [ ] Monitor API usage
- [ ] Enable GitHub secret scanning
- [ ] Review commits before pushing

---

## 📚 Additional Resources

- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [git-secrets Tool](https://github.com/awslabs/git-secrets)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)

---

**Remember:** Prevention is easier than recovery. Always verify `.gitignore` before committing!

---

**Last Updated:** October 1, 2025  
**Security Level:** Production-Ready  
**Review Schedule:** Quarterly

