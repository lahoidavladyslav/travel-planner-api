from functools import lru_cache

import httpx
from fastapi import HTTPException

ART_API_URL = "https://api.artic.edu/api/v1/artworks"

@lru_cache(maxsize=100)
async def validate_artwork_id(artwork_id: int):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{ART_API_URL}/{artwork_id}")
            if response.status_code == 200:
                return True
            if response.status_code == 404:
                return False
            return False
        except Exception:
            raise HTTPException(status_code=502, detail="External API unavailable")