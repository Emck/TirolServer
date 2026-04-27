"""web_fetch router"""

from dataclasses import asdict

from fastapi import HTTPException, Request
from gunicorn.dirty import get_dirty_client_async

import tirolserver.config as config
from tirolserver.commons import logger
from tirolserver.commons.type import FetchRequest, FetchResponse
from tirolserver.core import CleanerContent


async def web_fetch(request: FetchRequest, raw: Request) -> FetchResponse:
	"""web page fetch interface, return to the cleaned web page content.
	:param request: request parameters (include url, timeout, ...)
	:param raw: original request
	:return: response data
	"""
	try:
		# verify parameter
		if request.url is None:
			raise HTTPException(status_code=500, detail="url is none")
		elif request.timeout > config.Pool_acquire_timeout:
			raise HTTPException(status_code=500, detail=f"timeout set is too large (system max={config.Pool_acquire_timeout})")

		# run dirty func
		client = await get_dirty_client_async()
		result = await client.execute_async(config.dirty_apps[0], "fetch", asdict(request))
		if result["status"] == 200:
			response = FetchResponse(title=result["title"], content=result["body"])
			if request.clean:
				mclean = CleanerContent()
				response.content = mclean.clean(url=request.url, title=response.title, html=response.content)  # clean data

			logger.info(f'[Main] "{raw.method} {raw.url.path}" - 200 length="{len(result["body"])}->{len(response.content)}"')
			return response

			# import aiofiles
			# async with aiofiles.open("output.html", "w", encoding="utf-8") as f:
			# 	logger.debug(f"write {len(result['body'])} characters to output.html")
			# 	await f.write(result["body"])
		else:
			raise HTTPException(status_code=result["status"], detail=result["detail"])

	except HTTPException as e:
		raise e
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"unknow exception {str(type(e))} {str(e)}")
