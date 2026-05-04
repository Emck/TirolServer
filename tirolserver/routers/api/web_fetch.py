"""web_fetch router"""

from dataclasses import asdict, dataclass

from fastapi import HTTPException, Request
from gunicorn.dirty import get_dirty_client_async

import tirolserver.config as config
from tirolserver.core.markdown import HtmlToMarkdown
from tirolserver.utils import logger


@dataclass
class WebFetchRequest:
	"""web fetch request parameters
	:param url: The target URL to retrieve data from.
	:param timeout: The maximum time in seconds to wait for a response.
	"""

	url: str | None = None
	timeout: int = 30
	clean: bool = True


@dataclass
class WebFetchResponse:
	"""web fetch response parameters
	:param title: page title
	:param content: page content
	"""

	title: str | None = None
	content: str | None = None


async def web_fetch(request: WebFetchRequest, raw: Request) -> WebFetchResponse:
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
			response = WebFetchResponse(title=result["title"], content=result["body"])
			if request.clean:
				markdown = HtmlToMarkdown()
				response.content, info = markdown.toMarkdown(html=response.content, title=response.title, url=request.url)  # transform to markdown
				# markdown.printresult(info) # print info
			logger.info(f'[Main] "{raw.method} {raw.url.path}" - 200 length="original: {len(result["body"])} -> cleaned: {len(response.content)}"')

			# import aiofiles
			# async with aiofiles.open("output.html", "w", encoding="utf-8") as f:
			# 	logger.debug(f"write {len(result['body'])} characters to output.html")
			# 	await f.write(result["body"])
			return response
		else:
			raise HTTPException(status_code=result["status"], detail=result["detail"])

	except HTTPException as e:
		raise e
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"unknow exception {str(type(e))} {str(e)}")
