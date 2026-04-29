"""cleanhtml router"""

import asyncio
from dataclasses import dataclass

from fastapi import HTTPException, Request

from tirolserver.core import CleanerContent
from tirolserver.utils import logger


@dataclass
class CleanHtmlRequest:
	"""request parameters
	:param url: The target URL to retrieve data from.
	:param html: The target URL html content.
	:param title: The target URL html title.
	:param timeout: The maximum time in seconds to wait for cleanHtml request.
	"""

	url: str | None = None
	html: str = ""
	title: str = ""
	timeout: int = 10


@dataclass
class CleanHtmlResponse:
	"""response web page info
	:param title: page title
	:param content: page content
	"""

	title: str | None = None
	content: str | None = None


async def cleanhtml(request: CleanHtmlRequest, raw: Request) -> CleanHtmlResponse:
	"""clean html interface, return to the cleaned web page content.
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
