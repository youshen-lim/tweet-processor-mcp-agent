# Credentials Folder

This folder contains sensitive API credentials and service account keys.

## ⚠️ SECURITY WARNING

**NEVER commit files in this folder to version control!**

The `.gitignore` file should include:
```
credentials/
credentials/*.json
```

## 📋 Required Files

### 1. Google Drive Service Account Credentials

**File:** `google-drive-credentials.json`

**How to obtain:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable Google Drive API
4. Create a Service Account
5. Generate and download JSON key file
6. Rename to `google-drive-credentials.json`
7. Place in this `credentials/` folder
8. Share your Google Drive document with the service account email

**File structure:**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

## 🔒 Security Best Practices

1. **Never commit credentials to Git**
   - Always verify `.gitignore` is working
   - Use `git status` before committing

2. **Backup securely**
   - Store credentials in encrypted password manager
   - Keep offline backup in secure location

3. **Rotate regularly**
   - Regenerate service account keys periodically
   - Update Twitter API tokens if compromised

4. **Limit permissions**
   - Google Service Account: Only grant Drive read access
   - Twitter API: Only enable required permissions

5. **Monitor usage**
   - Check Google Cloud Console for unusual activity
   - Monitor Twitter API usage in Developer Portal

## 📚 Additional Resources

- [Google Drive API Setup Guide](../docs/TWITTER_API_SETUP_GUIDE.md)
- [Security Guide](../SECURITY_GUIDE.md)
- [Tweet Processor Documentation](../README.md)

