from fastapi import APIRouter, HTTPException
import httpx
from config import read_config

router = APIRouter()


def zt_headers(cfg: dict) -> dict:
    return {"X-ZT1-AUTH": cfg["zt_token"]}


def check_token(cfg: dict):
    if not cfg["zt_token"]:
        raise HTTPException(status_code=400, detail="ZeroTier token not configured")


async def zt_node_id(cfg: dict, client: httpx.AsyncClient) -> str:
    r = await client.get(
        f"{cfg['zt_url']}/status",
        headers=zt_headers(cfg),
        timeout=5,
    )
    r.raise_for_status()
    return r.json()["address"]


@router.get("")
async def list_networks():
    cfg = read_config()
    check_token(cfg)
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                f"{cfg['zt_url']}/controller/network",
                headers=zt_headers(cfg),
                timeout=5,
            )
            r.raise_for_status()
            network_ids = r.json()
            # Fetch each network's details
            networks = []
            for nwid in network_ids:
                nr = await client.get(
                    f"{cfg['zt_url']}/controller/network/{nwid}",
                    headers=zt_headers(cfg),
                    timeout=5,
                )
                if nr.status_code == 200:
                    networks.append(nr.json())
            return networks
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Cannot connect to ZeroTier")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.post("")
async def create_network(body: dict = {}):
    cfg = read_config()
    check_token(cfg)
    async with httpx.AsyncClient() as client:
        try:
            node_id = await zt_node_id(cfg, client)
            r = await client.post(
                f"{cfg['zt_url']}/controller/network/{node_id}______",
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


@router.get("/{nwid}")
async def get_network(nwid: str):
    cfg = read_config()
    check_token(cfg)
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                f"{cfg['zt_url']}/controller/network/{nwid}",
                headers=zt_headers(cfg),
                timeout=5,
            )
            r.raise_for_status()
            return r.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Cannot connect to ZeroTier")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.put("/{nwid}")
async def update_network(nwid: str, body: dict):
    cfg = read_config()
    check_token(cfg)
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(
                f"{cfg['zt_url']}/controller/network/{nwid}",
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


@router.delete("/{nwid}")
async def delete_network(nwid: str):
    cfg = read_config()
    check_token(cfg)
    async with httpx.AsyncClient() as client:
        try:
            r = await client.delete(
                f"{cfg['zt_url']}/controller/network/{nwid}",
                headers=zt_headers(cfg),
                timeout=5,
            )
            r.raise_for_status()
            return r.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Cannot connect to ZeroTier")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.get("/{nwid}/export")
async def export_network(nwid: str):
    """Export full network config + all members as a single JSON blob."""
    cfg = read_config()
    check_token(cfg)
    async with httpx.AsyncClient() as client:
        try:
            nr = await client.get(
                f"{cfg['zt_url']}/controller/network/{nwid}",
                headers=zt_headers(cfg), timeout=5,
            )
            nr.raise_for_status()
            mr = await client.get(
                f"{cfg['zt_url']}/controller/network/{nwid}/member",
                headers=zt_headers(cfg), timeout=5,
            )
            mr.raise_for_status()
            member_ids = mr.json()
            members = []
            for mid in member_ids:
                m = await client.get(
                    f"{cfg['zt_url']}/controller/network/{nwid}/member/{mid}",
                    headers=zt_headers(cfg), timeout=5,
                )
                if m.status_code == 200:
                    members.append(m.json())
            return {"network": nr.json(), "members": members}
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Cannot connect to ZeroTier")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.post("/{nwid}/import")
async def import_network(nwid: str, body: dict):
    """Restore network config and members from an exported blob."""
    cfg = read_config()
    check_token(cfg)
    network_cfg = body.get("network", {})
    members_cfg = body.get("members", [])

    # Strip read-only fields
    for key in ("id", "nwid", "objtype", "revision", "creationTime"):
        network_cfg.pop(key, None)

    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{cfg['zt_url']}/controller/network/{nwid}",
                headers=zt_headers(cfg), json=network_cfg, timeout=5,
            )
            for m in members_cfg:
                mid = m.get("nodeId") or m.get("id")
                if not mid:
                    continue
                payload = {k: v for k, v in m.items()
                           if k not in ("id", "nwid", "objtype", "revision")}
                await client.post(
                    f"{cfg['zt_url']}/controller/network/{nwid}/member/{mid}",
                    headers=zt_headers(cfg), json=payload, timeout=5,
                )
            return {"ok": True, "members_restored": len(members_cfg)}
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Cannot connect to ZeroTier")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
