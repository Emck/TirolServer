"""test router"""

import asyncio

from fastapi import HTTPException, Request

from tirolserver.utils import logger


async def test(raw: Request) -> dict:
	try:
		logger.info(f'[Main] "{raw.method} {raw.url.path}" - 200')
		return {"test": "test ok"}

	except HTTPException as e:
		raise e
	except asyncio.TimeoutError:
		raise HTTPException(status_code=500, detail="test timeout")
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"unknow exception {str(type(e))} {str(e)}")
