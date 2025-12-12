"""
Groq LLM Client
Handles all interactions with Groq API for text generation
"""
from groq import Groq
from typing import List, Dict, Optional, AsyncIterator
import json
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GroqClient:
    """Client for interacting with Groq LLM API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq client"""
        self.api_key = api_key or settings.GROQ_API_KEY
        self.client = Groq(api_key=self.api_key)
        self.model = settings.GROQ_MODEL
        
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False
    ) -> str:
        """
        Generate completion from Groq
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response
            
        Returns:
            Generated text or stream iterator
        """
        try:
            temperature = temperature or settings.TEMPERATURE
            max_tokens = max_tokens or settings.MAX_TOKENS
            
            logger.info(f"Generating completion with {len(messages)} messages")

            # DEBUG: Print actual messages being sent
            print("\n========== MESSAGES SENT TO LLM ==========")
            for i, msg in enumerate(messages):
                print(f"Message {i} - Role: {msg.get('role')}")
                print(f"Content: {msg.get('content')[:200]}...")  # First 200 chars
                print("---")
            print("==========================================\n")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                return self._handle_stream(response)
            else:
                content = response.choices[0].message.content
                logger.info(f"Generated {len(content)} characters")
                return content
                
        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise
    
    def _handle_stream(self, stream) -> AsyncIterator[str]:
        """Handle streaming response"""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def generate_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict],
        temperature: float = None
    ) -> Dict:
        """
        Generate completion with tool calling support
        
        Args:
            messages: Conversation messages
            tools: Available tools/functions
            temperature: Sampling temperature
            
        Returns:
            Response dict with content or tool calls
        """
        try:
            temperature = temperature or settings.TEMPERATURE
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                temperature=temperature,
                max_tokens=settings.MAX_TOKENS
            )
            
            choice = response.choices[0]
            
            # Check if model wants to call a tool
            if choice.message.tool_calls:
                return {
                    "type": "tool_call",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "name": tc.function.name,
                            "arguments": json.loads(tc.function.arguments)
                        }
                        for tc in choice.message.tool_calls
                    ]
                }
            else:
                return {
                    "type": "text",
                    "content": choice.message.content
                }
                
        except Exception as e:
            logger.error(f"Error in tool generation: {str(e)}")
            raise
    
    async def generate_structured(
        self,
        messages: List[Dict[str, str]],
        response_format: Dict,
        temperature: float = 0.3
    ) -> Dict:
        """
        Generate structured JSON response
        
        Args:
            messages: Conversation messages
            response_format: Expected JSON schema
            temperature: Lower temp for more consistent structure
            
        Returns:
            Parsed JSON response
        """
        try:
            # Add instruction to return JSON
            system_msg = {
                "role": "system",
                "content": f"You must respond with valid JSON matching this schema: {json.dumps(response_format)}"
            }
            
            full_messages = [system_msg] + messages
            
            response = await self.generate(
                messages=full_messages,
                temperature=temperature
            )
            
            # Parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                    return json.loads(json_str)
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0].strip()
                    return json.loads(json_str)
                else:
                    raise ValueError("Could not parse JSON from response")
                    
        except Exception as e:
            logger.error(f"Error generating structured response: {str(e)}")
            raise


# Global client instance
groq_client = GroqClient()
