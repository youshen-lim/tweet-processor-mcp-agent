# Documentation Index

The complete map of Tweet Processor documentation. Active documents describe the
system as it runs today; everything under `archive/` is historical and carries an
**[ARCHIVED - historical document]** banner.

*Index last updated: August 24, 2026 (project v2.3.1).*

---

## 📗 Active documentation

### At the repository root

| Document | Purpose |
|----------|---------|
| [README.md](../README.md) | Full project documentation: architecture, installation, configuration, usage, content authoring (`.docx` → `.md`) |
| [QUICK_START_GUIDE.md](../QUICK_START_GUIDE.md) | Get running in 30 minutes; weekly automation checklist; updating articles |
| [TROUBLESHOOTING_GUIDE.md](../TROUBLESHOOTING_GUIDE.md) | Diagnosing stalls, Task Scheduler failures, article-sync issues |
| [SECURITY_GUIDE.md](../SECURITY_GUIDE.md) | Sensitive-file inventory, `.gitignore` verification, publishing safety, incident response |
| [TESTING.md](../TESTING.md) | Test suite guide (156 tests), markers, fixtures, coverage |

### In `docs/`

| Document | Purpose |
|----------|---------|
| [TWITTER_API_SETUP_GUIDE.md](TWITTER_API_SETUP_GUIDE.md) | Obtaining all four Twitter/X OAuth 1.0a credentials, permissions, connection check |
| [TWITTER_QUICK_START.md](TWITTER_QUICK_START.md) | Condensed 5-minute version of the Twitter setup |

---

## 📁 Archive (historical)

Historical work reports and guides, kept for project history. **Do not follow
their instructions** — they routinely reference files, features, and statistics
that no longer exist. This directory is excluded from the public GitHub release,
so archive links below only resolve in the private workspace.

### Consolidated retrospectives

| Document | Summary |
|----------|---------|
| [GOOGLE_DRIVE_MIGRATION_RETROSPECTIVE.md](archive/GOOGLE_DRIVE_MIGRATION_RETROSPECTIVE.md) | The single, fact-checked record of the January 2026 Google Drive → local-file migration; replaces eight contemporaneous plan/instruction/report documents (removed Aug 2026, retrievable from git history) |

### `archive/reports/` — work reports, October 2025 – January 2026

**October 2025 — consolidation era**

| Document | Summary |
|----------|---------|
| [SECRETS_SETUP.md](archive/reports/SECRETS_SETUP.md) | Original end-to-end credential setup (Anthropic + Twitter + Google Cloud) |
| [API_KEY_ROTATION_GUIDE.md](archive/reports/API_KEY_ROTATION_GUIDE.md) | Anthropic key rotation runbook (key text redacted Aug 2026; see banner) |
| [WORKSPACE_CLEANUP_COMPLETION_REPORT.md](archive/reports/WORKSPACE_CLEANUP_COMPLETION_REPORT.md) | Removal of 36 legacy files and the vendored mcp-agent copy |
| [MCP_AGENT_UPDATE_VERIFICATION.md](archive/reports/MCP_AGENT_UPDATE_VERIFICATION.md) | Verification of mcp-agent v0.1.34 (superseded; now pinned in requirements.txt) |
| [ARTICLE_ANALYZER_SETUP.md](archive/reports/ARTICLE_ANALYZER_SETUP.md) | Standalone pre-analyzer setup (feature retired July 2026) |
| [WEEKLY_AUTOMATION_STRATEGY.md](archive/reports/WEEKLY_AUTOMATION_STRATEGY.md) | Original weekly cadence design (daily → weekly shift) |
| [URL_BUG_INVESTIGATION_REPORT.md](archive/reports/URL_BUG_INVESTIGATION_REPORT.md) | Investigation of the duplicate-LinkedIn-URL scare |
| [URL_VALIDATION_IMPLEMENTATION_REPORT.md](archive/reports/URL_VALIDATION_IMPLEMENTATION_REPORT.md) | First URL validator implementation (hardcoded 5 articles) |

**January 2026 — migration and hardening era**

| Document | Summary |
|----------|---------|
| [ARTICLE_6_FIX_REPORT.md](archive/reports/ARTICLE_6_FIX_REPORT.md) | Fix for Article #6 arriving empty from the migration (see also the migration retrospective above) |
| [ARTICLE_MANAGEMENT_GUIDE.md](archive/reports/ARTICLE_MANAGEMENT_GUIDE.md) | Article editing under the early local-file setup (superseded by the `.docx` → `.md` flow in the root README) |
| [COMPLETE_WEEKLY_SETUP.md](archive/reports/COMPLETE_WEEKLY_SETUP.md) | Combined weekly automation setup (includes retired analyzer task) |
| [TEST_SUITE_ANALYSIS.md](archive/reports/TEST_SUITE_ANALYSIS.md) | Initial test failure analysis |
| [TEST_IMPLEMENTATION_SUMMARY.md](archive/reports/TEST_IMPLEMENTATION_SUMMARY.md) | Test suite buildout summary |
| [NEXT_STEPS_ACTION_PLAN.md](archive/reports/NEXT_STEPS_ACTION_PLAN.md) | Post-test-buildout action plan |
| [PHASE_2_PRIORITY_2_COMPLETION.md](archive/reports/PHASE_2_PRIORITY_2_COMPLETION.md) | Test remediation phase report |
| [URL_VALIDATOR_DYNAMIC_UPDATE.md](archive/reports/URL_VALIDATOR_DYNAMIC_UPDATE.md) | URL validator made dynamic (removed hardcoded 5-article limit) |
| [STALLING_FIX_REPORT.md](archive/reports/STALLING_FIX_REPORT.md) | Root-cause analysis of production stalls during LLM calls |
| [IMPLEMENTATION_SUMMARY.md](archive/reports/IMPLEMENTATION_SUMMARY.md) | Timeout/heartbeat hardening summary (companion to the stalling report) |

### `archive/google-drive/` — removed integration, January 2026

These documents describe operating the Google Drive article source, removed
January 2026 (the migration itself is covered by the retrospective above):

| Document | Summary |
|----------|---------|
| [ACTION_REQUIRED.md](archive/google-drive/ACTION_REQUIRED.md) | User actions needed during the Drive-era cache incident |
| [GOOGLE_DOCS_API_SETUP.md](archive/google-drive/GOOGLE_DOCS_API_SETUP.md) | Enabling the Google Docs API (tactical fix for the 10 MB export limit) |
| [ARTICLE_CACHE_MANAGEMENT.md](archive/google-drive/ARTICLE_CACHE_MANAGEMENT.md) | Drive-era article cache management |
| [VERIFICATION_SUMMARY.md](archive/google-drive/VERIFICATION_SUMMARY.md) | Drive-era verification results |

---

## Conventions

- **Active docs** state a "Last Updated" date and must match the current code;
  if you find a mismatch, fix the doc or flag it.
- **Archived docs** are frozen: banner them, never update their content, and
  never follow their instructions against the current system.
- **Never put real credential values in any document** — placeholders only
  (see the incident note at the bottom of [SECURITY_GUIDE.md](../SECURITY_GUIDE.md)).
