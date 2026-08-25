# Credentials Folder

This folder is reserved for sensitive credential files and is excluded from
version control (only this README is tracked).

## ⚠️ SECURITY WARNING

**NEVER commit credential files in this folder to version control!**

The `.gitignore` file includes:
```
credentials/
credentials/*.json
```

## 📋 Current Status: no files required

**As of January 2026, the Tweet Processor needs no files in this folder.**

The Google Drive integration (and its `google-drive-credentials.json` service
account file) was removed when article sourcing moved to the local
`data/articles.docx` → `data/articles.md` pipeline. All remaining secrets live
in two root-level files, both gitignored:

| Secret | Where it lives |
|--------|----------------|
| Anthropic API key | `.env` (`ANTHROPIC_API_KEY`) and `mcp_agent.secrets.yaml` |
| Twitter/X API credentials (4 values) | `.env` (`TWITTER_*`) |

Set these up by copying the templates: `.env.example` → `.env` and
`mcp_agent.secrets.yaml.example` → `mcp_agent.secrets.yaml`. See
[QUICK_START_GUIDE.md](../QUICK_START_GUIDE.md) and
[docs/TWITTER_API_SETUP_GUIDE.md](../docs/TWITTER_API_SETUP_GUIDE.md).

The folder is kept so that any future integration has a pre-gitignored home
for credential files.

## 🔒 Security Best Practices

1. **Never commit credentials to Git**
   - Always verify `.gitignore` is working: `git check-ignore -v .env`
   - Use `git status` before committing

2. **Backup securely**
   - Store credentials in an encrypted password manager
   - Keep an offline backup in a secure location

3. **Rotate regularly**
   - Rotate the Anthropic key every 3-6 months, and immediately if exposed
   - Regenerate Twitter API tokens if compromised
   - Record the rotation date when you do

4. **Never put real key values in documentation** — use placeholders

5. **Monitor usage**
   - Check the Anthropic Console for unexpected API usage
   - Monitor Twitter API usage in the Developer Portal

## 📚 Additional Resources

- [Twitter API Setup Guide](../docs/TWITTER_API_SETUP_GUIDE.md)
- [Security Guide](../SECURITY_GUIDE.md)
- [Tweet Processor Documentation](../README.md)
