# 🐦 Tweet Processor - AI-Powered Newsletter-to-Twitter Automation

**Transform your newsletter articles into engaging Twitter/X content using AI and the Model Context Protocol (MCP)**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Agent](https://img.shields.io/badge/MCP-Agent%20Cloud-green.svg)](https://docs.mcp-agent.com/)
[![Claude Sonnet 4.5](https://img.shields.io/badge/Claude-Sonnet%204.5-purple.svg)](https://www.anthropic.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents

1. [Overview](#-overview)
2. [Why MCP Agent Cloud?](#-why-mcp-agent-cloud)
3. [Features](#-features)
4. [Architecture](#-architecture)
5. [Quick Start](#-quick-start)
6. [Installation](#-installation)
7. [Configuration](#-configuration)
8. [Usage](#-usage)
9. [Project Structure](#-project-structure)
10. [Development](#-development)
11. [Deployment](#-deployment)
12. [Troubleshooting](#-troubleshooting)
13. [Contributing](#-contributing)
14. [License](#-license)

---

## 🎯 Overview

Tweet Processor is an intelligent automation system that transforms newsletter articles into engaging Twitter/X content using AI. Built with **LastMile AI's MCP Agent Cloud framework** and **Claude Sonnet 4.5**, it provides a professional, maintainable solution for content automation.

### **What It Does**

- 📄 **Reads** newsletter content from local Markdown files (`data/articles.md`)
- 🧠 **Analyzes** articles using Claude Sonnet 4.5 to extract strategic insights
- ✍️ **Generates** 4 unique tweet variations per article
- 🐦 **Posts** tweets to Twitter/X with professional writing style
- 📅 **Manages** posting schedule and state automatically

### **Who It's For**

- Newsletter creators who want to amplify their content on Twitter
- Content marketers automating social media distribution
- Developers learning AI agent patterns and MCP integration
- Anyone interested in building production-ready AI workflows

---

## 🌟 Why MCP Agent Cloud?

> **Note:** The decision to use MCP Agent Cloud was informed by conversations with **Andrew Hoh**, co-founder of LastMile AI, who shared insights into the powerful capabilities and composable patterns of the framework.

This project uses **LastMile AI's MCP Agent Cloud framework** instead of alternatives like LangChain, direct API calls, or custom frameworks. Here's why:

### **1. Follows Anthropic's "Building Effective Agents" Principles**

Based on [Anthropic's research](https://www.anthropic.com/research/building-effective-agents) (December 2024), the most successful agent implementations use:

- ✅ **Simple, composable patterns** (not complex frameworks)
- ✅ **Clear separation of concerns** (workflows vs agents)
- ✅ **Augmented LLMs with tools** (MCP servers for external services)
- ✅ **Prompt chaining** (content analysis → tweet composition)
- ✅ **Human oversight checkpoints** (manual review before posting)

MCP Agent Cloud implements these patterns natively.

### **2. Model Context Protocol (MCP) Standardization**

**MCP Benefits:**
- **Interoperability**: Any tool exposed by MCP servers works seamlessly
- **Composability**: Chain together local files (read) → Claude (analyze) → Twitter (post)
- **Maintainability**: MCP servers handle API complexity, your code stays clean
- **Future-proof**: As more services adopt MCP, you can integrate them easily

**Current MCP Ecosystem:**
- 100+ MCP servers available (GitHub, Slack, databases, etc.)
- Growing rapidly with community contributions
- Standardized interface across all services

### **3. Comparison with Alternatives**

| Aspect | MCP Agent Cloud | LangChain/LangGraph | Direct API Calls | Custom Framework |
|--------|----------------|---------------------|------------------|------------------|
| **Simplicity** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Composability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Debuggability** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Interoperability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ |
| **Future-proof** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Learning Curve** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

### **4. Production-Ready Patterns**

MCP Agent Cloud implements proven workflow patterns:

| Pattern | Implementation | Benefit |
|---------|---------------|---------|
| **Augmented LLM** | Claude Sonnet 4.5 with MCP tools | Tool-using AI with external capabilities |
| **Prompt Chaining** | Analysis → Composition → Posting | Break complex task into manageable steps |
| **Agent-Computer Interface** | Well-documented MCP tools | Clear, reliable tool usage |
| **State Management** | `workflow_state.json` | Track progress, cache analyses |
| **Human-in-the-Loop** | Manual review mode | Safety and quality control |

### **5. Cost Optimization**

Smart caching reduces API costs by **75%**:
- Article analyses are cached in `workflow_state.json`
- Reused across 4 tweet variations
- Only re-analyze when article content changes

---

## ✨ Features

### 🤖 **Intelligent Content Generation**
- **AI-Powered Analysis**: Extracts 7 high-level, strategic insights from newsletter articles
- **Professional Writing Style**: Active voice, no abbreviations, no hyphens, capitalize after semicolons
- **Variation System**: Creates 4 unique tweet variations per article, each highlighting a different insight
- **Smart Rotation**: Automatically cycles through articles and variations

### 📅 **Flexible Scheduling & Preview**
- **Pipeline Preview**: Generate and review 3 weeks of scheduled tweets before posting
- **Customizable Schedule**: Configure posting day, time, and timezone
- **Manual Review Mode**: Preview and approve tweets before they go live
- **State Management**: Tracks posting history and automatically advances to next variation

### 🔗 **Seamless Integrations**
- **Local Files**: Reads newsletter content from local Markdown files (`data/articles.md`)
- **Twitter/X API**: Posts tweets automatically with OAuth 1.0a authentication via MCP server
- **Multi-LLM Support**: Works with both Anthropic Claude and OpenAI models
- **MCP Extensibility**: Easy to add new integrations (Slack, GitHub, databases, etc.)

### 🛡️ **Safe & Reliable**
- **Preview Mode**: Test tweet generation without posting
- **Simulated Posting**: Validate workflow before enabling live posting
- **Character Limit Enforcement**: Ensures tweets stay within Twitter's 280-character limit
- **Error Handling**: Graceful failure recovery with detailed logging
- **Secrets Management**: Secure handling of API keys and credentials

---

## 🏗️ Architecture

### **System Overview**

```
Windows Desktop Application
├── Manual Execution (run_tweet_processor.py)
├── MCP Agent Cloud Framework
│   ├── MCPApp (application container)
│   ├── AnthropicAugmentedLLM (Claude Sonnet 4.5)
│   └── MCP Servers (Twitter)
├── Agents
│   ├── MCPContentAnalyzerAgent (extract insights)
│   └── MCPTweetComposerAgent (generate tweets)
└── Workflow
    └── MCPTweetProcessorWorkflow (orchestration)
```

### **Workflow Steps**

```
Step 1: Read Document (Local Files)
   ↓
Step 2: Parse Articles
   ↓
Step 3: Analyze Content (Claude Sonnet 4.5)
   ↓  Extract 7 strategic insights per article
   ↓  Cache analysis in workflow_state.json
   ↓
Step 4: Compose Tweet (Claude Sonnet 4.5)
   ↓  Generate 4 variations (1 per insight)
   ↓  Enforce professional writing style
   ↓  Ensure 280-character limit
   ↓
Step 5: Post Tweet (Twitter MCP)
   ↓  Manual review or auto-post
   ↓  Update state for next variation
   ↓
Step 6: State Management
   ↓  Track current article/variation
   ↓  Log posting history
```

### **Key Design Principles**

- **Insight Uniqueness**: Each variation highlights a DIFFERENT key insight
- **Title Exclusion**: Tweets focus on content insights, not article titles
- **Strategic Focus**: Emphasizes "why it matters" over "what it is"
- **Character Optimization**: Aggressive enforcement of 280-character limit
- **Caching**: Stores article analysis to avoid redundant API calls (75% cost reduction)

---

## 🚀 Quick Start

### **Prerequisites**

- **Python 3.10+** (Python 3.13 recommended)
- **Twitter Developer Account** with API credentials
- **Anthropic API key** (for Claude Sonnet 4.5)

### **Installation (5 Minutes)**

```powershell
# 1. Clone the repository
git clone https://github.com/youshen-lim/tweet-processor-mcp-agent.git
cd tweet-processor-mcp-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up secrets
cp .env.example .env
cp mcp_agent.secrets.yaml.example mcp_agent.secrets.yaml
# Edit .env and mcp_agent.secrets.yaml with your API keys

# 4. Test the system
python run_tweet_processor.py --preview
```

**Detailed Setup:** See [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) for step-by-step instructions.

---

## 📦 Installation

### **1. Clone Repository**

```powershell
git clone https://github.com/youshen-lim/tweet-processor-mcp-agent.git
cd tweet-processor-mcp-agent
```

### **2. Install Dependencies**

```powershell
pip install -r requirements.txt
```

**Dependencies:**
- `mcp>=1.13.1` - Model Context Protocol SDK
- `mcp-agent>=0.1.34` - MCP Agent Cloud framework
- `fastmcp>=2.12.4` - FastMCP framework for MCP servers
- `anthropic>=0.48.0` - Claude API client
- `tweepy>=4.14.0` - Twitter API client
- `python-dotenv` - Environment variable management
- `python-docx>=1.1.0` - Word document parsing (`articles.docx` → `articles.md` converter)
- `pytest>=8.0.0` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-mock` - Mock utilities

### **3. Set Up Secrets**

See [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) for complete instructions.

**Quick Setup:**
```powershell
cp .env.example .env
cp mcp_agent.secrets.yaml.example mcp_agent.secrets.yaml
# Edit both files with your actual API keys
```

---

## ⚙️ Configuration

### **Environment Variables (.env)**

```bash
# LLM Provider
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# Twitter API
TWITTER_API_KEY=YOUR-API-KEY
TWITTER_API_SECRET=YOUR-API-SECRET
TWITTER_ACCESS_TOKEN=YOUR-ACCESS-TOKEN
TWITTER_ACCESS_TOKEN_SECRET=YOUR-ACCESS-TOKEN-SECRET

# Posting Configuration
# These values are used for previews/pipeline output. The actual automated run
# cadence is controlled by Windows Task Scheduler, which runs run_tweet_processor.bat.
ENABLE_TWITTER_POSTING=false
POSTING_DAY=Monday
POSTING_TIME=11:30
POSTING_TIMEZONE=America/New_York
```

### **MCP Agent Configuration (mcp_agent.config.yaml)**

```yaml
execution:
  engine: asyncio

logger:
  level: INFO
  transports:
    - type: file
      filename: logs/mcp_agent.log
    - type: console

mcp_servers:
  twitter:
    command: python
    args: ["src/mcp_servers/twitter_server.py"]

model:
  provider: anthropic
  name: claude-sonnet-4-5-20250929
```

---

## 🎯 Usage

### **Command-Line Interface**

```powershell
# Preview next tweet (safe - doesn't update state or post)
python run_tweet_processor.py --preview

# Generate 3-week pipeline of scheduled tweets
python run_tweet_processor.py --pipeline

# Generate next tweet and update state (manual review)
python run_tweet_processor.py

# Post tweet to Twitter (requires ENABLE_TWITTER_POSTING=true)
python run_tweet_processor.py --post

# Show current workflow state
python run_tweet_processor.py --status
```

### **Workflow Modes**

**Preview Mode** (Recommended for Testing)
- Generates next tweet without updating state or posting
- Safe for testing and development

**Pipeline Mode** (Recommended for Planning)
- Generates next 3 weeks of scheduled tweets
- Saves to `tweet_pipeline.json` and `tweet_pipeline.md`
- Allows review and editing before posting

**Manual Review Mode** (Default)
- Generates next tweet and updates state
- Does NOT post to Twitter (manual posting required)

**Auto-Post Mode**
- Generates and posts tweet automatically
- Requires `ENABLE_TWITTER_POSTING=true` in `.env`

---

## 📁 Project Structure

```
tweet-processor-mcp-agent/
├── run_tweet_processor.py          # Main entry point (--post, --preview, --pipeline, --status)
├── run_tweet_processor.bat         # Windows Task Scheduler automation
├── run_tweet_processor_timeout.bat # Timeout-protected runner (10 min)
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Test configuration
├── .env.example                    # Environment variables template
├── mcp_agent.config.yaml           # MCP Agent configuration
├── mcp_agent.secrets.yaml.example  # Secrets template
├── workflow_state.json.example     # Example state file
├── Dockerfile                      # Container deployment
├── LICENSE                         # MIT License
├── README.md                       # This file
├── QUICK_START_GUIDE.md            # Quick start guide
├── TESTING.md                      # Test suite documentation
├── TROUBLESHOOTING_GUIDE.md        # Troubleshooting guide
├── SECURITY_GUIDE.md               # Security best practices
├── src/
│   ├── agents/
│   │   ├── mcp_content_analyzer_agent.py  # 7 strategic insights extraction
│   │   └── mcp_tweet_composer_agent.py    # 4 tweet variations per article
│   ├── workflows/
│   │   └── mcp_tweet_processor_workflow.py # Core orchestration engine
│   ├── parsers/
│   │   ├── __init__.py
│   │   └── article_parser.py              # Local Markdown article parser
│   ├── mcp_servers/
│   │   └── twitter_server.py              # Twitter API v2 client
│   └── utils/
│       ├── __init__.py
│       ├── url_validator.py               # LinkedIn URL validation
│       ├── api_timeout_handler.py         # 90s timeouts + retry with backoff
│       └── heartbeat_monitor.py           # Stall detection (3-min threshold)
├── tests/                          # 128 tests, 100% pass rate
│   ├── conftest.py                 # Reusable test fixtures
│   ├── test_article_parser.py      # 23 tests
│   ├── test_tweet_composer.py      # 23 tests
│   ├── test_url_validator.py       # 26 tests
│   ├── test_edge_cases.py          # 22 tests
│   ├── test_workflow_integration.py # 14 tests
│   ├── test_workflow_state.py      # 8 tests
│   ├── test_url_integrity.py       # 7 tests
│   └── test_integration_workflow.py # 5 tests
├── data/
│   ├── articles.docx               # Source articles (authored in Word)
│   └── articles.md                 # Generated from articles.docx (read by the app)
├── scripts/
│   ├── convert_docx_to_md.py       # articles.docx → articles.md converter (--if-newer, --clear-cache, --dry-run)
│   ├── clear_article_cache.py      # Empty articles_cache in workflow_state.json
│   └── sync_publish.py             # Sync publish/ public copy from root HEAD (--dry-run, --push)
├── credentials/
│   └── README.md                   # Credentials setup guide
├── docs/
│   ├── TWITTER_API_SETUP_GUIDE.md
│   └── TWITTER_QUICK_START.md
├── tools/
│   └── document_analyzer.py        # Document validation utility
├── examples/
│   └── sample_tweet_generation.py  # Usage example
└── logs/                           # (gitignored)
```

---

## 💻 Development

### **Setting Up Development Environment**

```powershell
# Clone repository
git clone https://github.com/youshen-lim/tweet-processor-mcp-agent.git
cd tweet-processor-mcp-agent

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up secrets (see SECRETS_SETUP.md)
cp .env.example .env
cp mcp_agent.secrets.yaml.example mcp_agent.secrets.yaml
```

### **Testing**

```powershell
# Run the full test suite (128 tests)
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_article_parser.py -v
python -m pytest tests/test_workflow_integration.py -v
python -m pytest tests/test_edge_cases.py -v

# Test with preview mode (safe - no posting)
python run_tweet_processor.py --preview

# Generate test pipeline
python run_tweet_processor.py --pipeline
```

See [TESTING.md](TESTING.md) for complete test documentation.

### **Code Structure**

**Agents** (`src/agents/`):
- `mcp_content_analyzer_agent.py` - Analyzes articles and extracts 7 strategic insights
- `mcp_tweet_composer_agent.py` - Composes tweets with professional writing style

**Workflows** (`src/workflows/`):
- `mcp_tweet_processor_workflow.py` - Orchestrates the entire tweet generation process

**Parsers** (`src/parsers/`):
- `article_parser.py` - Parses local Markdown files into structured Article objects

**MCP Servers** (`src/mcp_servers/`):
- `twitter_server.py` - Twitter API v2 client with URL length calculation

**Utilities** (`src/utils/`):
- `url_validator.py` - LinkedIn URL format validation and uniqueness checks
- `api_timeout_handler.py` - 90-second async timeouts with retry and exponential backoff
- `heartbeat_monitor.py` - Thread-based stall detection with 3-minute threshold

### **Adding New Features**

**Example: Add a new MCP server**

1. Create new server file in `src/mcp_servers/`
2. Implement MCP server interface
3. Add server configuration to `mcp_agent.config.yaml`
4. Update workflow to use new server

**Example: Modify tweet style**

1. Edit `src/agents/mcp_tweet_composer_agent.py`
2. Update the prompt in `compose_tweet()` method
3. Test with `--preview` mode
4. Review generated tweets

---

## 🚀 Deployment

### **Local Deployment (Current Setup)**

**Windows Desktop Application:**
- Run manually via `python run_tweet_processor.py`
- Automated weekly by Windows Task Scheduler, which runs `run_tweet_processor.bat` every Monday
- Full control over when tweets are generated

**Advantages:**
- ✅ Complete control over execution
- ✅ Manual review before posting
- ✅ No cloud costs
- ✅ Easy debugging

### **Cloud Deployment (Optional)**

**LastMile AI MCP Agent Cloud:**
- Deploy to LastMile MCP Agent Cloud for automated scheduling
- See [MCP Agent Cloud Docs](https://docs.mcp-agent.com/cloud/overview) for instructions

**Other Options:**
- **Docker**: Use included `Dockerfile` for containerization
- **AWS Lambda**: Deploy as serverless function
- **Google Cloud Run**: Deploy as containerized service
- **Heroku**: Deploy as web worker

---

## 📝 Content Authoring (.docx → .md)

Articles are authored in **`data/articles.docx`** (Microsoft Word) and converted to **`data/articles.md`**, which is the file the application actually reads. The runtime parser (`src/parsers/article_parser.py`) only reads the Markdown file — it never opens the `.docx` directly.

### Authoring format (in `articles.docx`)

Each article is a block of paragraphs:

```
Article #N                       <- Heading 1 paragraph (marks a new article)
Article #N Title: <title>
Article #N URL: : <url>
<body paragraph 1>
<body paragraph 2>
...
```

The converter emits the exact Markdown the parser expects:

```
## Article #N

**Title:** <title>

**URL:** <url>

**Content:**

<content>

**Metadata:**
- Word Count: <n>
- Status: Active

---
```

### Converting to Markdown

Run the converter after editing the `.docx`:

```powershell
# Convert articles.docx -> articles.md and clear the cache in one step
python scripts/convert_docx_to_md.py --clear-cache

# Preview what would be written without changing anything
python scripts/convert_docx_to_md.py --dry-run

# Only convert if articles.docx is newer than articles.md (used by automation)
python scripts/convert_docx_to_md.py --if-newer --clear-cache
```

The converter backs up the previous `articles.md` and writes **atomically** (temp file + replace), so a failure can never leave a corrupt file in place.

> **Why clear the cache?** Parsed articles are cached in `workflow_state.json` (`articles_cache`) and are only re-read when that cache is empty. `--clear-cache` empties it so the regenerated `articles.md` is picked up on the next run.

### Automatic sync (no manual steps)

Both scheduled runners auto-sync before doing their work, so simply editing `articles.docx` is enough — the next run picks it up:

- **Option A (runner):** `run_tweet_processor.bat` calls `convert_docx_to_md.py --if-newer --clear-cache` before running. This is a no-op unless the `.docx` is newer, and it is **fail-open** — it logs the result and posts the last-good `articles.md` if conversion fails, rather than skipping the week.
- **Option B (workflow):** the workflow itself re-checks on startup (`_sync_articles_if_docx_newer`) and regenerates if the `.docx` is newer — a safety net for when the app is run directly instead of through the `.bat`.

The two layers cover different failure modes (a broken/edited runner vs. the conversion itself failing) and are idempotent with each other.

---

## 🔧 Troubleshooting

### **Common Issues**

#### **"Anthropic API Key not found"**
- Verify `.env` file exists in project root
- Check `ANTHROPIC_API_KEY` is set in `.env`
- Ensure no extra spaces around the `=` sign
- Verify the key starts with `sk-ant-api03-`

#### **"Twitter 403 Forbidden"**
- Access token doesn't have write permissions
- Regenerate access token with "Read and Write" permissions
- See [docs/TWITTER_API_SETUP_GUIDE.md](docs/TWITTER_API_SETUP_GUIDE.md)

#### **"Cannot read articles file"**
- Verify `data/articles.md` file exists
- Check file permissions (read access required)
- Ensure file is not empty or corrupted

#### **"Tweet exceeds 280 characters"**
- This should be automatically handled
- If it occurs, check `mcp_tweet_composer_agent.py` for character limit enforcement
- Report as a bug if it persists

#### **"Workflow state corrupted"**
- Delete `workflow_state.json` to reset
- Re-run with `--preview` to regenerate state
- Backup important state files before deleting

### **Debug Mode**

```powershell
# Enable debug logging
# Edit mcp_agent.config.yaml:
logger:
  level: DEBUG

# Run with verbose output
python run_tweet_processor.py --preview
```

### **Getting Help**

- 📖 Read [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) for setup issues
- 🔒 Read [SECURITY_GUIDE.md](SECURITY_GUIDE.md) for security questions
- 🧪 Read [TESTING.md](TESTING.md) for test documentation
- 🐛 [Open an issue](https://github.com/youshen-lim/tweet-processor-mcp-agent/issues) for bugs
- 💬 [Start a discussion](https://github.com/youshen-lim/tweet-processor-mcp-agent/discussions) for questions

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### **Ways to Contribute**

- 🐛 Report bugs and issues
- 💡 Suggest new features
- 📖 Improve documentation
- 🔧 Submit pull requests
- ⭐ Star the repository

### **Development Workflow**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### **Code Style**

- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and small
- Write descriptive commit messages

### **Testing**

- Test with `--preview` mode before submitting PR
- Ensure no secrets are committed
- Verify documentation is updated

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

### **Frameworks & Tools**

- **[LastMile AI](https://lastmileai.dev/)** - MCP Agent Cloud framework ([GitHub](https://github.com/lastmile-ai/mcp-agent), [Docs](https://docs.mcp-agent.com/cloud/overview))
- **[Anthropic](https://www.anthropic.com/)** - Claude Sonnet 4.5 LLM
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - Standardized AI-service interface

### **Inspiration**

- **[Anthropic's "Building Effective Agents"](https://www.anthropic.com/research/building-effective-agents)** - Agent design patterns
- **[MCP Agent GitHub](https://github.com/lastmile-ai/mcp-agent)** - Reference implementation

### **Community**

- Thanks to all contributors and users
- Special thanks to the MCP community for building amazing servers

---

## 📚 Additional Resources

### **Documentation**

- [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) - Quick start and secrets setup guide
- [SECURITY_GUIDE.md](SECURITY_GUIDE.md) - Security best practices
- [TESTING.md](TESTING.md) - Test suite documentation
- [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md) - Troubleshooting guide
- [docs/TWITTER_API_SETUP_GUIDE.md](docs/TWITTER_API_SETUP_GUIDE.md) - Twitter API setup

### **External Resources**

- [MCP Agent Cloud Documentation](https://docs.mcp-agent.com/cloud/overview)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Twitter API Documentation](https://developer.twitter.com/en/docs)


### **Related Projects**

- [MCP Servers Collection](https://github.com/modelcontextprotocol/servers)
- [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook)

---

## 📊 Project Status

**Current Version:** 2.3.0
**Status:** Production-ready, running weekly automated execution
**Last Updated:** July 10, 2026

### **Roadmap**

- [x] Core tweet generation functionality
- [x] MCP Agent Cloud integration
- [x] Professional writing style enforcement
- [x] State management and caching
- [x] Pipeline preview feature
- [x] Local Markdown article parser (replaced Google Drive)
- [x] Article pre-analyzer with caching (retired July 2026 — the main workflow analyzes and caches inline)
- [x] Reliability utilities (timeouts, retries, heartbeat)
- [x] Windows Task Scheduler automation
- [x] URL validation and integrity checks
- [x] Automated testing suite (128 tests, 100% pass rate)
- [x] Enhanced LLM response parsing (universal code fence handling)
- [x] Improved numbered list heuristics (arbitrary length support)
- [x] Synchronized state logic (consistent URL deduplication)
- [x] Defensive logging (safe metadata access)
- [x] Word (.docx) article authoring with `convert_docx_to_md.py` converter
- [x] Automatic .docx → .md sync in scheduled runners (fail-open) and workflow
- [x] Tweet content sanitizer (strips LLM meta-commentary such as character counts before posting)
- [x] Tweet audit log (`logs/tweet_audit.log` records every composed and posted tweet verbatim)
- [x] Per-run console capture in the scheduled runner (`logs/console-<timestamp>.log`)
- [ ] Cloud deployment templates
- [ ] Multi-account support
- [ ] Analytics dashboard
- [ ] Thread generation support

---

## 💬 Contact

**Author:** Aaron (Youshen) Lim
**Email:** yl3566@cornell.edu
**GitHub:** [@youshen-lim](https://github.com/youshen-lim)

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Built with ❤️ using LastMile AI's MCP Agent Cloud and Claude Sonnet 4.5**


