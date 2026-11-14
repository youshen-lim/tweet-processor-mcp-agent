"""
Twitter MCP Server
Provides tools for posting tweets to Twitter/X.
"""

import os
import re
import ssl
import time
import traceback
from typing import Dict, Any, Optional
import requests
import tweepy
from urllib3.exceptions import ConnectTimeoutError, NewConnectionError
from datetime import datetime

# Retries for create_tweet when the connection fails before the request is sent.
POST_CONNECT_ATTEMPTS = 3
POST_CONNECT_BACKOFF_SECONDS = 5


def _failed_before_send(exc: BaseException) -> bool:
    """
    True only when the error provably happened before the HTTP request reached X:
    TCP connect failure/timeout, DNS failure, or a TLS handshake failure.

    Errors after the request was sent (connection reset while reading the response,
    read timeouts, HTTP errors) return False. Those are never retried, because the
    tweet may already have been posted and a retry could post it twice.
    """
    if isinstance(exc, requests.exceptions.ConnectTimeout):
        return True
    seen = set()
    stack = [exc]
    while stack:
        err = stack.pop()
        if err is None or id(err) in seen:
            continue
        seen.add(id(err))
        # NameResolutionError subclasses NewConnectionError in urllib3 2.x.
        if isinstance(err, (NewConnectionError, ConnectTimeoutError)):
            return True
        # ssl.SSLError (e.g. SSLEOFError) or a ConnectionResetError raised inside
        # the TLS handshake: no HTTP bytes have been sent yet.
        if isinstance(err, (ssl.SSLError, OSError)) and err.__traceback__ is not None:
            frames = traceback.extract_tb(err.__traceback__)
            if any(frame.name == 'do_handshake' for frame in frames):
                return True
        stack.extend([err.__cause__, err.__context__, getattr(err, 'reason', None)])
        stack.extend(a for a in getattr(err, 'args', ()) if isinstance(a, BaseException))
    return False

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

        # Post tweet. Retry only connection failures that happened before the
        # request was sent (e.g. the 2026-11-14 TLS handshake EOF); anything
        # later is re-raised so a tweet is never posted twice.
        for attempt in range(1, POST_CONNECT_ATTEMPTS + 1):
            try:
                response = self.client.create_tweet(text=text)
                break
            except requests.exceptions.RequestException as e:
                if attempt < POST_CONNECT_ATTEMPTS and _failed_before_send(e):
                    delay = POST_CONNECT_BACKOFF_SECONDS * attempt
                    print(
                        f"⚠️  Connection to X failed before the tweet was sent "
                        f"({type(e).__name__}); retrying in {delay}s "
                        f"(attempt {attempt + 1}/{POST_CONNECT_ATTEMPTS})"
                    )
                    time.sleep(delay)
                    continue
                raise

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

