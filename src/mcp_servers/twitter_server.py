"""
Twitter MCP Server
Provides tools for posting tweets to Twitter/X.
"""

import os
import re
from typing import Dict, Any, Optional
import tweepy
from datetime import datetime

# MCP Server setup (using LastMile AI's MCP framework)
# NOTE: MCP Server functionality is currently disabled
# The TwitterClient class below can be used directly without MCP
# To enable MCP server, update to use FastMCP API (see mcp-agent examples)
# from mcp.server import Server
# from mcp.types import Tool, TextContent

# Initialize MCP server
# mcp = Server("twitter-server")


def calculate_tweet_length(text: str) -> int:
    """
    Calculate effective tweet length accounting for Twitter's URL shortening.

    Twitter automatically shortens all URLs to 23 characters (t.co links),
    regardless of the original URL length.

    Args:
        text: Tweet text that may contain URLs

    Returns:
        Effective character count after URL shortening
    """
    # Twitter shortens all URLs to 23 characters (t.co links)
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)

    # Replace each URL with 23-character placeholder
    adjusted_text = text
    for url in urls:
        adjusted_text = adjusted_text.replace(url, 'x' * 23, 1)

    return len(adjusted_text)


class TwitterClient:
    """Client for interacting with Twitter API v2."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None
    ):
        """Initialize Twitter client."""
        self.api_key = api_key or os.getenv('TWITTER_API_KEY')
        self.api_secret = api_secret or os.getenv('TWITTER_API_SECRET')
        self.access_token = access_token or os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = access_token_secret or os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        self.client = None
        self.api = None
        
    def authenticate(self):
        """Authenticate with Twitter API."""
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            raise ValueError("Twitter API credentials not provided")
        
        # Twitter API v2 client
        self.client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret
        )
        
        # Twitter API v1.1 (for media upload if needed)
        auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(auth)
        
    def post_tweet(self, text: str) -> Dict[str, Any]:
        """
        Post a tweet.

        Args:
            text: Tweet text (max 280 characters, accounting for URL shortening)

        Returns:
            Dictionary with tweet ID and metadata
        """
        if not self.client:
            self.authenticate()

        # Validate character count (accounting for URL shortening)
        effective_length = calculate_tweet_length(text)
        if effective_length > 280:
            raise ValueError(
                f"Tweet exceeds 280 characters: {effective_length} chars (effective length after URL shortening)\n"
                f"Original length: {len(text)} chars"
            )

        # Post tweet
        response = self.client.create_tweet(text=text)

        return {
            'tweet_id': response.data['id'],
            'text': text,
            'posted_at': datetime.now().isoformat(),
            'character_count': len(text),
            'effective_character_count': effective_length,
            'status': 'posted'
        }
    
    def delete_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Delete a tweet.
        
        Args:
            tweet_id: ID of tweet to delete
            
        Returns:
            Dictionary with deletion status
        """
        if not self.client:
            self.authenticate()
        
        response = self.client.delete_tweet(tweet_id)
        
        return {
            'tweet_id': tweet_id,
            'deleted': response.data['deleted'],
            'deleted_at': datetime.now().isoformat()
        }
    
    def get_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Get tweet details.
        
        Args:
            tweet_id: ID of tweet to retrieve
            
        Returns:
            Dictionary with tweet data
        """
        if not self.client:
            self.authenticate()
        
        response = self.client.get_tweet(
            tweet_id,
            tweet_fields=['created_at', 'public_metrics', 'text']
        )
        
        tweet = response.data
        metrics = tweet.public_metrics
        
        return {
            'tweet_id': tweet.id,
            'text': tweet.text,
            'created_at': tweet.created_at.isoformat(),
            'retweet_count': metrics['retweet_count'],
            'reply_count': metrics['reply_count'],
            'like_count': metrics['like_count'],
            'quote_count': metrics['quote_count'],
            'impression_count': metrics.get('impression_count', 0)
        }
    
    def verify_credentials(self) -> Dict[str, Any]:
        """
        Verify Twitter API credentials.
        
        Returns:
            Dictionary with user info
        """
        if not self.client:
            self.authenticate()
        
        user = self.client.get_me()
        
        return {
            'user_id': user.data.id,
            'username': user.data.username,
            'name': user.data.name,
            'verified': True
        }


# MCP Tools
# NOTE: MCP Server tools are currently disabled
# To enable, update to use FastMCP API (see mcp-agent examples)
# Example: from mcp.server.fastmcp import FastMCP
#
# @mcp.tool()
# async def post_tweet(text: str) -> Dict[str, Any]:
#     """Post a tweet to Twitter/X."""
#     client = TwitterClient()
#     result = client.post_tweet(text)
#     return result
#
# ... (other tools)
#
# if __name__ == "__main__":
#     mcp.run()


# For now, use TwitterClient directly in your code:
# from mcp_servers.twitter_server import TwitterClient
# client = TwitterClient()
# result = client.post_tweet("Hello, world!")

