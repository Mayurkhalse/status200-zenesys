import os
import json
import re
import asyncio
import httpx
from typing import Any, Dict, Optional
from app.core.config import settings

FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct",
    "google/gemini-2.5-flash",
    "google/gemma-2-9b-it:free",
    "meta-llama/llama-3-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen-2.5-72b-instruct"
]

class LLMService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY or settings.GEMINI_API_KEY
        self.model = settings.OPENROUTER_MODEL or "meta-llama/llama-3.3-70b-instruct"
        self.base_url = settings.OPENROUTER_BASE_URL or "https://openrouter.ai/api/v1"

    async def generate_completion(self, prompt: str) -> str:
        """Invokes OpenRouter API using free model tier (OpenAI ChatCompletions standard)."""
        api_key = settings.OPENROUTER_API_KEY or os.environ.get("OPENROUTER_API_KEY", "")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://intelliparse.ai",
            "X-Title": "IntelliParse AI",
            "Content-Type": "application/json"
        }

        # Try models starting with configured model, then fallback free models
        models_to_try = [self.model] + [m for m in FREE_MODELS if m != self.model]

        async with httpx.AsyncClient(timeout=30.0) as client:
            for model_name in models_to_try:
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1
                }
                try:
                    res = await client.post(url, headers=headers, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        choices = data.get("choices", [])
                        if choices:
                            text = choices[0].get("message", {}).get("content", "")
                            if text:
                                return text
                    elif res.status_code in [404, 429]:
                        print(f"OpenRouter note on {model_name} ({res.status_code}), trying next model...")
                        continue
                    else:
                        print(f"OpenRouter API warning ({res.status_code}): {res.text}")
                except Exception as e:
                    print(f"OpenRouter API call error ({model_name}): {e}")

        # Fallback to direct Gemini endpoint if OpenRouter is unconfigured
        return await self._fallback_gemini_call(prompt)

    async def _fallback_gemini_call(self, prompt: str) -> str:
        """Fallback to direct Gemini REST endpoint if OpenRouter API is unconfigured."""
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
            return "{}"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    candidates = res.json().get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
        except Exception:
            pass
        return "{}"

    async def generate_json(self, prompt: str) -> Any:
        """Invokes OpenRouter API and cleans markdown fences to parse valid JSON."""
        raw_text = await self.generate_completion(prompt)
        cleaned = re.sub(r"^```(?:json)?", "", raw_text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE).strip()
        
        try:
            return json.loads(cleaned)
        except Exception:
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
