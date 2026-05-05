"""api/testdb router"""

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request

from tirolserver.core import DataBase
from tirolserver.utils import get_clean_db, logger

from ...utils import router_path


async def testdb(raw: Request, db: DataBase = Depends(get_clean_db)) -> dict:
	try:
		print(f"{await db.async_get('d.avaw.com')}")
		logger.info(f'[Main] "{raw.method} {raw.url.path}" - 200')
		return {"testdb": "test ok"}

	except HTTPException as e:
		raise e
	except asyncio.TimeoutError:
		raise HTTPException(status_code=500, detail="teatapi timeout")
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"unknow exception {str(type(e))} {str(e)}")


#: fastapi routers
_router_api_testdb: APIRouter = APIRouter()

# add api/testdb router
_router_api_testdb.add_api_route(router_path(__file__, testdb), testdb, methods=["GET"])
