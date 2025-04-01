from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import httpx
import asyncio
from typing import Optional

async def proxy_image(url: str) -> tuple[bytes, str]:
    """
    代理获取图片内容
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, follow_redirects=True, timeout=30.0)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="URL 不是有效的图片")
                
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > 4 * 1024 * 1024:  # 4MB
                raise HTTPException(status_code=400, detail="图片大小不能超过 4MB")
                
            return response.content, content_type
            
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="获取图片超时")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="无法访问图片")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
