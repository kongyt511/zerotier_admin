from fastapi import APIRouter, HTTPException
import httpx
from config import read_config

router = APIRouter()


def zt_headers(cfg: dict) -> dict:
    return {"X-ZT1-AUTH": cfg["zt_token"]}


def check_token(cfg: dict):
    if not cfg["zt_token"]:
        raise HTTPException(status_code=400, detail="ZeroTier token not configured")


@router.get("")
async def list_members(nwid: str):
    cfg = read_config()
    check_token(cfg)
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                f"{cfg['zt_url']}/controller/network/{nwid}/member",
                headers=zt_headers(cfg),
                timeout=5,
            )
            r.raise_for_status()
            member_ids = r.json()
            members = []
            for mid in member_ids:
                mr = await client.get(
                    f"{cfg['zt_url']}/controller/network/{nwid}/member/{mid}",
                    headers=zt_headers(cfg),
                    timeout=5,
                )
                if mr.status_code == 200:
                    members.append(mr.json())
            return members
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Cannot connect to ZeroTier")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.get("/{mid}")
async def get_member(nwid: str, mid: str):
    cfg = read_config()
    check_token(cfg)
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                f"{cfg['zt_url']}/controller/network/{nwid}/member/{mid}",
                headers=zt_headers(cfg),
                timeout=5,
            )
            r.raise_for_status()
            return r.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Cannot connect to ZeroTier")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.put("/{mid}")
async def update_member(nwid: str, mid: str, body: dict):
    cfg = read_config()
    check_token(cfg)
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                f"{cfg['zt_url']}/controller/network/{nwid}/member/{mid}",
                headers=zt_headers(cfg),
                json=body,
                timeout=5,
            )
            r.raise_for_status()
            return r.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Cannot connect to ZeroTier")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.delete("/{mid}")
async def delete_member(nwid: str, mid: str):
    cfg = read_config()
    check_token(cfg)
    async with httpx.AsyncClient() as client:
        try:
            r = await client.delete(
                f"{cfg['zt_url']}/controller/network/{nwid}/member/{mid}",
                headers=zt_headers(cfg),
                timeout=5,
            )
            r.raise_for_status()
            return r.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Cannot connect to ZeroTier")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
