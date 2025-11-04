"""
LiteMAAS API client for integrating with the LLM backend.
"""

import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class LiteMAASClient:
    """Client for interacting with the LiteMAAS API"""

    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the LiteMAAS client.

        Args:
            base_url: Base URL for the LiteMAAS API
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        #self.model = "DeepSeek-R1-Distill-Qwen-14B-W4A16"
        self.model = "Granite-3.3-8B-Instruct"
        self.system_prompt = """You are a friendly Open Source Mentor Bot for a Red Hat hackathon.

Your role:
- Help participants learn about open source contribution
- Explain Red Hat values: Open Collaboration, Transparency, Community First, Automation, Trust
- Guide users on containerization with Podman/Docker
- Share community best practices

Be warm, encouraging, and concise. For greetings, introduce yourself briefly.
"""

    def get_completion(self, user_message: str, max_tokens: int = 1500) -> str:
        """
        Get a completion from the LiteMAAS API.

        Args:
            user_message: The user's input message
            max_tokens: Maximum tokens in the response

        Returns:
            The bot's response text

        Raises:
            Exception: If the API request fails
        """
        try:
            endpoint = f"{self.base_url}/v1/chat/completions"

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }

            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'system',
                        'content': self.system_prompt
                    },
                    {
                        'role': 'user',
                        'content': user_message
                    }
                ],
                'max_tokens': max_tokens,
                'temperature': 0.7,
                'top_p': 0.9
            }

            logger.debug(f"Sending request to {endpoint}")

            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()

            result = response.json()

            # Extract the response text
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0]['message']

                # For reasoning models, prefer content over reasoning_content
                # reasoning_content shows the model's thinking process
                # content shows the final answer
                content = message.get('content')

                # If no content, fall back to reasoning_content and extract the conclusion
                if not content:
                    reasoning = message.get('reasoning_content')
                    if reasoning:
                        # Reasoning models typically provide their conclusion at the END
                        # Split into paragraphs and take the last substantial ones
                        paragraphs = [p.strip() for p in reasoning.split('\n\n') if p.strip()]

                        if paragraphs:
                            # Take the last 2-3 paragraphs (where conclusion typically is)
                            conclusion_parts = []
                            total_length = 0

                            # Work backwards from the end
                            for para in reversed(paragraphs):
                                if total_length + len(para) > 600:
                                    break
                                conclusion_parts.insert(0, para)
                                total_length += len(para)

                            if conclusion_parts:
                                content = '\n\n'.join(conclusion_parts)
                            else:
                                # Fallback: just take the last paragraph
                                content = paragraphs[-1]
                                if len(content) > 500:
                                    content = content[:500] + "..."
                        else:
                            # No paragraphs found, just take a reasonable chunk
                            content = reasoning[:600] if len(reasoning) > 600 else reasoning

                if content:
                    return content
                else:
                    logger.error(f"No content in message: {message}")
                    return "I received a response but couldn't extract the content. Please try again."
            else:
                logger.error(f"Unexpected response format: {result}")
                return "I apologize, but I received an unexpected response format. Please try again."

        except requests.exceptions.Timeout:
            logger.error("LiteMAAS API request timed out")
            return "I'm taking longer than expected to respond. Please try again."

        except requests.exceptions.RequestException as e:
            logger.error(f"LiteMAAS API request failed: {str(e)}")
            return "I'm having trouble connecting to my knowledge base. Please try again later."

        except Exception as e:
            logger.error(f"Unexpected error in get_completion: {str(e)}", exc_info=True)
            return "I encountered an unexpected error. Please try again."
