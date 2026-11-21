# Changelog

All notable changes to this project. Dates are in 2026.

## 2.4.0 (November 20)

### Changed
- An article is re-analyzed automatically when its text changes. Each cached analysis stores a SHA-256 fingerprint of the article text (`content_hash`); whitespace, line-ending, metadata-only and title changes are ignored. Older analyses adopt the current text as their baseline, with no re-analysis.
- A cached analysis is reused only when its stored URL exactly matches the article's URL. An entry with no stored URL is re-analyzed.
- Tests use a temporary state file and never touch the real `workflow_state.json`.
- Added `tzdata` to `requirements.txt`, so `ZoneInfo` can resolve `POSTING_TIMEZONE` on Windows (`--pipeline` previously failed there).
- Rewrote the `Dockerfile` for the current entry point (Python 3.13, non-root user, state and logs in volumes, no secrets in the image) and added an allowlist `.dockerignore`. The image has not been build tested.

### Removed
- `run_tweet_processor_timeout.bat`, which did not work and was not used.

### Documentation corrections
The README was checked against the code and test suite and corrected. These corrections change documentation only.

| Item | Previously stated | Corrected to | Cause |
|------|-------------------|--------------|-------|
| Framework name | MCP Agent Cloud framework | mcp-agent framework | MCP Agent Cloud is LastMile's hosted deployment service. This project does not use it. |
| MCP use | Title and Agent Computer Interface row implied that MCP servers and tools run | No MCP server or tool runs | The `twitter_server.py` wrapper is disabled, and the agents attach no servers. |
| Badge | MCP Agent Cloud | Built with mcp-agent | The project is not deployed on MCP Agent Cloud. |
| Cloud deployment | Deploy to LastMile MCP Agent Cloud for automated scheduling | Not set up or tested | No deployment configuration exists in the repository. |
| Post retries | Retried up to 3 times | Up to 3 attempts in total (2 retries) | `POST_CONNECT_ATTEMPTS = 3` counts attempts, not retries. |
| Duplicate posts | A tweet cannot be posted twice | The retry rule reduces the risk of a duplicate post | The client retries only failures it classifies as before sending, and that classification is a best guess. |
| Status | Production ready | Personal project configured to run weekly | The label was undefined. The project runs weekly on one computer, and the scheduler entry is outside the repository. |
| MCP ecosystem | 100+ MCP servers | Removed | The linked repository does not support the count. |
| Comparison table | Star ratings for mcp-agent and alternatives | Removed | No benchmark or source supports the ratings. |
| Insight count | Extracts 7 insights | Asks for 7 and keeps at most 7 | The model can return fewer than 7. |
| Variations | 4 unique tweet variations | 4 variations, each assigned a different insight (repeats only if fewer than 4 insights) | Tweet uniqueness has not been measured. |
| Cloud costs | No cloud costs | No cloud hosting cost; API charges may apply | The project calls the Anthropic and X APIs. |
| Install time | Installation (5 Minutes) | Installation | X developer access and credential setup can take longer. |
| Discussions link | Start a discussion | Removed | Discussions are disabled on the repository. |
| Limitations | No section | New Limitations section | The README had no limitations section. |

The 212 test count, the per file test counts, the model dates and the dependency bounds were rechecked and are accurate.
