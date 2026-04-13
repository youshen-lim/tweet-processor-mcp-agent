#!/usr/bin/env python3
"""
Article Analyzer - Pre-analyze articles for Tweet Processor

This script analyzes articles 3 weeks in advance to ensure reliable tweet generation.
It caches analysis results in workflow_state.json for use by the main tweet processor.

Usage:
    python run_article_analyzer.py --analyze-all    # Analyze all unanalyzed articles
    python run_article_analyzer.py --analyze-next   # Analyze next 3 weeks of articles
    python run_article_analyzer.py --status         # Show analysis status
    python run_article_analyzer.py --force-refresh  # Re-analyze all articles
"""

import asyncio
import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from workflows.mcp_tweet_processor_workflow import MCPTweetProcessorWorkflow


class ArticleAnalyzer:
    """Pre-analyzes articles for the Tweet Processor workflow."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.workflow = MCPTweetProcessorWorkflow()
        self.state_file = 'workflow_state.json'
        
    def load_state(self) -> Dict[str, Any]:
        """Load current workflow state."""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "current_article": 1,
                "current_variation": 1,
                "last_posted": None,
                "total_posts": 0,
                "articles_cache": []
            }
    
    def save_state(self, state: Dict[str, Any]):
        """Save workflow state."""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def get_analysis_status(self) -> Dict[str, Any]:
        """Get current analysis status."""
        state = self.load_state()
        articles = state.get("articles_cache", [])
        
        if not articles:
            return {
                "total_articles": 0,
                "analyzed_articles": 0,
                "unanalyzed_articles": [],
                "analysis_coverage": "0%",
                "next_3_weeks": []
            }
        
        total_articles = len(articles)
        analyzed_count = 0
        unanalyzed_articles = []
        
        # Check which articles have analysis
        for article in articles:
            cache_key = f"analysis_{article['number']}"
            if cache_key in state:
                analyzed_count += 1
            else:
                unanalyzed_articles.append({
                    "number": article['number'],
                    "title": article['title'][:50] + "..." if len(article['title']) > 50 else article['title']
                })
        
        # Calculate next 3 weeks of articles needed
        current_article = state.get("current_article", 1)
        current_variation = state.get("current_variation", 1)
        
        next_3_weeks = []
        article_num = current_article
        variation_num = current_variation
        
        for week in range(3):
            if article_num <= total_articles:
                cache_key = f"analysis_{article_num}"
                is_analyzed = cache_key in state
                
                next_3_weeks.append({
                    "week": week + 1,
                    "article_number": article_num,
                    "variation": variation_num,
                    "title": articles[article_num - 1]['title'][:40] + "..." if len(articles[article_num - 1]['title']) > 40 else articles[article_num - 1]['title'],
                    "is_analyzed": is_analyzed
                })
                
                # Move to next variation/article
                variation_num += 1
                if variation_num > 4:  # 4 variations per article
                    variation_num = 1
                    article_num += 1
        
        coverage_percent = f"{(analyzed_count / total_articles * 100):.1f}%" if total_articles > 0 else "0%"
        
        return {
            "total_articles": total_articles,
            "analyzed_articles": analyzed_count,
            "unanalyzed_articles": unanalyzed_articles,
            "analysis_coverage": coverage_percent,
            "next_3_weeks": next_3_weeks
        }
    
    async def analyze_all_articles(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Analyze all articles that don't have cached analysis."""
        print("🔍 Starting article analysis process...")
        print()
        
        # Initialize the workflow
        async with self.workflow.mcp_app.run() as mcp_agent_app:
            logger = mcp_agent_app.logger
            logger.info("Starting bulk article analysis")
            
            # Initialize agents
            await self.workflow.initialize_agents()
            
            # Load current state
            state = self.load_state()
            
            # Load articles (from cache or Google Drive)
            if not state.get("articles_cache"):
                print("📄 Loading articles from Google Drive...")
                articles = await self.workflow._read_and_parse_document()
                state["articles_cache"] = articles
                self.save_state(state)
                print(f"✓ Loaded {len(articles)} articles")
            else:
                articles = state["articles_cache"]
                print(f"✓ Using cached articles ({len(articles)} total)")
            
            print()
            
            # Analyze each article
            analyzed_count = 0
            skipped_count = 0
            failed_count = 0
            
            for article in articles:
                cache_key = f"analysis_{article['number']}"
                
                # Skip if already analyzed (unless force refresh)
                if cache_key in state and not force_refresh:
                    print(f"⏭️  Article #{article['number']}: Already analyzed (skipping)")
                    skipped_count += 1
                    continue
                
                try:
                    print(f"🔍 Analyzing Article #{article['number']}: {article['title'][:50]}...")
                    
                    # Analyze the article
                    insights = await self.workflow.content_analyzer.analyze_article(article)
                    
                    # Cache the analysis
                    analysis = {
                        'article_number': insights.article_number,
                        'article_title': insights.article_title,
                        'article_url': insights.article_url,
                        'key_insights': insights.key_insights,
                        'themes': insights.themes,
                        'expert_references': insights.expert_references,
                        'frameworks_mentioned': insights.frameworks_mentioned,
                        'analyzed_at': datetime.now().isoformat()
                    }
                    
                    state[cache_key] = analysis
                    self.save_state(state)
                    
                    print(f"✅ Article #{article['number']}: Extracted {len(analysis['key_insights'])} insights")
                    analyzed_count += 1
                    
                except Exception as e:
                    print(f"❌ Article #{article['number']}: Analysis failed - {str(e)}")
                    failed_count += 1
                    logger.error(f"Failed to analyze article {article['number']}: {e}")
            
            print()
            print("📊 Analysis Summary:")
            print(f"   ✅ Analyzed: {analyzed_count} articles")
            print(f"   ⏭️  Skipped: {skipped_count} articles")
            print(f"   ❌ Failed: {failed_count} articles")
            print()
            
            return {
                "analyzed": analyzed_count,
                "skipped": skipped_count,
                "failed": failed_count,
                "total_processed": analyzed_count + skipped_count + failed_count
            }
    
    async def analyze_next_weeks(self, weeks: int = 3) -> Dict[str, Any]:
        """Analyze articles needed for the next N weeks."""
        print(f"🔍 Analyzing articles for next {weeks} weeks...")
        print(f"📅 Weekly schedule: Monday analysis → Thursday posting")
        print()
        
        status = self.get_analysis_status()
        articles_to_analyze = []
        
        # Identify articles needed for next weeks
        for week_info in status["next_3_weeks"][:weeks]:
            if not week_info["is_analyzed"]:
                articles_to_analyze.append(week_info["article_number"])
        
        # Remove duplicates
        articles_to_analyze = list(set(articles_to_analyze))
        
        if not articles_to_analyze:
            print("✅ All articles for the next 3 weeks are already analyzed!")
            return {"analyzed": 0, "skipped": 0, "failed": 0}
        
        print(f"📝 Need to analyze {len(articles_to_analyze)} articles: {articles_to_analyze}")
        print()
        
        # Load state and articles
        state = self.load_state()
        articles = state.get("articles_cache", [])
        
        if not articles:
            print("❌ No articles found in cache. Run with --analyze-all first.")
            return {"analyzed": 0, "skipped": 0, "failed": 1}
        
        # Initialize workflow for analysis
        async with self.workflow.mcp_app.run() as mcp_agent_app:
            await self.workflow.initialize_agents()
            
            analyzed_count = 0
            failed_count = 0
            
            for article_num in articles_to_analyze:
                # Find the article
                article = next((a for a in articles if a['number'] == article_num), None)
                if not article:
                    print(f"❌ Article #{article_num}: Not found in cache")
                    failed_count += 1
                    continue
                
                try:
                    print(f"🔍 Analyzing Article #{article_num}: {article['title'][:50]}...")
                    
                    # Analyze the article
                    insights = await self.workflow.content_analyzer.analyze_article(article)
                    
                    # Cache the analysis
                    cache_key = f"analysis_{article_num}"
                    analysis = {
                        'article_number': insights.article_number,
                        'article_title': insights.article_title,
                        'article_url': insights.article_url,
                        'key_insights': insights.key_insights,
                        'themes': insights.themes,
                        'expert_references': insights.expert_references,
                        'frameworks_mentioned': insights.frameworks_mentioned,
                        'analyzed_at': datetime.now().isoformat()
                    }
                    
                    state[cache_key] = analysis
                    self.save_state(state)
                    
                    print(f"✅ Article #{article_num}: Extracted {len(analysis['key_insights'])} insights")
                    analyzed_count += 1
                    
                except Exception as e:
                    print(f"❌ Article #{article_num}: Analysis failed - {str(e)}")
                    failed_count += 1
            
            print()
            print("📊 Analysis Summary:")
            print(f"   ✅ Analyzed: {analyzed_count} articles")
            print(f"   ❌ Failed: {failed_count} articles")
            print()
            
            return {"analyzed": analyzed_count, "skipped": 0, "failed": failed_count}


