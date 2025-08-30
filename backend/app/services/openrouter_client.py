"""
OpenRouter client for NewsNeuron
Direct HTTP client for OpenRouter API without OpenAI dependencies
"""
import httpx
import json
import logging
from typing import Dict, Any, List, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """
    Simple OpenRouter client using httpx instead of OpenAI library
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Set up headers
        self.headers = {
            "Content-Type": "application/json",
            "HTTP-Referer": "https://newseuron.ai",  # Optional: for OpenRouter analytics
            "X-Title": "NewsNeuron"  # Optional: for OpenRouter analytics
        }
        
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def is_available(self) -> bool:
        """Check if OpenRouter client is properly configured"""
        return bool(self.api_key)
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion using OpenRouter API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to settings default)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
        
        Returns:
            OpenRouter API response
        """
        if not self.is_available():
            raise Exception("OpenRouter API key not configured")
        
        # Prepare request data
        data = {
            "model": model or settings.default_llm_model,
            "messages": messages,
            "max_tokens": max_tokens or settings.max_tokens,
            "temperature": temperature if temperature is not None else settings.temperature,
            **kwargs
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=data
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"OpenRouter API error {response.status_code}: {error_text}")
                    raise Exception(f"OpenRouter API error: {response.status_code} - {error_text}")
                
                result = response.json()
                
                # Validate response structure
                if "choices" not in result or not result["choices"]:
                    raise Exception("Invalid response from OpenRouter API")
                
                return result
                
        except httpx.TimeoutException:
            logger.error("OpenRouter API request timeout")
            raise Exception("OpenRouter API request timeout")
        except httpx.RequestError as e:
            logger.error(f"OpenRouter API request error: {str(e)}")
            raise Exception(f"OpenRouter API request error: {str(e)}")
        except json.JSONDecodeError:
            logger.error("Invalid JSON response from OpenRouter API")
            raise Exception("Invalid JSON response from OpenRouter API")
        except Exception as e:
            logger.error(f"Unexpected error calling OpenRouter API: {str(e)}")
            raise
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Get available models from OpenRouter
        
        Returns:
            List of available models
        """
        if not self.is_available():
            return []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("data", [])
                else:
                    logger.warning(f"Failed to get models from OpenRouter: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.warning(f"Error getting models from OpenRouter: {str(e)}")
            return []
    
    def extract_message_content(self, response: Dict[str, Any]) -> str:
        """
        Extract the message content from OpenRouter response
        
        Args:
            response: OpenRouter API response
        
        Returns:
            The message content string
        """
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise Exception("Could not extract message content from OpenRouter response")


# Global OpenRouter client instance
_openrouter_client: Optional[OpenRouterClient] = None


def get_openrouter_client() -> OpenRouterClient:
    """Get singleton OpenRouter client instance"""
    global _openrouter_client
    if _openrouter_client is None:
        _openrouter_client = OpenRouterClient()
    return _openrouter_client


def is_openrouter_available() -> bool:
    """Check if OpenRouter is available and configured"""
    client = get_openrouter_client()
    return client.is_available()
