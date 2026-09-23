from typing import List, Dict, Any, Optional
import httpx
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.exceptions.exceptions import AIServiceException


class GroqLLMClient:
    """Direct, asynchronous client for Groq LLM completions using httpx."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self.api_url = settings.GROQ_API_URL

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """Call Groq chat completion API and return generated text content."""
        if not self.api_key:
            raise AIServiceException("GROQ_API_KEY is not configured in backend environment.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)

            if response.status_code != 200:
                logger.error(f"Groq API error ({response.status_code}): {response.text}")
                raise AIServiceException(
                    f"Groq API returned HTTP {response.status_code}: {response.text}"
                )

            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                raise AIServiceException("Groq API returned an empty choices list.")

            content = choices[0].get("message", {}).get("content", "")
            return content.strip()

        except httpx.RequestError as e:
            logger.error(f"Network error calling Groq API: {e}")
            raise AIServiceException(f"Network failure connecting to Groq: {str(e)}")


# Global LLM client instance
llm_client = GroqLLMClient()
