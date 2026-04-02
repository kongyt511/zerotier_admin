from fastapi import APIRouter, HTTPException
import httpx
from config import read_config

router = APIRouter()


@router.get("/status")
async def get_status():
    cfg = read_config()
    if not cfg["zt_token"]:
        raise HTTPException(status_code=400, detail="ZeroTier token not configured")
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                f"{cfg['zt_url']}/status",
                headers={"X-ZT1-AUTH": cfg["zt_token"]},
                timeout=5,
            )
            r.raise_for_status()
            return r.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Cannot connect to ZeroTier")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
