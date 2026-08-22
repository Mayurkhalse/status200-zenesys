import asyncio
from app.services.llm_service import llm_service

async def main():
    prompt = 'Return ONLY valid JSON with keys: {"status": "ok", "provider": "OpenRouter", "model": "free"}'
    res = await llm_service.generate_json(prompt)
    print("=== OPENROUTER API TEST SUCCESS ===")
    print("Response JSON:", res)

if __name__ == "__main__":
    asyncio.run(main())
