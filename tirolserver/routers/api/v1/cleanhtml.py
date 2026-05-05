"""cleanhtml router"""

import asyncio
from dataclasses import dataclass

from fastapi import HTTPException, Request

from tirolserver.core.markdown import HtmlToMarkdown
from tirolserver.utils import logger


@dataclass
class CleanHtmlRequest:
	"""request parameters
	:param html: The target URL html content.
	:param title: The target URL html title.
	:param url: The target URL to retrieve data from.
	:param timeout: The maximum time in seconds to wait for cleanHtml request.
	"""

	html: str = ""
	title: str = ""
	url: str = "https://demo.com"  # default any url
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
		if not request.url or not request.url.startswith(("http://", "https://")):
			raise HTTPException(status_code=500, detail="url is invalid")
		elif len(request.html) <= 4:
			raise HTTPException(status_code=500, detail="html is empty or too short")

		async with asyncio.timeout(request.timeout):
			markdown = HtmlToMarkdown()
			mdtext, info = markdown.toMarkdown(html=request.html, title=request.title, url=request.url)  # transform to markdown
			logger.info(f'[Main] "{raw.method} {raw.url.path}" - 200 length="original: {len(request.html)} -> cleaned: {len(mdtext)}"')
			return CleanHtmlResponse(title=request.title if request.title else info["title"], content=mdtext)

	except HTTPException as e:
		raise e
	except asyncio.TimeoutError:
		raise HTTPException(status_code=500, detail="cleanhtml timeout")
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"unknow exception {str(type(e))} {str(e)}")
