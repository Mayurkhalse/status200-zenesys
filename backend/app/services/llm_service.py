import json
import re
import asyncio
import httpx
from typing import Any, Dict, Optional
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL

    async def generate_completion(self, prompt: str) -> str:
        """Invokes Gemini 2.5 Flash model and returns text output."""
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            # Dev mock fallback if no real key provided yet
            return "{}"

        # Attempt call via official Google Generative AI / REST endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.1
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                print(f"Gemini API warning ({response.status_code}): {response.text}")
            except Exception as e:
                print(f"Gemini API call failed: {e}")
        return "{}"

    async def generate_json(self, prompt: str) -> Any:
        """Invokes LLM and cleans markdown fences to parse valid JSON."""
        raw_text = await self.generate_completion(prompt)
        cleaned = re.sub(r"^```(?:json)?", "", raw_text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE).strip()
        
        try:
            return json.loads(cleaned)
        except Exception:
            # Try finding first { or [ and last } or ]
            first_brace = min([pos for pos in [cleaned.find('{'), cleaned.find('[')] if pos != -1], default=-1)
            last_brace = max([cleaned.rfind('}'), cleaned.rfind(']')], default=-1)
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                sub = cleaned[first_brace:last_brace+1]
                try:
                    return json.loads(sub)
                except Exception:
                    pass
        return {} if "{" in cleaned else []

llm_service = LLMService()
