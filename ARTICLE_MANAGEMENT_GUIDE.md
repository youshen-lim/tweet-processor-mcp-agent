# Article Management Guide (Post-Migration)

**Last Updated:** 2026-01-20  
**Status:** Active (Local File System)

---

## 📋 Overview

After migrating from Google Drive to local file storage, all article management is done through the `data/articles.md` file. This guide explains how to add, edit, and manage articles in the new system.

---

## 🎯 Quick Answer: Where to Add New Articles

**Answer:** Edit `data/articles.md` directly

**DO NOT:**
- ❌ Add articles to Google Drive (no longer used)
- ❌ Create separate article files
- ❌ Modify the .docx backup file

**DO:**
- ✅ Edit `data/articles.md` in your text editor
- ✅ Follow the existing format exactly
- ✅ Commit changes to Git
- ✅ Test with the Tweet Processor

---

## 📝 Adding a New Article (Step-by-Step)

### Step 1: Open the Articles File

```bash
# Open in your preferred editor
code data/articles.md

# Or use any text editor
notepad data/articles.md
```

### Step 2: Scroll to the End of the File

Find the last article (currently Article #15).

### Step 3: Add Your New Article

Copy this template and paste it at the end:

```markdown
---

## Article #16

**Title:** [Your Article Title Here]

**URL:** [Your LinkedIn Article URL Here]

**Content:**

[Paste your article content here. This should be the full text of your article.]

**Metadata:**
- Word Count: [Automatic - will be calculated]
- Status: Active

---
```

### Step 4: Fill in the Details

Replace the placeholders:

- `[Your Article Title Here]` → Your actual article title
- `[Your LinkedIn Article URL Here]` → Full LinkedIn URL
- `[Paste your article content here...]` → Your article text

**Example:**

```markdown
---

## Article #16

**Title:** Understanding Transformer Architecture in Modern AI

**URL:** https://www.linkedin.com/pulse/understanding-transformer-architecture-modern-ai-youshen-wu

**Content:**

The transformer architecture has revolutionized natural language processing since its introduction in 2017. Unlike previous sequential models, transformers process entire sequences simultaneously through self-attention mechanisms...

[Rest of your article content]

**Metadata:**
- Word Count: 2450
- Status: Active

---
```

### Step 5: Save the File

```bash
# Save in your editor (Ctrl+S or Cmd+S)
```

### Step 6: Verify the Format

Run the test script to ensure proper formatting:

```bash
python scripts/test_article_parser.py
```

**Expected Output:**
```
✅ SUCCESS: Found all 16 articles!
```

### Step 7: Commit to Git

```bash
# Add the changes
git add data/articles.md

# Commit with descriptive message
git commit -m "Add Article #16: Understanding Transformer Architecture"

# Push to remote (optional)
git push
```

### Step 8: Test with Tweet Processor

```bash
# Test in preview mode
python run_tweet_processor.py --preview
```

---

## ✏️ Editing Existing Articles

### To Update Article Content:

1. Open `data/articles.md`
2. Find the article by searching for `## Article #N`
3. Edit the content between `**Content:**` and `**Metadata:**`
4. Update the word count if needed
5. Save and commit to Git

### To Update Article URL:

1. Find the article
2. Update the `**URL:**` line
3. Save and commit

### To Update Article Title:

1. Find the article
2. Update the `**Title:**` line
3. Save and commit

**Example Edit:**

```bash
# Open file
code data/articles.md

# Find Article #6 (search for "## Article #6")
# Update the URL or content
# Save (Ctrl+S)

# Commit changes
git add data/articles.md
git commit -m "Fix Article #6: Add missing content and URL"
git push
```

---

## 🔢 Article Numbering Rules

### Current System:
- Articles are numbered sequentially: #1, #2, #3, ..., #15
- **DO NOT skip numbers** (e.g., don't jump from #15 to #17)
- **DO NOT reuse numbers** (e.g., don't create two Article #10s)

### Adding New Articles:
- Always use the next sequential number
- Current last article: #15
- Next article should be: #16

### Deleting Articles:
- **DO NOT delete articles** - mark as inactive instead
- Change `Status: Active` to `Status: Inactive`
- The Tweet Processor will skip inactive articles

**Example:**

```markdown
## Article #6

**Title:** [Title]

**URL:** [URL]

**Content:**

[Content]

**Metadata:**
- Word Count: 0
- Status: Inactive  ← Changed from Active

---
```

---

## 🔄 No Cache Management Needed!

**Good News:** With local file storage, you don't need to manage caches anymore!

### Old System (Google Drive):
```bash
# Had to refresh cache after changes
python refresh_article_cache.py

# Had to clear cache if corrupted
python clear_article_cache.py
```

### New System (Local File):
```bash
# No cache commands needed!
# Just edit data/articles.md and run the workflow
python run_tweet_processor.py --preview
```

**Why?**
- Local file reads are instant (<10ms)
- No caching needed
- Changes take effect immediately
- No cache invalidation issues

---

## 📊 Workflow State Management

The Tweet Processor tracks which article and variation it's currently on in `workflow_state.json`.

### Current State File:

```json
{
  "current_article": 1,
  "current_variation": 1,
  "last_posted": "2026-01-20T10:00:00",
  "total_posts": 45
}
```

### After Adding New Articles:

**No action needed!** The workflow automatically:
- Detects new articles
- Cycles through all active articles
- Skips inactive articles

### To Reset to a Specific Article:

```bash
# Edit workflow_state.json
{
  "current_article": 16,  ← Change this
  "current_variation": 1,
  "last_posted": null,
  "total_posts": 0
}
```

---

## 🚫 What NOT to Do

### ❌ Don't Edit Google Drive

The Google Drive document is **no longer used**. Changes there will **not** be reflected in the Tweet Processor.

### ❌ Don't Create Multiple Article Files

All articles must be in `data/articles.md`. Don't create:
- `data/article_16.md`
- `data/new_articles.md`
- `articles/article_16.md`

### ❌ Don't Modify the .docx Backup

The file `data/articles.md.docx` is a backup only. Don't edit it.

### ❌ Don't Skip Article Numbers

Always use sequential numbering. Don't jump from #15 to #20.

### ❌ Don't Delete Article Sections

Mark as inactive instead of deleting.

---

## ✅ Best Practices

### 1. Always Test After Changes

```bash
# Test parsing
python scripts/test_article_parser.py

# Test workflow
python run_tweet_processor.py --preview
```

### 2. Commit Frequently

```bash
# After each article addition/edit
git add data/articles.md
git commit -m "Descriptive message"
```

### 3. Use Descriptive Commit Messages

```bash
# Good
git commit -m "Add Article #16: Transformer Architecture"
git commit -m "Fix Article #6: Add missing URL"

# Bad
git commit -m "Update"
git commit -m "Changes"
```

### 4. Keep Backups

```bash
# Create periodic backups
cp data/articles.md data/articles_backup_$(date +%Y%m%d).md
```

### 5. Validate Format

Always maintain the exact format:
- `## Article #N` (with space after ##)
- `**Title:**` (with colon)
- `**URL:**` (with colon)
- `**Content:**` (with colon)
- `**Metadata:**` (with colon)
- `---` (separator between articles)

---

## 🔍 Troubleshooting

### Issue: "Articles file not found"

**Solution:**
```bash
# Check file exists
ls data/articles.md

# If missing, re-run migration
python scripts/migrate_from_google_drive.py
```

### Issue: "Failed to parse articles"

**Solution:**
```bash
# Check format with test script
python scripts/test_article_parser.py

# Look for format errors in output
```

### Issue: "Article not showing up in workflow"

**Solution:**
1. Check article status is `Active`
2. Verify article number is sequential
3. Run test script to confirm parsing
4. Check `workflow_state.json` for current article

### Issue: "Word count is 0"

**Solution:**
1. Check content is between `**Content:**` and `**Metadata:**`
2. Ensure there's a blank line after `**Content:**`
3. Ensure there's a blank line before `**Metadata:**`

---

## 📚 Complete Example: Adding Article #16

```bash
# 1. Open file
code data/articles.md

# 2. Scroll to end, add new article
# (Use template from Step 3 above)

# 3. Save file (Ctrl+S)

# 4. Test parsing
python scripts/test_article_parser.py
# Output: ✅ SUCCESS: Found all 16 articles!

# 5. Test workflow
python run_tweet_processor.py --preview
# Output: Successfully generated tweet for Article #1

# 6. Commit to Git
git add data/articles.md
git commit -m "Add Article #16: Understanding Transformer Architecture in Modern AI"
git push

# Done! ✅
```

---

## 🎓 Summary

**To add a new article:**
1. Edit `data/articles.md`
2. Add article at the end using the template
3. Use next sequential number (#16, #17, etc.)
4. Test with `python scripts/test_article_parser.py`
5. Commit to Git

**To edit an existing article:**
1. Edit `data/articles.md`
2. Find article by number
3. Update content/URL/title
4. Test and commit

**Remember:**
- ✅ All changes go in `data/articles.md`
- ✅ No cache management needed
- ✅ Changes take effect immediately
- ✅ Always commit to Git
- ❌ Don't use Google Drive anymore

---

**Questions?** See `MIGRATION_INSTRUCTIONS.md` for more details.

