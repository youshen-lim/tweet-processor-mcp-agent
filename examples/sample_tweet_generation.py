"""
Sample Tweet Generation from CoreAI Newsletter Article #1
Demonstrates what the Tweet Processor will generate from your articles.
"""

# Sample article data extracted from your screenshot
ARTICLE_1 = {
    "number": 1,
    "title": "Creating Business Value with AI (Part 2) - What I Learned from Cornell (Republished Version)",
    "url": "https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/",
    "content": """
    Cornell University's eCornell "Designing and Building AI Solutions" Program (Under Lutz Finger's 
    instruction) transforms how business leaders and managers approach artificial intelligence implementation.
    
    This first program module "Creating Business Value With AI" cuts through technical complexity and 
    industry hype to focus on practical applications that align with business objectives to create value. 
    This systematic approach begins with identifying the right business problems, determines whether AI 
    suits those problems, and identifies which AI product/solution approach generates the most value. The 
    course design combines content with value-driven applications, including insightful speaker sessions 
    with industry experts like Dr. Guy Berger, Ph.D., former Principal Economist of LinkedIn who provided 
    valuable and practical perspectives on leveraging labor data analytics in the industry.
    
    Differentiating Between AI Areas and Applications
    
    One key learning was how to differentiate between AI areas and applications. The course outlined how 
    Good Old-Fashioned AI (GOFAI), deep learning, generative AI, and foundation models all serve different 
    purposes. Rather than viewing newer AI technologies as inherently superior, I learned to match the 
    approach to the specific business problem. For instance, rule-based GOFAI might be more appropriate...
    """
}

# Key insights extracted (what the Content Analyzer Agent would produce)
KEY_INSIGHTS = [
    "Cornell's program teaches business-first AI implementation, not tech-first",
    "Systematic approach: identify problems → assess AI suitability → select best solution",
    "Differentiate between GOFAI, deep learning, generative AI, and foundation models",
    "Match AI approach to business problem, not just newest technology",
    "Industry expert insights from Dr. Guy Berger on labor data analytics",
    "Focus on practical applications aligned with business objectives",
    "Value-driven approach cuts through technical complexity and hype"
]

# Sample tweets generated (what the Tweet Composer Agent would produce)
SAMPLE_TWEETS = [
    {
        "version": 1,
        "focus": "Business Value",
        "tweet": """🎯 AI implementation isn't about the newest tech—it's about business value.

Cornell's program taught me: Start with the problem, not the solution. Sometimes rule-based GOFAI beats cutting-edge models.

Key: Match AI approach to business needs.

Read more: https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/

#AI #DataStrategy""",
        "character_count": 278,
        "hashtags": ["#AI", "#DataStrategy"],
        "key_points_used": [
            "Match AI approach to business problem, not just newest technology",
            "Focus on practical applications aligned with business objectives"
        ]
    },
    {
        "version": 2,
        "focus": "Systematic Approach",
        "tweet": """💡 Cornell's AI program breaks down implementation into 3 steps:

1️⃣ Identify the right business problems
2️⃣ Determine if AI suits those problems
3️⃣ Select which AI solution generates most value

Systematic > Hype-driven

https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/

#AI #BusinessStrategy""",
        "character_count": 276,
        "hashtags": ["#AI", "#BusinessStrategy"],
        "key_points_used": [
            "Systematic approach: identify problems → assess AI suitability → select best solution",
            "Value-driven approach cuts through technical complexity and hype"
        ]
    },
    {
        "version": 3,
        "focus": "AI Differentiation",
        "tweet": """🔍 Not all AI is created equal.

Cornell taught me to differentiate:
• GOFAI (rule-based)
• Deep learning
• Generative AI
• Foundation models

Each serves different purposes. Choose based on your business problem, not the hype.

https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/

#AI #MachineLearning""",
        "character_count": 279,
        "hashtags": ["#AI", "#MachineLearning"],
        "key_points_used": [
            "Differentiate between GOFAI, deep learning, generative AI, and foundation models",
            "Match AI approach to business problem, not just newest technology"
        ]
    },
    {
        "version": 4,
        "focus": "Expert Insights",
        "tweet": """🎓 Cornell's AI program featured Dr. Guy Berger (former Principal Economist @LinkedIn).

His insights on labor data analytics show how AI aligns with real business objectives—not just technical capabilities.

Practical > Theoretical

https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/

#AI #DataAnalytics""",
        "character_count": 277,
        "hashtags": ["#AI", "#DataAnalytics"],
        "key_points_used": [
            "Industry expert insights from Dr. Guy Berger on labor data analytics",
            "Focus on practical applications aligned with business objectives"
        ]
    }
]


def display_sample_tweets():
    """Display sample tweets in a formatted way."""
    print("=" * 80)
    print("SAMPLE TWEET GENERATION FROM ARTICLE #1")
    print("=" * 80)
    print()
    
    print("📄 ARTICLE INFORMATION")
    print("-" * 80)
    print(f"Number: {ARTICLE_1['number']}")
    print(f"Title: {ARTICLE_1['title']}")
    print(f"URL: {ARTICLE_1['url']}")
    print()
    
    print("🔍 KEY INSIGHTS EXTRACTED (7 total)")
    print("-" * 80)
    for i, insight in enumerate(KEY_INSIGHTS, 1):
        print(f"{i}. {insight}")
    print()
    
    print("🐦 GENERATED TWEETS (4 variations)")
    print("-" * 80)
    for tweet_data in SAMPLE_TWEETS:
        print()
        print(f"VERSION {tweet_data['version']}: {tweet_data['focus']}")
        print(f"Characters: {tweet_data['character_count']}/280")
        print(f"Hashtags: {', '.join(tweet_data['hashtags'])}")
        print()
        print(tweet_data['tweet'])
        print()
        print("Key Points Used:")
        for point in tweet_data['key_points_used']:
            print(f"  • {point}")
        print("-" * 80)
    
    print()
    print("=" * 80)
    print("WEEKLY ROTATION EXAMPLE")
    print("=" * 80)
    print()
    print("Week 1: Article #1, Version 1 (Business Value focus)")
    print("Week 2: Article #2, Version 1")
    print("Week 3: Article #3, Version 1")
    print("...")
    print("Week 25: Article #25, Version 1")
    print("Week 26: Article #1, Version 2 (Systematic Approach focus)")
    print("Week 27: Article #2, Version 2")
    print("...")
    print()
    print("Result: Fresh content for 75-100 weeks (~1.5-2 years)!")
    print("=" * 80)


if __name__ == "__main__":
    display_sample_tweets()

