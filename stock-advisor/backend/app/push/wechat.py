"""WeChat push via Server酱 (sct.ftqq.com) or PushPlus (pushplus.plus)."""

import httpx

from app.config import settings


async def push_wechat(title: str, content: str) -> bool:
    """
    Push message to WeChat.
    Tries PushPlus first, then Server酱 as fallback.
    """
    # Try PushPlus
    if settings.pushplus_token:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://www.pushplus.plus/send",
                    json={
                        "token": settings.pushplus_token,
                        "title": title,
                        "content": content,
                        "template": "html",
                    },
                    timeout=10,
                )
                if resp.status_code == 200:
                    return True
        except Exception:
            pass

    # Try Server酱
    if settings.wechat_push_token:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://sctapi.ftqq.com/{settings.wechat_push_token}.send",
                    params={"title": title, "desp": content},
                    timeout=10,
                )
                if resp.status_code == 200:
                    return True
        except Exception:
            pass

    return False
