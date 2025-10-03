"""
Content Analyzer Agent - MCP Agent Cloud Implementation
Extracts key insights from newsletter articles using MCP Agent framework.
"""

import os
import sys
from typing import List, Dict, Any
from dataclasses import dataclass
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# MCP Agent Cloud imports
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_anthropic import AnthropicAugmentedLLM


@dataclass
class ArticleInsights:
    """Represents insights extracted from an article."""
    article_number: int
    article_title: str
    article_url: str
    key_insights: List[str]
    themes: List[str]
    expert_references: List[str]
    frameworks_mentioned: List[str]


class MCPContentAnalyzerAgent:
    """Agent that analyzes article content using MCP Agent Cloud framework."""
    
    INSTRUCTION = """You are a content analyzer specializing in AI, data strategy, and business technology articles.

Your task is to analyze newsletter articles and extract HIGH-LEVEL, SALIENT insights that provide strategic value.

CRITICAL REQUIREMENTS:
1. Extract exactly 7 DISTINCT key insights
2. Each insight must be HIGH-LEVEL and STRATEGIC (not surface-level facts)
3. Each insight must be SUBSTANTIALLY DIFFERENT from the others
4. Focus on DEEP TAKEAWAYS that would make compelling, thought-provoking tweets
5. Ignore the article title - focus ONLY on the content itself

What makes a SALIENT insight:
✓ Strategic business implications (not just "what" but "why it matters")
✓ Actionable frameworks or methodologies
✓ Counter-intuitive findings or expert perspectives
✓ Practical applications with measurable impact
✓ Systemic approaches or mental models

What to AVOID:
✗ Surface-level facts or obvious statements
✗ Repeating similar points with different wording
✗ Generic advice without specific context
✗ Technical jargon without business value
✗ Restating the article title

Format your response as JSON with this structure:
{
    "key_insights": [
        "Insight 1 (high-level, strategic, tweet-worthy)",
        "Insight 2 (completely different angle)",
        ...7 distinct insights total
    ],
    "themes": ["Theme 1", "Theme 2", ...],
    "expert_references": ["Expert name and context", ...],
    "frameworks_mentioned": ["Framework name and brief description", ...]
}
"""
    
    def __init__(self, agent: Agent = None):
        """
        Initialize the Content Analyzer Agent.
        
        Args:
            agent: Optional pre-configured MCP Agent instance
        """
        if agent is None:
            # Create new agent with default configuration
            self.agent = Agent(
                name="content_analyzer",
                instruction=self.INSTRUCTION,
                server_names=[]  # No MCP servers needed for this agent
            )
        else:
            self.agent = agent
        
        self.llm = None

    async def initialize(self, model: str = None):
        """
        Initialize the LLM connection.

        Args:
            model: Optional model name override (defaults to config)
        """
        if not self.llm:
            # Attach Anthropic LLM to agent
            # Note: temperature and other params are set per-request via request_params
            self.llm = await self.agent.attach_llm(AnthropicAugmentedLLM)
        
    async def analyze_article(self, article: Dict[str, Any]) -> ArticleInsights:
        """
        Analyze an article and extract key insights.

        Args:
            article: Article data with number, title, url, and content

        Returns:
            ArticleInsights with extracted information
        """
        # Ensure LLM is initialized
        if not self.llm:
            await self.initialize()
        
        # Create analysis prompt - IGNORE TITLE, focus on content
        prompt = f"""Analyze this newsletter article and extract 7 HIGH-LEVEL, SALIENT insights.

IMPORTANT: Do NOT reference or use the article title in your analysis. Focus ONLY on the content below.

Article Content:
{article['content'][:3000]}...

Extract exactly 7 DISTINCT key insights that meet these criteria:

1. HIGH-LEVEL & STRATEGIC: Focus on "why it matters" not just "what it is"
   Example: "Strategic alignment trumps technical complexity in AI implementation"
   NOT: "The article discusses AI implementation"

2. SUBSTANTIALLY DIFFERENT: Each insight must explore a DIFFERENT angle
   - Insight 1: Strategic/business perspective
   - Insight 2: Methodological/framework approach
   - Insight 3: Expert perspective or counter-intuitive finding
   - Insight 4: Practical application with measurable impact
   - Insight 5: Organizational/cultural dimension
   - Insight 6: Risk mitigation or common pitfalls
   - Insight 7: Future implications or emerging trends

3. TWEET-WORTHY: Each insight should be compelling enough to stand alone as a tweet

4. ACTIONABLE: Provide specific value that readers can apply

Ensure NO overlap or repetition between insights. Each must be unique and valuable.
"""

        # Get analysis from LLM using MCP Agent framework
        response = await self.llm.generate_str(message=prompt)
        
        try:
            analysis = json.loads(response)
        except json.JSONDecodeError:
            # Fallback: extract insights manually
            analysis = self._parse_text_response(response)
        
        return ArticleInsights(
            article_number=article['number'],
            article_title=article['title'],
            article_url=article['url'],
            key_insights=analysis.get('key_insights', [])[:7],  # Ensure exactly 7
            themes=analysis.get('themes', []),
            expert_references=analysis.get('expert_references', []),
            frameworks_mentioned=analysis.get('frameworks_mentioned', [])
        )
    
    def _parse_text_response(self, response: str) -> Dict[str, List[str]]:
        """Parse text response if JSON parsing fails."""
        # Simple fallback parser
        lines = response.split('\n')
        insights = []
        themes = []
        experts = []
        frameworks = []
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if 'insight' in line.lower():
                current_section = 'insights'
            elif 'theme' in line.lower():
                current_section = 'themes'
            elif 'expert' in line.lower() or 'reference' in line.lower():
                current_section = 'experts'
            elif 'framework' in line.lower():
                current_section = 'frameworks'
            elif line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                # Extract bullet point
                text = line.lstrip('-•*0123456789. ')
                if current_section == 'insights':
                    insights.append(text)
                elif current_section == 'themes':
                    themes.append(text)
                elif current_section == 'experts':
                    experts.append(text)
                elif current_section == 'frameworks':
                    frameworks.append(text)
        
        return {
            'key_insights': insights[:7],
            'themes': themes,
            'expert_references': experts,
            'frameworks_mentioned': frameworks
        }
    
    async def analyze_multiple_articles(
        self, 
        articles: List[Dict[str, Any]]
    ) -> List[ArticleInsights]:
        """
        Analyze multiple articles.
        
        Args:
            articles: List of article data
            
        Returns:
            List of ArticleInsights
        """
        insights_list = []
        for article in articles:
            insights = await self.analyze_article(article)
            insights_list.append(insights)
        return insights_list


# Standalone function for use in workflows
async def analyze_article_content(
    article: Dict[str, Any],
    agent: Agent = None
) -> Dict[str, Any]:
    """
    Analyze article content and extract insights.
    
    Args:
        article: Article data with number, title, url, and content
        agent: Optional pre-configured MCP Agent instance
        
    Returns:
        Dictionary with insights, themes, experts, and frameworks
    """
    analyzer = MCPContentAnalyzerAgent(agent=agent)
    await analyzer.initialize()
    insights = await analyzer.analyze_article(article)
    
    return {
        "article_number": insights.article_number,
        "article_title": insights.article_title,
        "article_url": insights.article_url,
        "key_insights": insights.key_insights,
        "themes": insights.themes,
        "expert_references": insights.expert_references,
        "frameworks_mentioned": insights.frameworks_mentioned
    }