def print_status(analyzer: ArticleAnalyzer):
    """Print current analysis status."""
    status = analyzer.get_analysis_status()
    
    print("================================================================================")
    print("📊 ARTICLE ANALYSIS STATUS")
    print("================================================================================")
    print()
    print(f"📚 Total Articles: {status['total_articles']}")
    print(f"✅ Analyzed: {status['analyzed_articles']}")
    print(f"📈 Coverage: {status['analysis_coverage']}")
    print()
    
    if status['unanalyzed_articles']:
        print("❌ Unanalyzed Articles:")
        for article in status['unanalyzed_articles']:
            print(f"   #{article['number']}: {article['title']}")
        print()
    
    print("📅 Next 3 Weeks Schedule:")
    for week in status['next_3_weeks']:
        status_icon = "✅" if week['is_analyzed'] else "❌"
        print(f"   Week {week['week']}: Article #{week['article_number']}, Variation {week['variation']} {status_icon}")
        print(f"            {week['title']}")
    print()


async def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Pre-analyze articles for Tweet Processor')
    parser.add_argument('--analyze-all', action='store_true', help='Analyze all unanalyzed articles')
    parser.add_argument('--analyze-next', action='store_true', help='Analyze articles for next 3 weeks')
    parser.add_argument('--status', action='store_true', help='Show analysis status')
    parser.add_argument('--force-refresh', action='store_true', help='Re-analyze all articles (ignore cache)')
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = ArticleAnalyzer()
    
    try:
        if args.status:
            print_status(analyzer)
            
        elif args.analyze_all:
            await analyzer.analyze_all_articles(force_refresh=args.force_refresh)
            print_status(analyzer)
            
        elif args.analyze_next:
            await analyzer.analyze_next_weeks(weeks=3)
            print_status(analyzer)
            
        else:
            # Default: show status and analyze next 3 weeks if needed
            print_status(analyzer)
            
            status = analyzer.get_analysis_status()
            unanalyzed_next_weeks = [w for w in status['next_3_weeks'] if not w['is_analyzed']]
            
            if unanalyzed_next_weeks:
                print("🔍 Found unanalyzed articles for next 3 weeks. Analyzing now...")
                print()
                await analyzer.analyze_next_weeks(weeks=3)
                print_status(analyzer)
            else:
                print("✅ All articles for next 3 weeks are ready!")
    
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
