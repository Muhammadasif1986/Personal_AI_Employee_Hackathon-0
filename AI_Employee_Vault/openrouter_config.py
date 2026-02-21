#!/usr/bin/env python3
"""
Configuration for OpenRouter API integration
"""
import os
import requests
import json
from typing import Dict, List, Optional, Any


class OpenRouterAPI:
    def __init__(self, api_key: str = None):
        """
        Initialize OpenRouter API client
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")

        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def chat_completion(self,
                       messages: List[Dict[str, str]],
                       model: str = "openai/gpt-3.5-turbo",
                       temperature: float = 0.7,
                       max_tokens: Optional[int] = 500) -> Dict[str, Any]:
        """
        Make a chat completion request to OpenRouter
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }

        # Set max_tokens to a lower default to avoid credit issues
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            data=json.dumps(payload)
        )

        if response.status_code != 200:
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

        return response.json()

    def list_models(self) -> Dict[str, Any]:
        """
        List available models on OpenRouter
        """
        response = requests.get(
            f"{self.base_url}/models",
            headers=self.headers
        )

        if response.status_code != 200:
            raise Exception(f"OpenRouter models API error: {response.status_code} - {response.text}")

        return response.json()


def get_available_models(api_key: str = None) -> List[Dict[str, Any]]:
    """
    Convenience function to list available OpenRouter models
    """
    client = OpenRouterAPI(api_key)
    response = client.list_models()
    return response.get("data", [])


def chat_with_openrouter(
    prompt: str,
    system_message: str = "You are a helpful AI assistant.",
    model: str = "openai/gpt-3.5-turbo",
    api_key: str = None,
    temperature: float = 0.7
) -> str:
    """
    Convenience function to chat with OpenRouter API
    """
    client = OpenRouterAPI(api_key)

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

    response = client.chat_completion(
        messages=messages,
        model=model,
        temperature=temperature
    )

    return response["choices"][0]["message"]["content"]


# Example Claude models that can be used via OpenRouter
CLAUDE_MODELS = [
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-3-sonnet",
    "anthropic/claude-3-opus",
    "anthropic/claude-3-haiku"
]

# Example OpenAI models available through OpenRouter
OPENAI_MODELS = [
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "openai/gpt-4-turbo",
    "openai/gpt-3.5-turbo"
]

# Free/paid models available through OpenRouter
FREE_MODELS = [
    "google/gemini-2.0-flash-thinking",  # Free model with reasoning capability
    "google/gemini-2.0-flash",          # Free model
    "openai/gpt-4o-mini",               # Relatively inexpensive
    "anthropic/claude-3-haiku",        # Most economical Claude model
    "mistralai/mistral-7b-instruct",    # Free open source model
    "meta-llama/llama-3.1-8b-instruct"  # Free open source model
]

# Other popular models available through OpenRouter
OTHER_MODELS = [
    "google/gemini-pro",
    "google/gemini-flash",
    "meta-llama/llama-3.1-405b-instruct",
    "mistralai/mistral-nemo",
    "microsoft/wizardlm-2-8x22b"
]

ALL_AVAILABLE_MODELS = CLAUDE_MODELS + OPENAI_MODELS + FREE_MODELS + OTHER_MODELS