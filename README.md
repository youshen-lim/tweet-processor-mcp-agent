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

- 📄 **Reads** newsletter content from Google Drive
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
- **Composability**: Chain together Google Drive (read) → Claude (analyze) → Twitter (post)
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
- **Google Drive**: Reads newsletter content directly from Google Docs via MCP server
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
│   └── MCP Servers (Google Drive, Twitter)
├── Agents
│   ├── MCPContentAnalyzerAgent (extract insights)
│   └── MCPTweetComposerAgent (generate tweets)
└── Workflow
    └── MCPTweetProcessorWorkflow (orchestration)
```

### **Workflow Steps**

```
Step 1: Read Document (Google Drive MCP)
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
- **Google Drive API credentials** (service account)
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

# 4. Set up Google Drive credentials
# See SECRETS_SETUP.md for detailed instructions

# 5. Test the system
python run_tweet_processor.py --preview
```

**Detailed Setup:** See [SECRETS_SETUP.md](SECRETS_SETUP.md) for step-by-step instructions.

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
- `mcp-agent>=0.1.27` - MCP Agent Cloud framework
- `anthropic>=0.48.0` - Claude API client
- `tweepy>=4.14.0` - Twitter API client
- `google-auth`, `google-api-python-client` - Google Drive API
- `python-dotenv` - Environment variable management

### **3. Set Up Secrets**

See [SECRETS_SETUP.md](SECRETS_SETUP.md) for complete instructions.

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
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Google Drive
GOOGLE_DRIVE_DOCUMENT_ID=YOUR-DOCUMENT-ID
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials/google-drive-credentials.json

# Twitter API
TWITTER_API_KEY=YOUR-API-KEY
TWITTER_API_SECRET=YOUR-API-SECRET
TWITTER_ACCESS_TOKEN=YOUR-ACCESS-TOKEN
TWITTER_ACCESS_TOKEN_SECRET=YOUR-ACCESS-TOKEN-SECRET

# Posting Configuration
ENABLE_TWITTER_POSTING=false
POSTING_DAY=Thursday
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
  google_drive:
    command: python
    args: ["src/mcp_servers/google_drive_server.py"]
  
  twitter:
    command: python
    args: ["src/mcp_servers/twitter_server.py"]

model:
  provider: anthropic
  name: claude-3-5-sonnet-20241022
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
├── run_tweet_processor.py          # Main entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── mcp_agent.config.yaml           # MCP Agent configuration
├── mcp_agent.secrets.yaml.example  # Secrets template
├── README.md                       # This file
├── SECRETS_SETUP.md                # Secrets setup guide
├── SECURITY_GUIDE.md               # Security best practices
├── DEPLOYMENT_GUIDE.md             # Deployment instructions
├── DEVELOPMENT_TRANSCRIPT.md       # Development story
├── src/
│   ├── agents/
│   │   ├── mcp_content_analyzer_agent.py
│   │   └── mcp_tweet_composer_agent.py
│   ├── workflows/
│   │   └── mcp_tweet_processor_workflow.py
│   └── mcp_servers/
│       ├── google_drive_server.py
│       └── twitter_server.py
├── credentials/
│   ├── README.md                   # Credentials setup guide
│   └── google-drive-credentials.json  # (gitignored)
├── docs/
│   ├── TWITTER_API_SETUP_GUIDE.md
│   └── TWITTER_QUICK_START.md
└── logs/
    └── mcp_agent.log               # (gitignored)
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
# Test with preview mode (safe - no posting)
python run_tweet_processor.py --preview

# Test Google Drive connection
python -c "from src.mcp_servers.google_drive_server import GoogleDriveMCPServer; print('✅ Google Drive MCP Server loaded')"

# Test Twitter connection (requires credentials)
python test_twitter_connection.py

# Generate test pipeline
python run_tweet_processor.py --pipeline
```

### **Code Structure**

**Agents** (`src/agents/`):
- `mcp_content_analyzer_agent.py` - Analyzes articles and extracts 7 strategic insights
- `mcp_tweet_composer_agent.py` - Composes tweets with professional writing style

**Workflows** (`src/workflows/`):
- `mcp_tweet_processor_workflow.py` - Orchestrates the entire tweet generation process

**MCP Servers** (`src/mcp_servers/`):
- `google_drive_server.py` - MCP server for reading Google Drive documents
- `twitter_server.py` - MCP server for posting tweets

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
- Schedule with Windows Task Scheduler (optional)
- Full control over when tweets are generated

**Advantages:**
- ✅ Complete control over execution
- ✅ Manual review before posting
- ✅ No cloud costs
- ✅ Easy debugging

### **Cloud Deployment (Optional)**

**LastMile AI MCP Agent Cloud:**
- Deploy to LastMile MCP Agent Cloud for automated scheduling
- See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for instructions

**Other Options:**
- **Docker**: Use included `Dockerfile` for containerization
- **AWS Lambda**: Deploy as serverless function
- **Google Cloud Run**: Deploy as containerized service
- **Heroku**: Deploy as web worker

---

## 📝 Document Format

Your Google Drive document should follow this structure:

```
Article #1: Title of First Article
URL: https://example.com/article-1

Content of the first article goes here...

---

Article #2: Title of Second Article
URL: https://example.com/article-2

Content of the second article...

---
```

**Format Rules:**
- Each article starts with `Article #N: Title`
- Next line: `URL: <article-url>`
- Followed by article content
- Articles separated by `---`

**Example Document:**
See [docs/EXAMPLE_NEWSLETTER.md](docs/EXAMPLE_NEWSLETTER.md) for a complete example.

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

#### **"Google Drive permission denied"**
- Service account email not shared with document
- Share document with service account email (from JSON file)
- Set permission to "Viewer" or higher

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

- 📖 Read [SECRETS_SETUP.md](SECRETS_SETUP.md) for setup issues
- 🔒 Read [SECURITY_GUIDE.md](SECURITY_GUIDE.md) for security questions
- 🚀 Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for deployment help
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

- [SECRETS_SETUP.md](SECRETS_SETUP.md) - Complete secrets setup guide
- [SECURITY_GUIDE.md](SECURITY_GUIDE.md) - Security best practices
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deployment options
- [DEVELOPMENT_TRANSCRIPT.md](DEVELOPMENT_TRANSCRIPT.md) - Development journey
- [docs/TWITTER_API_SETUP_GUIDE.md](docs/TWITTER_API_SETUP_GUIDE.md) - Twitter API setup

### **External Resources**

- [MCP Agent Cloud Documentation](https://docs.mcp-agent.com/cloud/overview)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Twitter API Documentation](https://developer.twitter.com/en/docs)
- [Google Drive API Documentation](https://developers.google.com/drive)

### **Related Projects**

- [MCP Servers Collection](https://github.com/modelcontextprotocol/servers)
- [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook)

---

## 📊 Project Status

**Current Version:** 1.0.0
**Status:** Production-ready for local use
**Last Updated:** October 2, 2025

### **Roadmap**

- [x] Core tweet generation functionality
- [x] MCP Agent Cloud integration
- [x] Professional writing style enforcement
- [x] State management and caching
- [x] Pipeline preview feature
- [ ] Automated testing suite
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


