import httpx
import json
import logging
import os
from typing import Optional
from app.contracts.providers.i_llm_provider import ILLMProvider, ExtractionResult

logger = logging.getLogger(__name__)


class GeminiProvider(ILLMProvider):
    """
    Summary: Implementation of ILLMProvider for Google Gemini (Free Tier).
    Provides high-performance cloud inference with generous free usage limits.
    """

    # Using v1beta as it supports the latest flash models and JSON response mode
    API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    INTENT_SYSTEM_PROMPT = (
        "You are a specialized JSON intent extractor for a dataset discovery platform. "
        "Your job is to determine if a user's message requires a semantic search. "
        "You MUST return a JSON object with EXACTLY these three fields:\n"
        "1. 'is_search_required': (boolean) true if the user is looking for datasets or info we might have in our vector store.\n"
        "2. 'search_query': (string or null) the optimized search terms if is_search_required is true.\n"
        "3. 'reasoning': (string) a brief explanation of why you made this decision.\n"
        "DO NOT add any other fields."
    )

    def __init__(self, model_name: str = "gemini-flash-latest", api_key: Optional[str] = None):
        
        self._model = model_name
        self._api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self._api_key:
            
            raise ValueError(
                "GEMINI_API_KEY environment variable is required. "
                "Get your free API key at https://aistudio.google.com"
            )
            
        self._url = self.API_URL_TEMPLATE.format(model=model_name, api_key=self._api_key)

    async def generate_response(self, prompt: str, system_message: str) -> str:
        """
        Summary: Generates a natural language response using Google Gemini.
        """

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_message}\n\nUser Message: {prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048
            }
        }

        try:
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                
                response = await client.post(self._url, json=payload)
                
                if response.status_code != 200:
                    
                    # Robust error parsing
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", "Unknown API Error")
                    except:
                        error_msg = response.text[:200]
                    
                    logger.error(f"Gemini API Error [{response.status_code}]: {error_msg}")
                    
                    return f"I'm sorry, I'm having trouble thinking right now. (API Error {response.status_code}: {error_msg})"
                
                data = response.json()
                
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()

        except httpx.TimeoutException:
            
            logger.error("Gemini API timeout - request took longer than 60 seconds")
            return "I'm sorry, the request timed out. Please try again."

        except Exception as e:
            
            logger.error(f"Gemini API unexpected error: {str(e)}", exc_info=True)
            return f"I'm sorry, I encountered an unexpected error: {str(e)}"

    async def extract_intent(self, prompt: str) -> ExtractionResult:
        """
        Summary: Extracts structured intent from user input using Gemini's native JSON mode.
        """
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{self.INTENT_SYSTEM_PROMPT}\n\nTask: {prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.0,
                "responseMimeType": "application/json"
            }
        }

        try:
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                
                response = await client.post(self._url, json=payload)
                
                if response.status_code != 200:
                    
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", "Unknown API Error")
                    except:
                        error_msg = response.text[:200]
                    
                    logger.error(f"Gemini API Error [{response.status_code}]: {error_msg}")
                    
                    return ExtractionResult(
                        is_search_required=False,
                        search_query=None,
                        reasoning=f"Gemini API unreachable ({response.status_code}: {error_msg})"
                    )

                data = response.json()
                raw_content = data["candidates"][0]["content"]["parts"][0]["text"]
                
                try:
                    
                    intent_data = json.loads(raw_content)
                    return ExtractionResult(**intent_data)

                except (json.JSONDecodeError, TypeError) as e:
                    
                    logger.error(f"Gemini JSON parsing error: {e}. Raw content: {raw_content}")
                    return ExtractionResult(
                        is_search_required=False,
                        search_query=None,
                        reasoning="Failed to parse structured intent from response"
                    )

        except Exception as e:
            
            logger.error(f"Error during Gemini intent extraction: {str(e)}")
            return ExtractionResult(
                is_search_required=False,
                search_query=None,
                reasoning=f"Unexpected error: {str(e)}"
            )
