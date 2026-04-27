"""cleanhtml router"""

import asyncio

from fastapi import HTTPException, Request

from tirolserver.commons import logger
from tirolserver.commons.type import CleanHtmlRequest, CleanHtmlResponse
from tirolserver.core import CleanerContent


async def cleanhtml(request: CleanHtmlRequest, raw: Request) -> CleanHtmlResponse:
	"""web page fetch interface, return to the cleaned web page content.
	:param request: request parameters (include url, title, html, timeout, ...)
	:param raw: original request
	:return: response data
	"""
	try:
		# verify parameter
		if request.url is None or not request.url.startswith(("http://", "https://")):
			raise HTTPException(status_code=500, detail="url is invalid")
		elif len(request.html) <= 4:
			raise HTTPException(status_code=500, detail="html is short")

		async with asyncio.timeout(request.timeout):
			mclean = CleanerContent()
			html = mclean.clean(url=request.url, title=request.title, html=request.html)  # clean data
			logger.info(f'[Main] "{raw.method} {raw.url.path}" - 200 length="{len(request.html)}->{len(html)}"')
			return CleanHtmlResponse(title=request.title, content=html)

	except HTTPException as e:
		raise e
	except asyncio.TimeoutError:
		raise HTTPException(status_code=500, detail="cleanhtml timeout")
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"unknow exception {str(type(e))} {str(e)}")
