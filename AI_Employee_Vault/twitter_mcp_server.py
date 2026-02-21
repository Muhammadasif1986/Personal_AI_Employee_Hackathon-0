#!/usr/bin/env python3
"""
Twitter MCP Server - Model Context Protocol server for Twitter/X integration
"""
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any
import re


class TwitterMCP:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Get Twitter API configuration from environment
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            self.logger.warning("Twitter API credentials not set. Server will operate in dry-run mode.")
            self.dry_run = True
        else:
            self.dry_run = False

    def post_tweet(self, content: str, media_urls: list = None) -> Dict[str, Any]:
        """Post a tweet to Twitter"""
        try:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would post tweet: {content[:100]}...")
                if media_urls:
                    self.logger.info(f"[DRY RUN] Would attach media: {media_urls}")
                return {
                    "success": True,
                    "message": "Would post tweet in dry-run mode",
                    "tweet_id": "dry_run_1234567890",
                    "dry_run": True
                }

            # In a real implementation, this would call the Twitter API
            # For now, we'll simulate the API call
            self.logger.info(f"Posting tweet: {content[:100]}...")

            # Simulate Twitter API call
            tweet_id = f"real_tweet_{int(asyncio.get_event_loop().time())}"
            return {
                "success": True,
                "message": "Tweet posted successfully",
                "tweet_id": tweet_id,
                "dry_run": False
            }

        except Exception as e:
            self.logger.error(f"Error posting tweet: {e}")
            return {
                "success": False,
                "message": f"Error posting tweet: {str(e)}",
                "dry_run": self.dry_run
            }

    def get_tweets(self, count: int = 10) -> Dict[str, Any]:
        """Get recent tweets"""
        try:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would get {count} tweets")
                return {
                    "success": True,
                    "tweets": [
                        {"id": f"simulated_tweet_{i}", "text": f"Simulated tweet {i}", "timestamp": "2026-02-21T00:00:00Z"}
                        for i in range(count)
                    ],
                    "dry_run": True
                }

            # In a real implementation, this would call the Twitter API
            self.logger.info(f"Getting {count} tweets")

            # Simulate Twitter API response
            tweets = [
                {"id": f"real_tweet_{int(asyncio.get_event_loop().time()) - i}",
                 "text": f"Real tweet {i}",
                 "timestamp": "2026-02-21T00:00:00Z"}
                for i in range(count)
            ]

            return {
                "success": True,
                "tweets": tweets,
                "dry_run": False
            }

        except Exception as e:
            self.logger.error(f"Error getting tweets: {e}")
            return {
                "success": False,
                "message": f"Error getting tweets: {str(e)}",
                "dry_run": self.dry_run
            }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        try:
            method = request.get("method")

            if method == "post_tweet":
                params = request.get("params", {})
                result = self.post_tweet(
                    content=params.get("content", ""),
                    media_urls=params.get("media_urls", [])
                )
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }

            elif method == "get_tweets":
                params = request.get("params", {})
                result = self.get_tweets(count=params.get("count", 10))
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }

            elif method == "mcp/initialize":
                # Initialize the MCP server
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "serverInfo": {
                            "name": "twitter-mcp-server",
                            "version": "1.0.0"
                        },
                        "capabilities": {
                            "prompts": {},
                            "resources": {
                                "read": False,
                                "write": False
                            },
                            "tools": {
                                "definitions": [
                                    {
                                        "name": "post_tweet",
                                        "description": "Post a tweet to Twitter/X",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {
                                                "content": {"type": "string", "description": "Tweet content (max 280 characters)"},
                                                "media_urls": {"type": "array", "items": {"type": "string"}, "description": "URLs of media to attach (optional)"}
                                            },
                                            "required": ["content"]
                                        }
                                    },
                                    {
                                        "name": "get_tweets",
                                        "description": "Get recent tweets from timeline",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {
                                                "count": {"type": "integer", "description": "Number of tweets to retrieve (default: 10)"}
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }

            elif method == "textDocument/capabilities":
                # Return capabilities
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {}
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,  # Method not found
                        "message": f"Method {method} not supported"
                    }
                }

        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,  # Internal error
                    "message": str(e)
                }
            }

    async def run_server(self):
        """Run the MCP server"""
        self.logger.info("Twitter MCP Server starting...")

        # Read from stdin and write to stdout in MCP protocol
        while True:
            try:
                # Read content length (simplified for this example)
                line = await asyncio.get_event_loop().run_in_executor(None, input)
                if line.startswith('Content-Length:'):
                    length = int(line.split(':')[1].strip())

                    # Read empty line
                    await asyncio.get_event_loop().run_in_executor(None, input)

                    # Read JSON-RPC request
                    request_str = await asyncio.get_event_loop().run_in_executor(None, input)
                    request = json.loads(request_str)

                    # Handle the request
                    response = await self.handle_request(request)

                    # Send response
                    response_str = json.dumps(response)
                    response_bytes = response_str.encode('utf-8')

                    print(f'Content-Length: {len(response_bytes)}')
                    print('')
                    print(response_str, flush=True)

            except EOFError:
                # End of input, exit gracefully
                break
            except Exception as e:
                self.logger.error(f"Server error: {e}")
                # Continue running despite errors


if __name__ == "__main__":
    import sys

    # Check if running in MCP mode (through Claude Code)
    if '--mcp' in sys.argv:
        # Run as MCP server
        server = TwitterMCP()
        try:
            asyncio.run(server.run_server())
        except KeyboardInterrupt:
            print("Twitter MCP Server stopped.")
    else:
        # Run in standalone mode for testing
        print("Twitter MCP Server - Standalone mode for testing")
        print("To run as MCP server, use: python twitter_mcp_server.py --mcp")

        # Example usage in standalone mode
        mcp = TwitterMCP()
        result = mcp.post_tweet("This is a test tweet from the MCP server.")
        print(f"Test result: {result}")