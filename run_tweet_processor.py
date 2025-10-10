#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tweet Processor - Local Desktop Runner

This script runs the Tweet Processor locally on your Windows computer.
Use this for manual weekly execution and testing before cloud deployment.

Usage:
    python run_tweet_processor.py              # Generate next tweet (manual review)
    python run_tweet_processor.py --post       # Generate and post to Twitter
    python run_tweet_processor.py --preview    # Preview next tweet without updating state
    python run_tweet_processor.py --pipeline   # Generate 3-week pipeline of scheduled tweets
    python run_tweet_processor.py --generate-all  # Generate all tweets for all articles
    python run_tweet_processor.py --status     # Show current state
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import MCP-based workflow (new implementation)
from workflows.mcp_tweet_processor_workflow import MCPTweetProcessorWorkflow

# Legacy import (fallback)
try:
    from workflows.tweet_processor_workflow import TweetProcessorWorkflow
    LEGACY_AVAILABLE = True
except ImportError:
    LEGACY_AVAILABLE = False
    TweetProcessorWorkflow = None


def validate_environment():
    """Validate all required environment variables and files are present."""
    print("🔍 Validating environment...")

    # Get current working directory
    current_dir = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"📁 Current directory: {current_dir}")
    print(f"📁 Script directory: {script_dir}")

    # Check if we're in the right directory
    if current_dir != script_dir:
        print(f"⚠️  Warning: Running from different directory than script location")
        print(f"💡 Consider running from: {script_dir}")

    # Check required files exist
    required_files = [
        '.env',
        'mcp_agent.config.yaml',
        'requirements.txt',
        'src/workflows/mcp_tweet_processor_workflow.py',
        'src/mcp_servers/google_drive_server.py',
        'src/mcp_servers/twitter_server.py'
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print()
        print("💡 Make sure you're running this script from the tweet-processor-mcp-agent directory")
        print("📖 See PORTABLE_SETUP.md for setup instructions")
        return False

    # Check required environment variables
    required_env_vars = [
        'ANTHROPIC_API_KEY',
        'GOOGLE_DRIVE_DOCUMENT_ID',
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET'
    ]

    missing_vars = []
    placeholder_vars = []

    for var in required_env_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif value in ['your_document_id_here', 'YOUR-ACTUAL-KEY-HERE', 'YOUR-ACTUAL-SECRET-HERE',
                       'YOUR-ACTUAL-TOKEN-HERE', 'YOUR-ACTUAL-TOKEN-SECRET-HERE']:
            placeholder_vars.append(var)

    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("📖 Please set these variables in your .env file")
        print("💡 See SECRETS_SETUP.md for detailed instructions")
        return False

    if placeholder_vars:
        print("❌ Environment variables still have placeholder values:")
        for var in placeholder_vars:
            print(f"   - {var} = {os.getenv(var)}")
        print()
        print("📖 Please replace placeholder values with your actual API keys")
        print("💡 See SECRETS_SETUP.md for detailed instructions")
        return False

    # Special check for Google Drive Document ID format
    doc_id = os.getenv('GOOGLE_DRIVE_DOCUMENT_ID')
    if doc_id and len(doc_id) < 20:  # Google Drive document IDs are typically much longer
        print(f"⚠️  Warning: GOOGLE_DRIVE_DOCUMENT_ID looks too short: {doc_id}")
        print("💡 Make sure you copied the full document ID from the Google Drive URL")
        print("📖 See SECRETS_SETUP.md section 'F. Get Document ID' for help")

    # Check Google Drive credentials file
    credentials_path = os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH', 'credentials/google-drive-credentials.json')
    if not os.path.exists(credentials_path):
        print(f"❌ Google Drive credentials file not found: {credentials_path}")
        print("📖 Please set up Google Drive credentials")
        print("💡 See SECRETS_SETUP.md section '3. Google Drive API Setup' for instructions")
        return False

    print("✅ Environment validation passed")
    print()
    return True


def print_banner():
    """Print welcome banner."""
    print("=" * 80)
    print("🐦 TWEET PROCESSOR - LOCAL DESKTOP RUNNER (MCP Agent Cloud)")
    print("=" * 80)
    print()


def print_state(state: dict):
    """Print current workflow state."""
    print("📊 CURRENT STATE:")
    print(f"   Current Article: #{state['current_article']}")
    print(f"   Current Variation: #{state['current_variation']}")
    print(f"   Total Posts: {state['total_posts']}")
    print(f"   Last Posted: {state['last_posted'] or 'Never'}")
    print()


def print_tweet(tweet_data: dict):
    """Print tweet in a nice format."""
    print("=" * 80)
    print(f"📝 GENERATED TWEET (Article #{tweet_data['article_number']}, Variation #{tweet_data['variation_number']})")
    print("=" * 80)
    print()
    print(tweet_data['content'])
    print()
    print("=" * 80)
    print(f"📊 CHARACTER COUNT: {tweet_data['character_count']} / 280")
    print(f"🏷️  HASHTAGS: {', '.join(tweet_data['hashtags'])}")
    if 'focus_theme' in tweet_data:
        print(f"🎯 FOCUS: {tweet_data['focus_theme']}")
    print("=" * 80)
    print()


async def run_status():
    """Show current status."""
    print_banner()

    workflow = MCPTweetProcessorWorkflow()
    print_state(workflow.state)

    # Show configuration
    print("⚙️  CONFIGURATION:")
    print(f"   Framework: MCP Agent Cloud (LastMile AI)")
    print(f"   LLM Provider: {os.getenv('LLM_PROVIDER', 'anthropic')}")
    print(f"   Model: {os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-5-20250929')}")
    print(f"   Use Real APIs: {os.getenv('USE_REAL_APIS', 'false')}")
    print(f"   Enable Twitter Posting: {os.getenv('ENABLE_TWITTER_POSTING', 'false')}")
    print()


async def run_preview():
    """Preview next tweet without updating state."""
    print_banner()
    print("🔍 PREVIEW MODE - State will NOT be updated")
    print()

    workflow = MCPTweetProcessorWorkflow()
    print_state(workflow.state)

    print("⏳ Generating next tweet with MCP Agent Cloud...")
    print()

    # Run workflow but don't save state (post_to_twitter=False)
    result = await workflow.run_weekly_post(post_to_twitter=False)
    
    if result['status'] == 'success':
        print_tweet(result['tweet'])
        
        print("💡 NEXT STEPS:")
        print("   1. Review the tweet above")
        print("   2. If satisfied, run: python run_tweet_processor.py")
        print("   3. This will generate the tweet and update state")
        print()
    else:
        print(f"❌ ERROR: {result.get('error', 'Unknown error')}")
        print()


async def run_generate():
    """Generate next tweet and update state (manual review mode)."""
    print_banner()
    print("📝 GENERATE MODE - Tweet will be generated and state updated")
    print()

    workflow = MCPTweetProcessorWorkflow()
    print_state(workflow.state)

    print("⏳ Generating next tweet with MCP Agent Cloud...")
    print()

    # Run workflow (simulation mode - don't post)
    result = await workflow.run_weekly_post(post_to_twitter=False)
    
    if result['status'] == 'success':
        print_tweet(result['tweet'])
        
        # Save to file for manual posting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tweet_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ SUCCESS!")
        print(f"📁 Tweet saved to: {filename}")
        print()
        print("📊 UPDATED STATE:")
        print_state(workflow.state)
        
        print("💡 NEXT STEPS:")
        print("   1. Review the tweet above")
        print("   2. Manually post to Twitter if satisfied")
        print("   3. Run again next Monday for the next tweet")
        print()
        
    else:
        print(f"❌ ERROR: {result.get('error', 'Unknown error')}")
        print()


async def run_post():
    """Generate and post tweet to Twitter."""
    print_banner()
    print("🚀 POST MODE - Tweet will be generated and posted to Twitter")
    print()

    # Check if Twitter posting is enabled
    enable_posting = os.getenv('ENABLE_TWITTER_POSTING', 'false').lower() == 'true'

    if not enable_posting:
        print("⚠️  WARNING: Twitter posting is DISABLED in .env file")
        print("   Set ENABLE_TWITTER_POSTING=true to enable auto-posting")
        print()
        print("   Running in manual review mode instead...")
        print()
        await run_generate()
        return

    workflow = MCPTweetProcessorWorkflow()
    print_state(workflow.state)

    print("⏳ Generating and posting tweet with MCP Agent Cloud...")
    print()

    # Run workflow with posting enabled
    result = await workflow.run_weekly_post(post_to_twitter=True)
    
    if result['status'] == 'success':
        print_tweet(result['tweet'])
        
        if result.get('posted', False):
            print("✅ TWEET POSTED TO TWITTER!")
            print(f"🔗 Tweet URL: {result.get('tweet_url', 'N/A')}")
        else:
            print("ℹ️  Tweet generated but not posted (Twitter API not configured)")
        
        print()
        print("📊 UPDATED STATE:")
        print_state(workflow.state)
        
    else:
        print(f"❌ ERROR: {result.get('error', 'Unknown error')}")
        print()


async def run_pipeline():
    """Generate pipeline of scheduled tweets for next 3 weeks."""
    print_banner()
    print("🔮 PIPELINE MODE - Generating 3-week tweet schedule with MCP Agent Cloud")
    print()

    workflow = MCPTweetProcessorWorkflow()
    print_state(workflow.state)

    print("⏳ Generating pipeline (this may take a minute)...")
    print()

    # Generate pipeline
    pipeline = await workflow.generate_pipeline_preview(weeks=3)

    # Format result for display
    result = {
        'pipeline': [],
        'generated_at': datetime.now().isoformat(),
        'posting_schedule': {
            'day': os.getenv('POSTING_DAY', 'Thursday'),
            'time': os.getenv('POSTING_TIME', '11:30'),
            'timezone': os.getenv('POSTING_TIMEZONE', 'America/New_York')
        }
    }

    for item in pipeline:
        post_date = datetime.fromisoformat(item['post_date'])
        result['pipeline'].append({
            'week_number': item['week'],
            'scheduled_date_formatted': post_date.strftime('%A, %B %d, %Y at %I:%M %p %Z'),
            'article_number': item['article_number'],
            'variation_number': item['variation_number'],
            'article_title': item['article_title'],
            'article_url': '',  # Not included in preview
            'focus_theme': f"variation_{item['variation_number']}",
            'tweet_content': item['tweet_content'],
            'character_count': item['character_count'],
            'hashtags': [word for word in item['tweet_content'].split() if word.startswith('#')]
        })

    # Display pipeline
    print("=" * 80)
    print("📅 TWEET PIPELINE - NEXT 3 WEEKS")
    print("=" * 80)
    print()

    for tweet_data in result['pipeline']:
        print(f"{'─' * 80}")
        print(f"📌 WEEK {tweet_data['week_number']}: {tweet_data['scheduled_date_formatted']}")
        print(f"{'─' * 80}")
        print(f"📝 Article #{tweet_data['article_number']}, Variation #{tweet_data['variation_number']}")
        print(f"📄 Title: {tweet_data['article_title'][:70]}...")
        print(f"🎯 Focus: {tweet_data['focus_theme']}")
        print()
        print("🐦 TWEET CONTENT:")
        print(tweet_data['tweet_content'])
        print()
        print(f"📊 Characters: {tweet_data['character_count']}/280")
        print(f"🏷️  Hashtags: {', '.join(tweet_data['hashtags'])}")
        print()

    print("=" * 80)

    # Save to JSON file
    json_filename = 'tweet_pipeline.json'
    with open(json_filename, 'w') as f:
        json.dump(result, f, indent=2)

    # Save to Markdown file for easy review
    md_filename = 'tweet_pipeline.md'
    with open(md_filename, 'w') as f:
        f.write("# Tweet Pipeline - Next 3 Weeks\n\n")
        f.write(f"**Generated:** {result['generated_at']}\n\n")
        f.write(f"**Schedule:** Every {result['posting_schedule']['day']} at {result['posting_schedule']['time']} {result['posting_schedule']['timezone']}\n\n")
        f.write("---\n\n")

        for tweet_data in result['pipeline']:
            f.write(f"## Week {tweet_data['week_number']}: {tweet_data['scheduled_date_formatted']}\n\n")
            f.write(f"**Article:** #{tweet_data['article_number']} - {tweet_data['article_title']}\n\n")
            f.write(f"**Variation:** #{tweet_data['variation_number']}\n\n")
            f.write(f"**Focus Theme:** {tweet_data['focus_theme']}\n\n")
            f.write(f"**Character Count:** {tweet_data['character_count']}/280\n\n")
            f.write(f"**Hashtags:** {', '.join(tweet_data['hashtags'])}\n\n")
            f.write("### Tweet Content\n\n")
            f.write("```\n")
            f.write(tweet_data['tweet_content'])
            f.write("\n```\n\n")
            f.write(f"**Article URL:** {tweet_data['article_url']}\n\n")
            f.write("---\n\n")

    print(f"✅ Pipeline saved to:")
    print(f"   📁 {json_filename} (JSON format)")
    print(f"   📁 {md_filename} (Markdown format)")
    print()
    print("💡 NEXT STEPS:")
    print("   1. Review the pipeline in tweet_pipeline.md")
    print("   2. Edit tweets directly in the markdown file if needed")
    print("   3. When ready to post, run: python run_tweet_processor.py")
    print("   4. Or enable auto-posting: Set ENABLE_TWITTER_POSTING=true in .env")
    print()


async def run_generate_all():
    """Generate all tweets for all articles."""
    print_banner()
    print("📚 GENERATE ALL MODE - Generating tweets for all articles with MCP Agent Cloud")
    print()

    workflow = MCPTweetProcessorWorkflow()

    print("⏳ This may take a few minutes...")
    print()

    # Note: This function needs to be implemented in MCPTweetProcessorWorkflow
    print("⚠️  This feature is not yet implemented in MCP Agent Cloud version")
    print("   Use --pipeline instead to generate a 3-week preview")
    return

    print(f"✅ Generated {result['total_tweets']} tweets from {result['total_articles']} articles")
    print(f"📅 Content duration: {result['content_duration_weeks']} weeks (~{result['content_duration_weeks']/52:.1f} years)")
    print()

    # Save to file
    filename = 'all_tweets.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"📁 All tweets saved to: {filename}")
    print()

    # Show first 3 tweets as preview
    print("📝 PREVIEW (First 3 tweets):")
    print()
    for i, tweet in enumerate(result['tweets'][:3], 1):
        print(f"--- Tweet {i} ---")
        print(tweet['content'][:150] + "...")
        print(f"Characters: {tweet['character_count']}")
        print()


async def main():
    """Main entry point."""
    print_banner()

    # Validate environment before proceeding
    if not validate_environment():
        print("❌ Environment validation failed. Please fix the issues above before continuing.")
        print()
        print("📚 Helpful resources:")
        print("   - PORTABLE_SETUP.md - Complete setup guide")
        print("   - SECRETS_SETUP.md - API configuration guide")
        print("   - README.md - Project overview")
        sys.exit(1)

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "--status":
            await run_status()
        elif command == "--preview":
            await run_preview()
        elif command == "--post":
            await run_post()
        elif command == "--pipeline":
            await run_pipeline()
        elif command == "--generate-all":
            await run_generate_all()
        elif command in ["--help", "-h"]:
            print(__doc__)
        else:
            print(f"❌ Unknown command: {command}")
            print()
            print(__doc__)
    else:
        # Default: generate next tweet (manual review mode)
        await run_generate()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

